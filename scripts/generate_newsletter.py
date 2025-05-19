#!/usr/bin/env python3
""" editor_note.txt（ja）を 3 言語に翻訳し RSS を 3 件ずつ取得して HTML 合成、
    newsletters/latest.html を吐く。
"""
import datetime, feedparser, pathlib, html, os
from openai import OpenAI  # ✅ 新バージョン対応

# ────────────────
# 設定
DATE = datetime.date.today().isoformat()
LANGS = [("ja", "🇯🇵 Japanese"),
         ("en", "🇺🇸 English"),
         ("es", "🇪🇸 Spanish")]

RSS = {
    "ja": {
        "Studyriver":      "https://studyriver.jp/feed",
        "Studyriver Kids": "https://studyriver.jp/kids/feed",
        "SassaMahha":      "https://sassamahha.me/feed",
    },
    "en": {
        "Studyriver":      "https://studyriver.jp/en/feed",
        "Studyriver Kids": "https://studyriver.jp/kids/en/feed",
    },
    "es": {
        "Studyriver":      "https://studyriver.jp/es/feed",
        "Studyriver Kids": "https://studyriver.jp/kids/es/feed",
    },
}

# ────────────────
# OpenAI API Client 初期化（v1.0対応）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def t(text_ja, lang):
    if lang == "ja":
        return text_ja
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Translate into {dict(LANGS)[lang]} preserving line breaks."},
            {"role": "user", "content": text_ja}
        ],
        max_tokens=800
    )
    return rsp.choices[0].message.content.strip()

def rss_html(url, limit=3):
    f = feedparser.parse(url)
    items = f.entries[:limit]
    return "\n".join(
        f'<li><a href="{html.escape(e.link)}">{html.escape(e.title)}</a></li>'
        for e in items
    ) or "<li><em>No updates.</em></li>"

# ────────────────
# 1. エディターノートの読み込みと翻訳
note_ja = pathlib.Path("blocks/editor_note.txt").read_text().strip()
notes = {lg: t(note_ja, lg) for lg, _ in LANGS}

# 2. 各言語の Road to 2112 HTML 読み込み
road_html = {
    lg: pathlib.Path(f"blocks/road_to_2112_{lg}.html").read_text()
    for lg, _ in LANGS
}

# 3. HTML構築
parts = [f"""<!DOCTYPE html>
<html lang="ja"><meta charset="utf-8">
<title>週刊 Road to 2112</title>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;line-height:1.6;max-width:680px;margin:auto">
<h1>週刊 Road to 2112 🌐</h1>
<p><small>{DATE}</small></p>
<nav>
<strong>▼各言語へジャンプ</strong><br>
""" + " | ".join(
    f'<a href="#{lg}">{flag}</a>'
    for lg, flag in LANGS
) + "</nav><hr>"
]

for lg, label in LANGS:
    flag, name = label.split(" ", 1)
    parts.append(f'<h2 id="{lg}">{flag} {name}</h2>')

    # アイスブレイク
    parts.append("<h3>今週のアイスブレイク</h3>")
    parts.append("<p>" + notes[lg].replace("\n", "<br>") + "</p>")

    # RSS
    parts.append("<h3>最新記事 (RSS)</h3>")
    for site, url in RSS[lg].items():
        parts.append(f"<h4>{site}</h4><ul>{rss_html(url)}</ul>")

    # Road to 2112 紹介
    parts.append(road_html[lg])
    parts.append("<hr>")

parts.append("</body></html>")

# 保存
out = pathlib.Path("newsletters/latest.html")
out.write_text("\n".join(parts), encoding="utf-8")
print("✅ wrote", out)
