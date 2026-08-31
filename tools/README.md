# 記事量産ツール

SEO記事をテンプレートから生成し、機械検証するための一式。
2026-08-24（10本）と 2026-08-31（20本）の量産で使用。

## ファイル

| ファイル | 役割 |
|---|---|
| `WRITER_BRIEF.md` | 執筆エージェントに渡す仕様と禁止事項。**最初にこれを更新する** |
| `FACTS.md` | 一次資料で検証済みの規制情報。**ここに無い法令・手数料・数値は記事に書かせない** |
| `style.html` | 全記事共通のCSS（既存記事から抽出したもの。触らない） |
| `meta.json` | 記事メタ（slug / title / tag / date / related）。量産のたびに書き換える |
| `build.py` | `meta.json` + `body_<slug>.html` + `faq_<slug>.json` → `articles/<slug>.html` |
| `update_site.py` | `index.html` の記事一覧カードと `sitemap.xml` に新記事を追加（冪等） |
| `add_links.py` | 既存記事の関連記事欄に新記事へのリンクを追加（冪等）。MAP を書き換えて使う |
| `verify.py` | 機械検証。字数 / 絵文字 / リンク切れ / 自己リンク / タグ整合 / 未許可class / インラインstyle / 外部リンクのnoopener / JSON-LD / description の長さ |

## 手順

1. `FACTS.md` を更新する（規制系のテーマがあれば一次資料を当たって書き足す）
2. `meta.json` に新記事のエントリを書く
3. 執筆エージェントに `WRITER_BRIEF.md` / `FACTS.md` / リンク先一覧を読ませ、
   作業ディレクトリに `body_<slug>.html` と `faq_<slug>.json` を作らせる
4. `python verify.py` — **エラー0になるまでエージェントに差し戻す**
5. `python build.py` → `python update_site.py` → `python add_links.py`
6. `python verify.py` で再検査 → commit / push
7. 本番URLに curl して全記事の 200 を確認する

## 注意

- **エージェントの自己申告（文字数・修正済みの報告）は信用しない。** 必ず `verify.py` で再計測する
- 実行時は `PYTHONIOENCODING=utf-8` を付ける（Windowsのコンソールで日本語が化けるため）
- スクリプトは `body_*.html` / `faq_*.json` と同じディレクトリに置いて実行する
