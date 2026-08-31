# -*- coding: utf-8 -*-
"""既存記事の「関連記事」欄に新記事へのリンクを追加する（冪等）"""
import json, os, re

GEN = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:\Users\kamas\projects\webapps\travel-packing-list"
ARTICLES = os.path.join(SITE, "articles")
META = {a["slug"]: a for a in json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))}

# 新記事 -> それを関連記事として載せるべき既存記事
MAP = {
    "paris-packing-list": ["europe-backpacking", "overseas-must-have", "women-overseas-packing"],
    "italy-packing-list": ["europe-backpacking", "packing-light-tips", "overseas-documents"],
    "london-packing-list": ["europe-backpacking", "first-overseas-trip-prep", "travel-gadgets-airtag"],
    "bali-packing-list": ["beach-resort-packing", "thailand-packing-list", "honeymoon-packing"],
    "australia-packing-list": ["hawaii-packing-list", "overseas-documents", "jetlag-tips"],
    "dubai-packing-list": ["overseas-business-trip", "inflight-comfort", "overseas-must-have"],
    "cebu-packing-list": ["beach-resort-packing", "dormitory-guide", "wifi-sim-comparison"],
    "kyoto-trip": ["domestic-1night", "onsen-trip", "packing-list-template"],
    "themepark-packing": ["kids-travel-packing", "domestic-1night", "hyakukin-travel-goods"],
    "live-tour-packing": ["business-trip-packing", "domestic-1night", "packing-list-template"],
    "camping-packing": ["hokkaido-winter-packing", "hyakukin-travel-goods", "okinawa-packing-list"],
    "maternity-travel": ["senior-travel", "medicine-travel", "kids-travel-packing"],
    "long-stay-packing": ["laundry-travel-tips", "minimal-packing", "europe-backpacking", "packing-light-tips"],
    "study-abroad-packing": ["first-overseas-trip-prep", "graduation-trip", "dormitory-guide", "overseas-documents"],
    "customs-duty-free": ["overseas-must-have", "money-cashless", "hawaii-packing-list", "korea-packing-list"],
    "lost-baggage": ["passport-lost-procedures", "travel-insurance-guide", "travel-gadgets-airtag", "lcc-baggage-comparison"],
    "plug-voltage-guide": ["travel-gadgets-airtag", "travel-gadgets-2024", "first-overseas-trip-prep", "korea-packing-list", "america-packing-list"],
    "checked-baggage-rules": ["carry-on-liquids-rules", "mobile-battery-rules", "suitcase-size-guide", "lcc-baggage-comparison", "carry-on-bag-guide"],
    "airport-procedure": ["first-overseas-trip-prep", "day-before-departure", "overseas-documents", "graduation-trip"],
    "travel-security": ["passport-lost-procedures", "women-solo-travel", "money-cashless", "dormitory-guide", "europe-backpacking"],
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# 既存記事ごとに追加する新記事を集約
per_host = {}
for new, hosts in MAP.items():
    for h in hosts:
        per_host.setdefault(h, []).append(new)

total = 0
for host, news in sorted(per_host.items()):
    p = os.path.join(ARTICLES, host + ".html")
    if not os.path.exists(p):
        print("MISSING host:", host); continue
    h = open(p, encoding="utf-8").read()
    m = re.search(r'(<ul class="related-list">)(.*?)(\s*</ul>)', h, re.S)
    if not m:
        print("no related-list:", host); continue
    items = m.group(2)
    add = []
    for n in news:
        if './%s.html' % n in h:
            continue
        add.append('          <li><a href="./%s.html">%s</a></li>' % (n, esc(META[n]["title"])))
    if not add:
        continue
    new_block = m.group(1) + items.rstrip("\n") + "\n" + "\n".join(add) + m.group(3)
    h = h[:m.start()] + new_block + h[m.end():]
    open(p, "w", encoding="utf-8", newline="\n").write(h)
    total += len(add)
    print("%-28s +%d" % (host, len(add)))

print("追加した関連リンク合計:", total)

# 新記事1本あたりの被リンク数
inbound = {n: 0 for n in MAP}
for f in os.listdir(ARTICLES):
    if not f.endswith(".html"):
        continue
    c = open(os.path.join(ARTICLES, f), encoding="utf-8").read()
    for n in inbound:
        if f[:-5] != n and './%s.html' % n in c:
            inbound[n] += 1
print("\n新記事ごとの被リンク数（記事内リンク含む）:")
for k, v in sorted(inbound.items(), key=lambda x: x[1]):
    print("  %-28s %d" % (k, v))
