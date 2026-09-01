# -*- coding: utf-8 -*-
"""既存記事の「関連記事」欄に新記事へのリンクを追加する（冪等）"""
import json, os, re

GEN = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:\Users\kamas\projects\webapps\travel-packing-list"
ARTICLES = os.path.join(SITE, "articles")
META = {a["slug"]: a for a in json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))}

# 新記事 -> それを関連記事として載せるべき既存記事
MAP = {
    "packing-order": ["day-before-departure", "packing-list-template", "first-overseas-trip-prep", "forgotten-items-ranking"],
    "backpack-vs-suitcase": ["suitcase-size-guide", "carry-on-bag-guide", "europe-backpacking", "packing-light-tips"],
    "clothes-folding": ["packing-cubes-compression", "packing-light-tips", "business-trip-packing"],
    "shoes-choice": ["tokyo-trip", "nagasaki-trip", "kyoto-trip", "europe-backpacking"],
    "outfit-planning": ["minimal-packing", "laundry-travel-tips", "long-stay-packing", "joshi-tabi"],
    "cosmetics-travel": ["carry-on-liquids-rules", "women-overseas-packing", "joshi-tabi"],
    "hair-care-travel": ["plug-voltage-guide", "hotel-vs-hostel-packing", "onsen-trip"],
    "period-travel": ["women-solo-travel", "women-overseas-packing", "medicine-travel"],
    "baggage-weight": ["lcc-baggage-comparison", "checked-baggage-rules", "suitcase-size-guide", "souvenir-guide"],
    "insect-bites": ["camping-packing", "beach-resort-packing", "hiking-packing", "thailand-packing-list"],
    "altitude-sickness": ["hiking-packing", "switzerland-packing-list", "medicine-travel"],
    "food-safety-travel": ["medicine-travel", "allergy-travel", "vietnam-packing-list", "travel-vaccination"],
    "dry-air-travel": ["inflight-comfort", "contact-glasses", "jetlag-tips", "medicine-travel"],
    "travel-fatigue": ["jetlag-tips", "senior-travel", "inflight-comfort", "night-bus"],
    "beppu-yufuin": ["onsen-trip", "fukuoka-trip", "domestic-1night"],
    "kumamoto-aso": ["car-trip", "fukuoka-trip", "camping-packing"],
    "kagoshima-trip": ["yakushima-trip", "okinawa-packing-list", "domestic-1night"],
    "ise-shima": ["nagoya-trip", "kyoto-trip", "domestic-1night"],
    "nara-trip": ["kyoto-trip", "osaka-trip", "graduation-trip"],
    "takayama-trip": ["kanazawa-trip", "hokkaido-winter-packing", "onsen-trip"],
    "philippines-packing-list": ["cebu-packing-list", "beach-resort-packing", "thailand-packing-list"],
    "india-packing-list": ["travel-vaccination", "overseas-documents", "europe-backpacking"],
    "northern-europe-packing": ["europe-backpacking", "netherlands-packing-list", "germany-packing-list"],
    "czech-packing-list": ["europe-backpacking", "germany-packing-list", "italy-packing-list"],
    "egypt-packing-list": ["turkey-packing-list", "dubai-packing-list", "australia-packing-list"],
    "solo-domestic": ["women-solo-travel", "domestic-1night", "minimal-packing", "train-trip"],
    "three-generation-trip": ["senior-travel", "kids-travel-packing", "onsen-trip", "maternity-travel"],
    "car-camping": ["car-trip", "camping-packing", "tohoku-trip"],
    "cycling-trip": ["karuizawa-trip", "camping-packing", "rainy-travel"],
    "marathon-trip": ["live-tour-packing", "domestic-1night", "business-trip-packing"],
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
