# -*- coding: utf-8 -*-
"""記事HTML生成: meta.json + body_<slug>.html -> articles/<slug>.html"""
import json, os, re, urllib.parse, sys

GEN = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:\Users\kamas\projects\webapps\travel-packing-list"
ARTICLES = os.path.join(SITE, "articles")
BASE = "https://packing-list.net"

STYLE = open(os.path.join(GEN, "style.html"), encoding="utf-8").read()
META = json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))

# faq_<slug>.json（執筆エージェント作成）から description / faq / cta を取り込む
for _a in META:
    _f = os.path.join(GEN, "faq_%s.json" % _a["slug"])
    if os.path.exists(_f):
        _d = json.load(open(_f, encoding="utf-8"))
        _a.setdefault("description", _d.get("description", ""))
        _a.setdefault("faq", _d.get("faq", []))
        _a.setdefault("cta_title", _d.get("cta_title", "持ち物リストを自動で作る"))
        _a.setdefault("cta_text", _d.get("cta_text", "行き先と泊数を入れるだけで、過不足のない持ち物リストが出来上がります。"))

FONTS = ('  <link href="https://fonts.googleapis.com/css2?'
         'family=Cormorant+Garamond:wght@400;600;700&'
         'family=Noto+Sans+JP:wght@400;600;700&display=swap" rel="stylesheet">\n')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def jstr(s):
    return json.dumps(s, ensure_ascii=False)


def build(a):
    slug, title, desc = a["slug"], a["title"], a["description"]
    date = a.get("date", "2026-08-31")
    ymd = "%s年%d月%d日" % (date[:4], int(date[5:7]), int(date[8:10]))
    url = "%s/articles/%s.html" % (BASE, slug)
    img = BASE + "/og-image.png"
    body = open(os.path.join(GEN, "body_%s.html" % slug), encoding="utf-8").read().rstrip() + "\n"

    faq = ",\n      ".join(
        '{"@type": "Question", "name": %s, "acceptedAnswer": {"@type": "Answer", "text": %s}}'
        % (jstr(q["q"]), jstr(q["a"])) for q in a["faq"])

    rel = "\n".join(
        '          <li><a href="./%s.html">%s</a></li>' % (r[0], esc(r[1])) for r in a["related"])

    share_t = urllib.parse.quote(title, safe="")
    share_u = urllib.parse.quote(url, safe="")

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="canonical" href="{url}">

  <!-- Favicon -->
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">

  <!-- OGP -->
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{img}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="旅行持ち物リストメーカー">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{img}">

  <!-- JSON-LD Article Schema -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": {jstr(title)},
    "description": {jstr(desc)},
    "url": "{url}",
    "image": "{img}",
    "datePublished": "{date}T00:00:00Z",
    "dateModified": "{date}T00:00:00Z",
    "author": {{
      "@type": "Organization",
      "name": "旅行持ち物リストメーカー"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "旅行持ち物リストメーカー",
      "url": "{BASE}/"
    }},
    "mainEntityOfPage": {{
      "@type": "WebPage",
      "@id": "{url}"
    }}
  }}
  </script>

  <!-- JSON-LD BreadcrumbList -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{"@type": "ListItem", "position": 1, "name": "ホーム", "item": "{BASE}/"}},
      {{"@type": "ListItem", "position": 2, "name": {jstr(title)}, "item": "{url}"}}
    ]
  }}
  </script>

  <!-- JSON-LD FAQPage -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {faq}
    ]
  }}
  </script>

{FONTS}
{STYLE}</head>
<body>
  <header>
    <div class="container">
      <div class="header-content">
        <a href="../" class="site-title">旅行持ち物リストメーカー</a>
        <a href="../" class="home-link">ホーム</a>
      </div>
    </div>
  </header>

  <main class="container">
    <article>
      <h1>{esc(title)}</h1>

      <div class="article-meta">
        <time datetime="{date}">{ymd}</time> | 更新日: <time datetime="{date}">{ymd}</time>
      </div>

{body}
      <div class="cta-banner">
        <h3>{esc(a["cta_title"])}</h3>
        <p>{esc(a["cta_text"])}</p>
        <a href="../" class="cta-btn">旅行持ち物リストを無料で作る</a>
      </div>

      <div class="share-section">
        <p class="share-label">この記事をシェアする</p>
        <div class="share-buttons">
          <a href="https://twitter.com/intent/tweet?text={share_t}&url={share_u}" target="_blank" rel="noopener" class="share-btn share-x">X（Twitter）</a>
          <a href="https://social-plugins.line.me/lineit/share?url={share_u}" target="_blank" rel="noopener" class="share-btn share-line">LINE</a>
          <a href="https://www.facebook.com/sharer/sharer.php?u={share_u}" target="_blank" rel="noopener" class="share-btn share-fb">Facebook</a>
        </div>
      </div>

      <div class="related-articles">
        <h3>関連記事</h3>
        <ul class="related-list">
{rel}
        </ul>
      </div>
    </article>
  </main>

  <footer>
    <div class="container">
      <p>&copy; 2024-2026 packing-list.net All rights reserved.</p>
    </div>
  </footer>
</body>
</html>
"""


if __name__ == "__main__":
    only = sys.argv[1:] or None
    n = 0
    for a in META:
        if only and a["slug"] not in only:
            continue
        if not os.path.exists(os.path.join(GEN, "body_%s.html" % a["slug"])):
            print("SKIP (no body):", a["slug"]); continue
        out = os.path.join(ARTICLES, a["slug"] + ".html")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(a))
        n += 1
        print("OK", a["slug"], os.path.getsize(out), "bytes")
    print("built", n)
