import datetime, pathlib, feedparser, textwrap, os
from openai import OpenAI

DATE = datetime.date.today().isoformat()
LANGS = {"ja": "Japanese", "en": "English", "es": "Spanish"}

# OpenAIクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ■ 1. 今週の余談
note_ja = pathlib.Path("blocks/editor_note.md").read_text().strip()

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

note = {lg: translate(note_ja, lg) for lg in LANGS}

# ■ 2. RSS 取得ユーティリティ
def rss_block(url, max_items=3):
    feed = feedparser.parse(url)
    lines = [f"- [{e.title}]({e.link})" for e in feed.entries[:max_items]]
    return "\n".join(lines) if lines else "_No updates._"

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

# ■ 3. Road to 2112 紹介文
intro_ja = pathlib.Path("blocks/road_to_2112.md").read_text().strip()
intro = {lg: translate(intro_ja, lg) for lg in LANGS}

# ■ 4. Markdown 組立
parts = [f"<!-- slug: {DATE}-weekly-roadto2112\npublish_date: {DATE}\ncategory: newsletter -->\n",
         "# 週刊 Road to 2112 🌐\n"]

for lg, flag in (("ja", "🇯🇵"), ("en", "🇺🇸"), ("es", "🇪🇸")):
    parts.append(f"\n---\n## {flag} {LANGS[lg]}\n")
    parts.append("### 今週のアイスブレイク\n")
    parts.append(note[lg] + "\n")
    parts.append("### 最新記事 (RSS)\n")
    for label, url in RSS_MAP[lg].items():
        parts.append(f"**{label}**\n{rss_block(url)}\n")
    parts.append("### 📘 Road to 2112\n")
    parts.append(intro[lg] + "\n")

# Save
out = pathlib.Path("newsletters/latest.md")
out.write_text("\n".join(parts), encoding="utf-8")
print("✅ Markdown generated:", out)
