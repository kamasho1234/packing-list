# -*- coding: utf-8 -*-
"""既存記事の「関連記事」欄に新記事へのリンクを追加する（冪等）"""
import json, os, re

GEN = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:\Users\kamas\projects\webapps\travel-packing-list"
ARTICLES = os.path.join(SITE, "articles")
META = {a["slug"]: a for a in json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))}

# 新記事 -> それを関連記事として載せるべき既存記事
MAP = {
    "korea-packing-list": ["taiwan-packing-list", "overseas-must-have", "first-overseas-trip-prep"],
    "okinawa-packing-list": ["hokkaido-winter-packing", "kids-travel-packing", "packing-list-template"],
    "guam-packing-list": ["hawaii-packing-list", "honeymoon-packing", "kids-travel-packing"],
    "thailand-packing-list": ["dormitory-guide", "europe-backpacking", "overseas-documents"],
    "vietnam-packing-list": ["taiwan-packing-list", "minimal-packing"],
    "singapore-packing-list": ["business-trip-packing", "overseas-business-trip"],
    "america-packing-list": ["hawaii-packing-list", "travel-insurance-guide", "overseas-documents"],
    "suitcase-size-guide": ["carry-on-bag-guide", "packing-light-tips", "lcc-baggage-comparison", "europe-backpacking"],
    "packing-cubes-compression": ["packing-light-tips", "hyakukin-travel-goods", "minimal-packing", "laundry-travel-tips"],
    "mobile-battery-rules": ["travel-gadgets-airtag", "travel-gadgets-2024", "carry-on-liquids-rules", "lcc-baggage-comparison"],
    "esim-guide": ["wifi-sim-comparison", "first-overseas-trip-prep", "overseas-business-trip"],
    "inflight-comfort": ["carry-on-bag-guide", "carry-on-liquids-rules", "europe-backpacking"],
    "medicine-travel": ["overseas-must-have", "women-overseas-packing", "travel-insurance-guide", "forgotten-items-ranking"],
    "money-cashless": ["overseas-documents", "passport-lost-procedures", "first-overseas-trip-prep", "travel-insurance-guide"],
    "domestic-1night": ["business-trip-packing", "packing-list-template", "hotel-vs-hostel-packing"],
    "onsen-trip": ["hokkaido-winter-packing", "packing-list-template"],
    "graduation-trip": ["first-overseas-trip-prep", "dormitory-guide", "women-solo-travel", "europe-backpacking"],
    "senior-travel": ["kids-travel-packing", "honeymoon-packing"],
    "jetlag-tips": ["overseas-business-trip", "europe-backpacking", "hawaii-packing-list"],
    "beach-resort-packing": ["hawaii-packing-list", "women-overseas-packing", "honeymoon-packing", "taiwan-packing-list"],
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
