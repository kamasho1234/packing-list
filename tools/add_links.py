# -*- coding: utf-8 -*-
"""既存記事の「関連記事」欄に新記事へのリンクを追加する（冪等）"""
import json, os, re

GEN = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:\Users\kamas\projects\webapps\travel-packing-list"
ARTICLES = os.path.join(SITE, "articles")
META = {a["slug"]: a for a in json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))}

# 新記事 -> それを関連記事として載せるべき既存記事
MAP = {
    "tokyo-trip": ["domestic-1night", "themepark-packing", "graduation-trip", "business-trip-packing"],
    "osaka-trip": ["kyoto-trip", "domestic-1night", "themepark-packing"],
    "fukuoka-trip": ["domestic-1night", "onsen-trip", "packing-list-template"],
    "nagoya-trip": ["business-trip-packing", "domestic-1night", "overseas-business-trip"],
    "kanazawa-trip": ["kyoto-trip", "onsen-trip", "domestic-1night"],
    "hiroshima-trip": ["domestic-1night", "okinawa-packing-list", "graduation-trip"],
    "tohoku-trip": ["hokkaido-winter-packing", "onsen-trip", "camping-packing"],
    "nagasaki-trip": ["domestic-1night", "packing-light-tips", "kyoto-trip"],
    "hakone-izu": ["onsen-trip", "domestic-1night", "senior-travel"],
    "karuizawa-trip": ["onsen-trip", "camping-packing", "domestic-1night"],
    "shikoku-trip": ["hiking-packing", "domestic-1night", "minimal-packing"],
    "yakushima-trip": ["hiking-packing", "camping-packing", "okinawa-packing-list"],
    "malaysia-packing-list": ["singapore-packing-list", "thailand-packing-list", "vietnam-packing-list"],
    "switzerland-packing-list": ["europe-backpacking", "germany-packing-list", "italy-packing-list"],
    "netherlands-packing-list": ["europe-backpacking", "germany-packing-list", "london-packing-list"],
    "turkey-packing-list": ["europe-backpacking", "dubai-packing-list", "spain-packing-list"],
    "newzealand-packing-list": ["australia-packing-list", "international-license", "jetlag-tips"],
    "losangeles-packing-list": ["america-packing-list", "esta-guide", "hawaii-packing-list"],
    "company-trip": ["onsen-trip", "business-trip-packing", "domestic-1night"],
    "club-camp": ["camping-packing", "school-trip", "laundry-travel-tips"],
    "couple-trip": ["honeymoon-packing", "onsen-trip", "graduation-trip"],
    "joshi-tabi": ["women-solo-travel", "women-overseas-packing", "onsen-trip"],
    "car-trip": ["camping-packing", "kids-travel-packing", "domestic-1night", "hokkaido-winter-packing"],
    "train-trip": ["night-bus", "domestic-1night", "live-tour-packing"],
    "diving-snorkeling": ["beach-resort-packing", "okinawa-packing-list", "ishigaki-miyako", "bali-packing-list"],
    "wedding-guest": ["business-trip-packing", "suitcase-size-guide", "domestic-1night"],
    "early-late-flight": ["airport-procedure", "day-before-departure", "inflight-comfort", "transit-guide"],
    "souvenir-guide": ["customs-duty-free", "animal-plant-quarantine", "duty-free-shopping", "checked-baggage-rules"],
    "rainy-travel": ["laundry-travel-tips", "packing-light-tips", "hyakukin-travel-goods", "kyoto-trip"],
    "contact-glasses": ["medicine-travel", "carry-on-liquids-rules", "inflight-comfort", "overseas-must-have"],
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
