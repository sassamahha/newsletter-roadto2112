import datetime, os, pathlib, textwrap
from openai import OpenAI

# OpenAIクライアント初期化（v1.0以降対応）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATE = datetime.date.today().isoformat()

def ask(prompt):
    """ChatGPTにプロンプトを投げてレスポンスを取得"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1800,
        temperature=1.0
    )
    return response.choices[0].message.content

def main():
    # 各ニュースを生成（日本語）
    news_trend = ask("ささきや商店トレンドニュースを、職人気質のBtoB読者向けに出力してください。トーンは分析寄り、余分な煽りなし。")
    news_future = ask("スタリバの未来仮説ニュースを、問い形式で1本構成してください。10年後を予習するテーマで。")
    news_kids = ask("スタリバキッズ向けに、未来のニュースを小学校低学年でもわかる文体で1本作ってください。問い形式が望ましいです。")

    # 日本語版 Markdown
    md_ja = textwrap.dedent(f"""\
    ## オープニング
    10年後、君のカバンの中に入っているものは？

    ## 今週のショートショート（Study River）
    {news_future}

    ## キッズ向け未来ニュース（Study River Kids）
    {news_kids}

    ## モノの視点から見る未来（ささきや商店）
    {news_trend}

    ## 制作ログ
    – 今週は KDP 第2弾の準備を進行中。
    – 翻訳パイプラインの検証も継続中。
    """)

    # 英語翻訳（自然な表現に）
    md_en = ask(f"Please translate the following markdown newsletter into natural English:\n\n{md_ja}")

    # 統合Markdown
    combined_md = textwrap.dedent(f"""\
    <!-- slug: {DATE}-weekly-roadto2112
    publish_date: {DATE}
    category: newsletter -->

    # 週刊 Road to 2112 🌐

    以下の言語から選んでお読みください：

    - [🇯🇵 日本語](#日本語)
    - [🇺🇸 English](#english)

    ---

    ## 🇯🇵 日本語
    {md_ja}

    ---

    ## 🇺🇸 English
    {md_en}
    """)

    # 保存（1ファイルのみ）
    path = pathlib.Path("newsletters") / "latest.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(combined_md, encoding="utf-8")

if __name__ == "__main__":
    main()
