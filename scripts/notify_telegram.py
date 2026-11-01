"""推播最新一份 fa-daily-brief 產出到 Telegram(純標準函式庫,GitHub Actions 用)。"""
import glob
import json
import os
import re
import urllib.parse
import urllib.request

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]
REPO = os.environ.get("REPO", "Stevensun77/fa-daily-brief")


def send(text: str) -> None:
    data = urllib.parse.urlencode(
        {"chat_id": CHAT, "text": text, "disable_web_page_preview": "true"}
    ).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage", data=data
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        assert json.load(r)["ok"]


def chunks(text: str, size: int = 3800):
    while text:
        yield text[:size]
        text = text[size:]


def latest(pattern: str):
    files = sorted(f for f in glob.glob(pattern) if re.search(r"\d{4}-\d{2}-\d{2}\.md$", f))
    return files[-1] if files else None


daily, ig = latest("daily/*.md"), latest("ig/*.md")
if not daily and not ig:
    raise SystemExit("找不到 daily/ig 檔案")

date = (ig or daily).split("/")[-1][:-3]
base = f"https://github.com/{REPO}/blob/main"
head = f"📰 {date} 每日素材已完成"
if daily:
    head += f"\n每日新聞摘要:{base}/{daily}"
if ig:
    head += f"\nIG 文案檔:{base}/{ig}"
send(head)

if ig:
    for part in chunks(open(ig, encoding="utf-8").read()):
        send(part)
