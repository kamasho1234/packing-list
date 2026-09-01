# -*- coding: utf-8 -*-
"""既存記事の「関連記事」欄に新記事へのリンクを追加する（冪等）"""
import json, os, re

GEN = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:\Users\kamas\projects\webapps\travel-packing-list"
ARTICLES = os.path.join(SITE, "articles")
META = {a["slug"]: a for a in json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))}

# 新記事 -> それを関連記事として載せるべき既存記事
MAP = {
    "passport-application": ["overseas-documents", "first-overseas-trip-prep", "airport-procedure", "day-before-departure"],
    "esta-guide": ["america-packing-list", "hawaii-packing-list", "guam-packing-list", "overseas-documents"],
    "visa-guide": ["overseas-documents", "first-overseas-trip-prep", "europe-backpacking"],
    "international-license": ["australia-packing-list", "america-packing-list", "okinawa-packing-list"],
    "animal-plant-quarantine": ["customs-duty-free", "checked-baggage-rules", "korea-packing-list", "taiwan-packing-list"],
    "pet-travel": ["long-stay-packing", "senior-travel", "domestic-1night"],
    "travel-vaccination": ["medicine-travel", "travel-insurance-guide", "first-overseas-trip-prep"],
    "transit-guide": ["airport-procedure", "inflight-comfort", "lost-baggage", "europe-backpacking"],
    "immigration-card": ["overseas-documents", "korea-packing-list", "thailand-packing-list", "singapore-packing-list"],
    "tax-refund": ["customs-duty-free", "money-cashless", "italy-packing-list", "paris-packing-list"],
    "duty-free-shopping": ["customs-duty-free", "carry-on-liquids-rules", "airport-procedure"],
    "barrier-free-travel": ["senior-travel", "maternity-travel", "medicine-travel"],
    "allergy-travel": ["kids-travel-packing", "medicine-travel", "inflight-comfort"],
    "medical-device-travel": ["medicine-travel", "mobile-battery-rules", "carry-on-liquids-rules", "senior-travel"],
    "emergency-contact": ["passport-lost-procedures", "travel-insurance-guide", "travel-security", "lost-baggage"],
    "china-packing-list": ["korea-packing-list", "taiwan-packing-list", "esim-guide"],
    "hongkong-packing-list": ["taiwan-packing-list", "singapore-packing-list", "thailand-packing-list"],
    "germany-packing-list": ["europe-backpacking", "paris-packing-list", "italy-packing-list", "plug-voltage-guide"],
    "spain-packing-list": ["italy-packing-list", "paris-packing-list", "europe-backpacking", "travel-security"],
    "canada-packing-list": ["america-packing-list", "hokkaido-winter-packing", "australia-packing-list"],
    "newyork-packing-list": ["america-packing-list", "hawaii-packing-list", "business-trip-packing"],
    "ishigaki-miyako": ["okinawa-packing-list", "beach-resort-packing", "domestic-1night"],
    "school-trip": ["kids-travel-packing", "graduation-trip", "domestic-1night", "kyoto-trip"],
    "ski-snowboard": ["hokkaido-winter-packing", "onsen-trip", "camping-packing", "domestic-1night"],
    "hiking-packing": ["camping-packing", "minimal-packing", "packing-light-tips"],
    "night-bus": ["domestic-1night", "live-tour-packing", "graduation-trip"],
    "workation": ["business-trip-packing", "long-stay-packing", "travel-gadgets-airtag", "overseas-business-trip"],
    "kisei-packing": ["domestic-1night", "kids-travel-packing", "hyakukin-travel-goods"],
    "golf-trip": ["checked-baggage-rules", "suitcase-size-guide", "domestic-1night"],
    "cruise-packing": ["beach-resort-packing", "senior-travel", "inflight-comfort", "honeymoon-packing"],
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
