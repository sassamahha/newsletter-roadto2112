import datetime, pathlib, feedparser, os
from openai import OpenAI

DATE = datetime.date.today().isoformat()
LANGS = {"ja": "Japanese", "en": "English", "es": "Spanish"}

# OpenAIクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ■ 翻訳関数
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

# ■ 1. 今週の余談
note_ja = pathlib.Path("blocks/editor_note.md").read_text().strip()
note = {lg: translate(note_ja, lg) for lg in LANGS}

# ■ 2. RSS取得ユーティリティ
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
intro_ja_path = pathlib.Path("blocks/road_to_2112.md")
intro_ja = intro_ja_path.read_text().strip() if intro_ja_path.exists() else "（紹介文が見つかりませんでした）"
intro = {lg: translate(intro_ja, lg) for lg in LANGS}

# ■ 4. Markdown組立
parts = [
    "---",
    f"slug: {DATE}-weekly-roadto2112",
    f"publish_date: {DATE}",
    f"category: newsletter",
    "---",
    "",  # ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ★重要：空行
    "# 週刊 Road to 2112 🌐"
]

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
