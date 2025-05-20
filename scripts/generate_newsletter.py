#!/usr/bin/env python3
"""
日本語の editor_note.txt を元に英語と日本語のメール HTML を生成する。
出力ファイルは email.html。
"""
import datetime, feedparser, pathlib, html, os
from openai import OpenAI

# ---- 設定 ----
DATE = datetime.date.today().isoformat()
LANGS = [
    ("ja", "Japanese", "🇯🇵"),
    ("en", "English", "🇺🇸"),
]

RSS = {
    "ja": {
        "Studyriver": "https://studyriver.jp/feed",
        "Studyriver Kids": "https://studyriver.jp/kids/feed",
        "SassaMahha": "https://sassamahha.me/feed",
    },
    "en": {
        "Studyriver": "https://studyriver.jp/en/feed",
        "Studyriver Kids": "https://studyriver.jp/kids/en/feed",
    },
}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def t(text_ja, lang):
    if lang == "ja":
        return text_ja
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Translate into {lang} preserving line breaks."},
            {"role": "user", "content": text_ja}
        ]
    )
    return rsp.choices[0].message.content.strip()

def rss_html(url, limit=3):
    f = feedparser.parse(url)
    items = f.entries[:limit]
    return "\n".join(
        f'<li><a href="{html.escape(e.link)}">{html.escape(e.title)}</a></li>'
        for e in items
    ) or "<li><em>No updates.</em></li>"

note_ja = pathlib.Path("blocks/editor_note.txt").read_text().strip()
notes = {lg: t(note_ja, lg) for lg, _, _ in LANGS}

road_html = {
    lg: pathlib.Path(f"blocks/road_to_2112_{lg}.html").read_text()
    for lg, _, _ in LANGS
}

# ---- HTML生成 ----
parts = [f"""<!DOCTYPE html>
<html lang="ja"><meta charset="utf-8">
<title>週刊 Road to 2112</title>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;line-height:1.6;background-color:#B6B09F;max-width:680px;margin:auto">
<div style="background:#F2F2F2; padding:30px; border-radius:8px;">
<h1>週刊 Road to 2112 🌐</h1>
<p><small>{DATE}</small></p>
<hr>"""]

for lg, name, flag in LANGS:
    parts.append(f"<h2>{flag} {name}</h2>")
    parts.append("<h3>今週のアイスブレイク</h3>")
    parts.append("<p>" + notes[lg].replace("\n", "<br>") + "</p>")
    parts.append("<h3>最新記事 (RSS)</h3>")
    for site, url in RSS[lg].items():
        parts.append(f"<h4>{site}</h4><ul>{rss_html(url)}</ul>")
    parts.append("<h3>📘 Road to 2112</h3>")
    parts.append(road_html[lg])
    parts.append("<hr>")

parts.append("</div></body></html>")

out = pathlib.Path("email.html")
out.write_text("\n".join(parts), encoding="utf-8")
print("✅ wrote", out)
