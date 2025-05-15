import datetime, openai, os, pathlib, textwrap

DATE = datetime.date.today().isoformat()
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask(prompt):
    """ChatGPTにプロンプトを投げてレスポンスを取得"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=1800,
        temperature=1.0
    )
    return response["choices"][0]["message"]["content"]

def main():
    # 日本語ニュース生成
    news_trend = ask("ささきや商店トレンドニュースを、職人気質のBtoB読者向けに出力してください。トーンは分析寄り、余分な煽りなし。")
    news_future = ask("スタリバの未来仮説ニュースを、問い形式で1本構成してください。10年後を予習するテーマで。")
    news_kids = ask("スタリバキッズ向けに、未来のニュースを小学校低学年でもわかる文体で1本作ってください。問い形式が望ましいです。")

    md_ja = textwrap.dedent(f"""\
    <!-- slug: {DATE}-weekly-roadto2112
    publish_date: {DATE}
    category: newsletter -->

    # 週刊 Road to 2112

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

    # 保存：日本語版
    path_ja = pathlib.Path("newsletters") / "latest.md"
    path_ja.parent.mkdir(parents=True, exist_ok=True)
    path_ja.write_text(md_ja, encoding="utf-8")

    # 英語翻訳プロンプト
    md_en = ask(f"Please translate the following Japanese markdown newsletter into natural English:\n\n{md_ja}")

    # 保存：英語版
    path_en = pathlib.Path("newsletters") / "latest.en.md"
    path_en.write_text(md_en, encoding="utf-8")

if __name__ == "__main__":
    main()
