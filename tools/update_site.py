# -*- coding: utf-8 -*-
"""index.html の記事一覧と sitemap.xml に新規20本を追加する（冪等）"""
import json, os, re

GEN = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:\Users\kamas\projects\webapps\travel-packing-list"
BASE = "https://packing-list.net"
META = json.load(open(os.path.join(GEN, "meta.json"), encoding="utf-8"))
DATE = "2026-08-31"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---- index.html ----
idx_path = os.path.join(SITE, "index.html")
idx = open(idx_path, encoding="utf-8").read()
cards = []
added = []
for a in META:
    href = "articles/%s.html" % a["slug"]
    if href in idx:
        continue
    cards.append(
        '      <a class="article-card" href="%s">\n'
        '        <span class="article-card-tag">%s</span>\n'
        '        <p class="article-card-title">%s</p>\n'
        '      </a>' % (href, esc(a["tag"]), esc(a["title"])))
    added.append(a["slug"])

if cards:
    marker = "    </div>\n  </section>\n\n  <footer class=\"app-footer\">"
    assert marker in idx, "index.html の記事グリッド末尾が見つからない"
    idx = idx.replace(marker, "\n".join(cards) + "\n" + marker, 1)
    open(idx_path, "w", encoding="utf-8", newline="\n").write(idx)
print("index.html: added %d cards" % len(added))

# ---- sitemap.xml ----
sm_path = os.path.join(SITE, "sitemap.xml")
sm = open(sm_path, encoding="utf-8").read()
entries = []
for a in META:
    loc = "%s/articles/%s.html" % (BASE, a["slug"])
    if loc in sm:
        continue
    entries.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                   "    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>\n  </url>"
                   % (loc, DATE))
if entries:
    sm = sm.replace("</urlset>", "\n".join(entries) + "\n</urlset>", 1)
    open(sm_path, "w", encoding="utf-8", newline="\n").write(sm)
print("sitemap.xml: added %d urls" % len(entries))

# トップページの lastmod を更新
sm = open(sm_path, encoding="utf-8").read()
sm = re.sub(r"(<loc>https://packing-list\.net/</loc>\s*\n\s*<lastmod>)[0-9-]+(</lastmod>)",
            r"\g<1>%s\g<2>" % DATE, sm, count=1)
open(sm_path, "w", encoding="utf-8", newline="\n").write(sm)
print("sitemap.xml: top lastmod ->", DATE)
