# -*- coding: utf-8 -*-
"""生成物の機械検証: 文字数 / 絵文字 / リンク切れ / JSON-LD / 見出し / 文字化け"""
import json, os, re, sys, glob

GEN = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:\Users\kamas\projects\webapps\travel-packing-list"
ARTICLES = os.path.join(SITE, "articles")
META = json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))
NEW = [a["slug"] for a in META]

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\u2B00-\u2BFF\uFE0F\u203C\u2049\u2705\u274C]")

errors, warns = [], []


def text_len(html):
    t = re.sub(r"<[^>]+>", "", html)
    t = re.sub(r"\s+", "", t)
    return len(t)


# 全記事のslug（既存+新規）
all_slugs = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ARTICLES, "*.html"))}
all_slugs |= set(NEW)

# ---- 本文フラグメントの検査 ----
for a in META:
    slug = a["slug"]
    bp = os.path.join(GEN, "body_%s.html" % slug)
    fp = os.path.join(GEN, "faq_%s.json" % slug)
    if not os.path.exists(bp):
        errors.append("%s: body ファイルが無い" % slug); continue
    body = open(bp, encoding="utf-8").read()

    n = text_len(body)
    if n < 7000:
        errors.append("%s: 本文 %d 字（7,000字未満）" % (slug, n))
    elif n > 12000:
        warns.append("%s: 本文 %d 字（長め）" % (slug, n))

    if EMOJI.search(body):
        errors.append("%s: 絵文字を検出 %r" % (slug, EMOJI.findall(body)[:5]))
    if "\ufffd" in body:
        errors.append("%s: 文字化け(U+FFFD)を検出" % slug)
    if "<h1" in body:
        errors.append("%s: body に h1 が含まれる" % slug)
    for bad in ("cta-banner", "share-section", "related-articles"):
        if bad in body:
            errors.append("%s: body に %s が含まれる（ビルド側で付与する）" % (slug, bad))
    if 'class="intro"' not in body:
        errors.append("%s: 導入文 <p class=\"intro\"> が無い" % slug)
    if "<h2>よくある質問</h2>" not in body:
        errors.append("%s: 「よくある質問」の h2 が無い" % slug)

    # 内部リンク
    links = re.findall(r'href="\./([a-z0-9\-]+)\.html"', body)
    for l in links:
        if l not in all_slugs:
            errors.append("%s: 存在しないリンク先 ./%s.html" % (slug, l))
        if l == slug:
            errors.append("%s: 自分自身へのリンク" % slug)
    if len(links) < 4:
        warns.append("%s: 内部リンク %d 本（少ない）" % (slug, len(links)))
    dup = {x for x in links if links.count(x) > 1}
    if dup:
        warns.append("%s: 同じリンク先が重複 %s" % (slug, sorted(dup)))

    # 許可されていない class / style
    for c in set(re.findall(r'class="([^"]+)"', body)):
        for one in c.split():
            if one not in ("intro", "highlight-box", "checklist", "comparison-table", "highlight"):
                errors.append("%s: 未許可の class=%s" % (slug, one))
    # タグの開閉整合
    for tag in ("p","h2","h3","ul","li","table","thead","tbody","tr","td","th","div","a","strong","em"):
        o = len(re.findall(r"<%s[ >]" % tag, body)); c = len(re.findall(r"</%s>" % tag, body))
        if o != c:
            errors.append("%s: <%s> %d 個 / </%s> %d 個で不整合" % (slug, tag, tag, c) if False
                          else "%s: <%s> が %d 個、</%s> が %d 個で不整合" % (slug, tag, o, tag, c))
    # 誤ったクラス適用
    if 'class="comparison-table"' in body and not re.search(r'<table class="comparison-table">', body):
        errors.append("%s: comparison-table が table 以外の要素に付いている" % slug)
    if re.search(r'<div class="comparison-table"', body):
        errors.append("%s: <div class=\"comparison-table\"> は不正（<table> にする）" % slug)

    if "style=" in body:
        errors.append("%s: インラインstyleが使われている" % slug)

    # 外部リンク
    for u in re.findall(r'href="(https?://[^"]+)"', body):
        if not re.match(r"https://(www\.)?(mlit|mhlw|customs|ncd\.mhlw|mofa|npa|maff|forth)\.go\.jp|https://tdac\.immigration\.go\.th|https://www\.ica\.gov\.sg|https://www\.hsa\.gov\.sg|https://overseas\.mofa\.go\.kr|https://www\.vn\.emb-japan\.go\.jp|https://www\.anzen\.mofa\.go\.jp|https://www\.ezairyu\.mofa\.go\.jp|https://esta\.cbp\.dhs\.gov|https://www\.cbp\.gov|https://www\.federalregister\.gov|https://home-affairs\.ec\.europa\.eu", u):
            warns.append("%s: 想定外の外部リンク %s" % (slug, u))
    for m in re.finditer(r'<a href="https?://[^"]+"([^>]*)>', body):
        if 'rel="noopener"' not in m.group(1):
            errors.append("%s: 外部リンクに rel=\"noopener\" が無い" % slug)

    # faq json
    if not os.path.exists(fp):
        errors.append("%s: faq json が無い" % slug); continue
    try:
        d = json.load(open(fp, encoding="utf-8"))
    except Exception as e:
        errors.append("%s: faq json がパースできない: %s" % (slug, e)); continue
    for k in ("description", "faq", "cta_title", "cta_text"):
        if not d.get(k):
            errors.append("%s: faq json に %s が無い" % (slug, k))
    if isinstance(d.get("faq"), list) and len(d["faq"]) < 2:
        errors.append("%s: faq が2件未満" % slug)
    dl = len(d.get("description", ""))
    if not (70 <= dl <= 140):
        warns.append("%s: description %d 字（推奨90〜120）" % (slug, dl))
    if EMOJI.search(json.dumps(d, ensure_ascii=False)):
        errors.append("%s: faq json に絵文字" % slug)

# ---- 生成済みHTMLの検査 ----
built = 0
for a in META:
    p = os.path.join(ARTICLES, a["slug"] + ".html")
    if not os.path.exists(p):
        continue
    built += 1
    h = open(p, encoding="utf-8").read()
    for m in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', h, re.S):
        try:
            json.loads(m.group(1))
        except Exception as e:
            errors.append("%s: JSON-LD パースエラー: %s" % (a["slug"], e))
    if h.count("<h1>") != 1:
        errors.append("%s: h1 が1個でない" % a["slug"])
    if "\ufffd" in h:
        errors.append("%s: 生成HTMLに文字化け" % a["slug"])

# ---- 危険な数値・ブランド名のスキャン（body と faq の両方） ----
RISKY = [
    (re.compile(r"[0-9０-９]+\s*(℃|度[CＣ]?(?![数目])）?)"), "気温らしき数値"),
    (re.compile(r"SPF\s*[0-9]"), "SPFの数値"),
    (re.compile(r"[0-9０-９][0-9０-９,，]*\s*(ドル|ユーロ|ポンド|ウォン|バーツ|ペソ|ルピア|ディルハム)"), "外貨の金額"),
    (re.compile(r"(Anker|サムソナイト|リモワ|RIMOWA|無印良品|ユニクロ|iPhone|Android|Apple\s*Pay|Google\s*Pay|VISA|Mastercard|MasterCard|JCB|AMEX|シャネル|プラダ|ビックカメラ|ヤマダ電機|Amazon|楽天)"), "ブランド名"),
]
for a in META:
    for f in ("body_%s.html" % a["slug"], "faq_%s.json" % a["slug"]):
        fp = os.path.join(GEN, f)
        if not os.path.exists(fp):
            continue
        c = open(fp, encoding="utf-8").read()
        for rx, label in RISKY:
            for m in rx.finditer(c):
                warns.append("%s: %s %r" % (f, label, re.sub(r"\s+", "", c[max(0, m.start()-24):m.end()+12])))

print("=" * 60)
print("検証対象: body %d / 生成HTML %d" % (len(META), built))
print("ERROR: %d 件" % len(errors))
for e in errors:
    print("  [E]", e)
print("WARN : %d 件" % len(warns))
for w in warns:
    print("  [W]", w)
print("=" * 60)
sys.exit(1 if errors else 0)
