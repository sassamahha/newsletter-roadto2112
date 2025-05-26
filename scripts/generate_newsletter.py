#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly multilingual newsletter generator
----------------------------------------
* RSS をクロールして <ul> リスト化
* blocks/editor_note.md をターゲット言語へ翻訳（GPT）
* blocks/kdp_intro_<lang>.md があれば差し込む
* SendGrid (Marketing List) へ送信
* 送信した HTML を newsletters/YYYY-MM-DD_<lang>.html として保存
"""

import os, sys, argparse, datetime, pathlib, textwrap, json, time
import feedparser, markdown
import openai                         # pip install openai>=1,<2
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Personalization, Content


# ---------- 設定 ----------
LANG_FULL = {                         # GPT への指示用
    "ja": "Japanese",
    "en": "English",
    "es": "Spanish",
    "pt": "Portuguese",
    "zh": "Chinese (Simplified)",
    "zh-hant": "Chinese (Traditional)",
    "id": "Indonesian",
    "de": "German",
    "it": "Italian",
    "fr": "French",
}

MODEL = "gpt-4o-mini"                # お好みで
OPENAI_RETRY = 3                     # 軽いリトライ



# ---------- util ----------
def read_file(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def md2html(md_text: str) -> str:
    return markdown.markdown(md_text) if md_text else ""

def translate(md_text: str, target_lang: str) -> str:
    """GPT でマークダウン翻訳。ja→ja など同一言語なら素通し。"""
    if target_lang == "ja":
        return md_text

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = textwrap.dedent(f"""\
        You are a professional translator.
        Translate the following Markdown text into **{LANG_FULL[target_lang]}**.
        Keep all Markdown structure and inline code unchanged.

        ---
        {md_text}
        ---
        Return only the translated Markdown.
    """)

    for attempt in range(1, OPENAI_RETRY + 1):
        try:
            rsp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            return rsp.choices[0].message.content.strip()
        except Exception as e:
            if attempt == OPENAI_RETRY:
                print(f"[!] GPT translate failed ({target_lang}): {e}", file=sys.stderr)
                return md_text
            time.sleep(2 * attempt)


def build_articles(feeds: list[str], limit: int = 10) -> str:
    items = []
    for url in feeds:
        d = feedparser.parse(url)
        items.extend(d.entries)
    items.sort(key=lambda e: e.get("published_parsed") or 0, reverse=True)
    html = ["<ul>"]
    for e in items[:limit]:
        html.append(f'<li><a href="{e.link}">{e.title}</a></li>')
    html.append("</ul>")
    return "\n".join(html)


# ---------- main generator ----------
def generate_html(lang: str, feeds: list[str]) -> str:
    today = datetime.date.today()

    # 1. editor note (翻訳込み)
    src_note_md = read_file(pathlib.Path("blocks/editor_note.md"))
    note_md_translated = translate(src_note_md, lang)
    note_html = md2html(note_md_translated) or "<p>(No editor note)</p>"

    # 2. KDP intro (言語別固定、なければ空)
    kdp_md = read_file(pathlib.Path("blocks") / f"kdp_intro_{lang}.md")
    kdp_html = md2html(kdp_md)

    # 3. Articles
    articles_html = build_articles(feeds)

    return f"""\
<!doctype html><html><body>
{note_html}
<hr/><h2>Latest Articles</h2>
{articles_html}
{('<hr/>'+kdp_html) if kdp_html else ''}
<hr/><p style="font-size:12px;color:#888;">Sent {today} • StudyRiver</p>
</body></html>
"""


def send_via_sendgrid(html: str, lang: str, list_id: str, api_key: str):
    sg = SendGridAPIClient(api_key)
    mail = Mail(
        from_email=From("info@studyriver.jp", "StudyRiver"),
        subject=f"StudyRiver Weekly ({lang}) – {datetime.date.today()}",
        html_content=Content("text/html", html),
    )
    p = Personalization()
    p.add_to(To(email=f"{list_id}@contact.list"))
    mail.add_personalization(p)

    rsp = sg.client.mail.send.post(request_body=mail.get())
    if rsp.status_code >= 300:
        raise RuntimeError(f"SendGrid error {rsp.status_code}: {rsp.body}")


# ---------- CLI ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", required=True, help="ja / en / es …")
    ap.add_argument("--list-id", required=True, help="SendGrid Marketing List ID (digits)")
    ap.add_argument("--feeds", required=True, help="newline-separated RSS URLs")

    args = ap.parse_args()
    feeds = [f.strip() for f in args.feeds.splitlines() if f.strip()]

    # HTML build
    html = generate_html(args.lang, feeds)

    # Archive locally
    out_dir = pathlib.Path("newsletters"); out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{datetime.date.today()}_{args.lang}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"[+] saved {out_path}")

    # Send
    send_via_sendgrid(html, args.lang, args.list_id, os.environ["SENDGRID_API_KEY"])
    print(f"[+] sent to list {args.list_id}")

if __name__ == "__main__":
    main()
