import datetime, pathlib, feedparser, os
from openai import OpenAI

DATE = datetime.date.today().isoformat()
LANGS = {"ja": "Japanese", "en": "English", "es": "Spanish"}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 改行→<br>でHTML用に整形
def load_note_html(path: str):
    raw = pathlib.Path(path).read_text().strip()
    return raw.replace("\n", "<br>")

# 翻訳関数
def translate(text, lang):
    if lang == "ja":
        return text
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Translate into {LANGS[lang]}."},
            {"role": "user", "content": text}
        ],
        max_tokens=800
    )
    return rsp.choices[0].message.content.strip()

# 今週のアイスブレイク（翻訳あり）
note_ja = load_note_html("blocks/editor_note.md")
note = {lg: translate(note_ja, lg) for lg in LANGS}

# RSSユーティリティ
def rss_block(url, max_items=3):
    feed = feedparser.parse(url)
    lines = [f'<a href="{e.link}">{e.title}</a>' for e in feed.entries[:max_items]]
    return "<br>".join(lines) if lines else "_No updates._"

RSS_MAP = {
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

# Road to 2112 紹介文
intro_ja_path = pathlib.Path("blocks/road_to_2112.md")
intro_ja = intro_ja_path.read_text().strip() if intro_ja_path.exists() else "（紹介文が見つかりませんでした）"
intro = {lg: translate(intro_ja, lg).replace("\n", "<br>") for lg in LANGS}

# HTML組立
parts = [
    "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>",
    f"<h1>週刊 Road to 2112 🌐</h1>",
    "<hr>",
    "<p>▼各言語へジャンプ</p>",
    '<p><a href="#ja">🇯🇵 JP</a> ｜ <a href="#en">🇺🇸 EN</a> ｜ <a href="#es">🇪🇸 ES</a></p>',
    "<hr>"
]

for lg, flag in (("ja", "🇯🇵"), ("en", "🇺🇸"), ("es", "🇪🇸")):
    parts.append(f'<a id="{lg}"></a>')
    parts.append(f"<h2>{flag} {LANGS[lg]}</h2>")
    parts.append("<h3>今週のアイスブレイク</h3>")
    parts.append(f"<
