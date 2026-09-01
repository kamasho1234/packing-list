# -*- coding: utf-8 -*-
"""verify.py を補う独自スキャン。
第3弾の教訓（自己申告は信用しない）を受けて、FACTS.md に無い数値と、
第4弾で禁止した「店名・施設名・料金・所要時間」を全記事から拾う。
"""
import io, json, os, re, glob, sys

GEN = os.path.dirname(os.path.abspath(__file__))
facts = io.open(os.path.join(GEN, "FACTS.md"), encoding="utf-8").read()
facts_nums = set(re.findall(r"[0-9][0-9,\.]*", facts))
meta = json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))
slugs = [a["slug"] for a in meta]
# 差別化の軸が本文に現れているかを見るためのキーワード（国内12本）
AXIS = {
    "tokyo-trip": ["乗り換え", "歩"], "osaka-trip": ["食べ歩き"], "fukuoka-trip": ["屋台"],
    "nagoya-trip": ["乗り継ぎ", "拠点"], "kanazawa-trip": ["雨"], "hiroshima-trip": ["船", "フェリー"],
    "tohoku-trip": ["移動"], "nagasaki-trip": ["坂"], "hakone-izu": ["乗り"],
    "karuizawa-trip": ["自転車"], "shikoku-trip": ["車"], "yakushima-trip": ["雨"],
}

HARD = [  # 見つかったら必ず直す
    (r"[0-9]+\s*℃", "摂氏の数値"),
    (r"SPF\s*[0-9]", "SPFの数値"),
    (r"徒歩\s*[0-9]+\s*分", "徒歩◯分"),
    (r"[0-9]+\s*分\s*(?:程度|ほど|かかり|要し)", "所要時間の断定"),
    (r"(Visa|Mastercard|JCB|AMEX|Anker|iPhone|Android|Amazon|楽天|無印良品|ユニクロ)", "ブランド名"),
]
SOFT = [  # 文脈しだい。FACTS 由来なら可
    (r"[0-9][0-9,]*\s*円", "金額(円)"),
    (r"[0-9][0-9,\.]*\s*(?:ドル|ユーロ|ポンド)", "外貨"),
    (r"[0-9]+\s*%", "割合"),
    (r"[0-9]+\s*(?:Wh|kg|ml|IU|オンス)", "単位つき数値"),
]

hard_hits, soft_hits, axis_ng, struct_ng = [], [], [], []
for s in slugs:
    p = os.path.join(GEN, "body_%s.html" % s)
    if not os.path.exists(p):
        struct_ng.append((s, "body が無い")); continue
    raw = io.open(p, encoding="utf-8").read()
    t = re.sub(r"<[^>]+>", "", raw)

    for rx, lab in HARD:
        for m in re.finditer(rx, t):
            hard_hits.append((s, lab, t[max(0, m.start()-25):m.end()+15].replace("\n", "")))
    for rx, lab in SOFT:
        for m in re.finditer(rx, t):
            num = re.search(r"[0-9][0-9,\.]*", m.group(0)).group(0)
            if num in facts_nums:
                continue
            soft_hits.append((s, lab, t[max(0, m.start()-25):m.end()+15].replace("\n", "")))

    # 構造: 最後の h2 が「よくある質問」か / comparison-table が table か
    h2 = re.findall(r"<h2>([^<]+)</h2>", raw)
    if not h2 or h2[-1] != "よくある質問":
        struct_ng.append((s, "最後のh2が『よくある質問』でない: %s" % (h2[-1] if h2 else "h2なし")))
    if '<div class="comparison-table"' in raw:
        struct_ng.append((s, "comparison-table が div で書かれている"))
    links = re.findall(r'href="\./([a-z0-9\-]+)\.html"', raw)
    if not (5 <= len(links) <= 8):
        struct_ng.append((s, "内部リンク %d 本（5〜8本にする）" % len(links)))

    if s in AXIS and not any(k in t for k in AXIS[s]):
        axis_ng.append((s, "差別化の軸のキーワードが本文に無い: %s" % AXIS[s]))

def dump(title, rows, limit=40):
    print("\n== %s: %d 件 ==" % (title, len(rows)))
    for r in rows[:limit]:
        print("   ", " | ".join(str(x) for x in r))

dump("構造の問題（必ず直す）", struct_ng)
dump("禁止パターン（必ず直す）", hard_hits)
dump("FACTS.md に無い数値（要確認）", soft_hits)
dump("差別化の軸が見当たらない", axis_ng)
print("\n合計: 構造 %d / 禁止 %d / 要確認 %d / 軸 %d" %
      (len(struct_ng), len(hard_hits), len(soft_hits), len(axis_ng)))
sys.exit(1 if (struct_ng or hard_hits) else 0)
