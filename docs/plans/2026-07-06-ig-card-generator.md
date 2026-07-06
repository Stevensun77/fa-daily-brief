# IG 圖文卡片產生器 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `ig/YYYY-MM-DD.md` 的三段式 IG 文案,轉成一組套用固定視覺模板的 1080×1350 PNG 輪播圖卡(封面卡 / 內文金句卡 / CTA 卡)。

**Architecture:** 純 Python 腳本,不依賴任何 web 框架。內容(文字)與樣式(HTML/CSS token)分離:`tokens.py` 定義顏色/字體/尺寸,`templates.py` 用這些 token 產生每種卡片的完整 HTML 字串,`card_builder.py` 把一份結構化的 JSON 內容(`ig/YYYY-MM-DD/cards.json`)組成一串「檔名 + HTML」,`renderer.py` 用 Playwright 把每個 HTML 截圖成 PNG,`generate.py` 是串起以上流程的 CLI 入口。手動執行,不接入現有的每日自動排程。

**Tech Stack:** Python 3.14、`playwright`(已安裝 1.56.0,含 chromium)、`pytest`、`Pillow`(測試截圖尺寸用)。

## Global Constraints

以下數值直接對應 `docs/specs/2026-07-06-ig-card-style-design.md`,每個 Task 的程式碼都必須照這些值寫,不可自行調整:

- 語言:所有卡片文字一律台灣繁體中文。
- 卡片尺寸:`1080 x 1350` px(4:5),Playwright viewport 與輸出 PNG 都是這個尺寸。
- 內容邊界 `CONTENT_MARGIN = 86` px:金線、底部列(IG 帳號/頁碼)、所有文字區塊的水平內距都用這個值,不得各自使用不同數字。
- 底色 token(依新聞焦點領域):
  - `investment` → `#0f1620`(深海軍藍)
  - `insurance` → `#16181c`(鐵灰霧面)
  - `finance` → `#10201a`(深綠霧面)
  - `legacy` → `#1c140f`(深棕霧面)
  - 未知類別(含「社會大小事」)一律 fallback 到 `investment`。
- 字體:`Noto Sans TC`,透過 Google Fonts CDN 載入,URL 固定為 `https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap`。
- 文字顏色:主文字 `#f5f3ee`、內文次要文字 `#c7cdd6`、金線 `#c9a86a`、金句文字 `#e8c98a`、底部小字(IG 帳號/頁碼)`#6b7480`。
- 字級(px):標題 97、金句 68、內文段落 45、CTA 主文字 58、CTA 導流句 65、底部小字 36。
- IG 帳號固定顯示純文字 handle(不含圖示),頁碼格式固定為 `"NN / TT"`(兩位數,例如 `01 / 04`)。
- 封面卡不放任何頂部標籤文字,標題整張垂直置中;標題下方的金線左右邊界對齊 `CONTENT_MARGIN`,不是置中短線,也不頂到卡片邊緣。
- 輸出檔名格式固定為 `{index:02d}-{card_type}.png`(`card_type` 是 `cover` / `quote` / `cta`),存到 `ig/YYYY-MM-DD/` 資料夾。
- 產圖流程手動觸發,本計畫不修改、不接入任何自動排程。

---

## Task 1: 專案相依套件與 design tokens 模組

**Files:**
- Create: `fa-daily-brief/requirements.txt`
- Create: `fa-daily-brief/scripts/__init__.py`
- Create: `fa-daily-brief/scripts/ig_cards/__init__.py`
- Create: `fa-daily-brief/scripts/ig_cards/tokens.py`
- Test: `fa-daily-brief/tests/ig_cards/test_tokens.py`
- Create: `fa-daily-brief/tests/__init__.py`
- Create: `fa-daily-brief/tests/ig_cards/__init__.py`

**Interfaces:**
- Produces: `tokens.CARD_WIDTH: int`, `tokens.CARD_HEIGHT: int`, `tokens.CONTENT_MARGIN: int`, `tokens.FONT_FAMILY: str`, `tokens.FONT_IMPORT_URL: str`, `tokens.COLOR_TEXT_PRIMARY: str`, `tokens.COLOR_TEXT_BODY: str`, `tokens.COLOR_ACCENT_GOLD_LINE: str`, `tokens.COLOR_ACCENT_GOLD_TEXT: str`, `tokens.COLOR_TEXT_META: str`, `tokens.FONT_SIZE_HEADLINE/QUOTE/BODY/CTA_TEXT/CTA_LINE/META: int`, `tokens.CATEGORY_BG_COLORS: dict[str, str]`, `tokens.DEFAULT_CATEGORY: str`, `tokens.bg_color_for_category(category: str) -> str`, `tokens.format_page_label(index: int, total: int) -> str`, `tokens.output_filename(index: int, total: int, card_type: str) -> str`

- [ ] **Step 1: 安裝相依套件**

建立 `fa-daily-brief/requirements.txt`:

```txt
playwright==1.56.0
pytest>=8.0
Pillow>=10.0
```

執行安裝:

```bash
cd fa-daily-brief
pip install -r requirements.txt
playwright install chromium
```

Expected: 兩個指令都無錯誤結束(`playwright` 1.56.0 與 chromium 瀏覽器機器上已經有,這步驟主要是補裝 `pytest`、`Pillow`,並確保 `playwright install chromium` 是 idempotent 的,重複執行不會壞)。

- [ ] **Step 2: 建立套件目錄與空的 `__init__.py`**

```bash
mkdir -p scripts/ig_cards tests/ig_cards
touch scripts/__init__.py scripts/ig_cards/__init__.py tests/__init__.py tests/ig_cards/__init__.py
```

- [ ] **Step 3: 寫失敗的 tokens 測試**

建立 `tests/ig_cards/test_tokens.py`:

```python
from scripts.ig_cards import tokens


def test_bg_color_for_known_category():
    assert tokens.bg_color_for_category("insurance") == "#16181c"
    assert tokens.bg_color_for_category("investment") == "#0f1620"
    assert tokens.bg_color_for_category("finance") == "#10201a"
    assert tokens.bg_color_for_category("legacy") == "#1c140f"


def test_bg_color_for_unknown_category_defaults_to_investment():
    assert tokens.bg_color_for_category("social") == tokens.CATEGORY_BG_COLORS["investment"]
    assert tokens.bg_color_for_category("") == tokens.CATEGORY_BG_COLORS["investment"]


def test_format_page_label():
    assert tokens.format_page_label(1, 4) == "01 / 04"
    assert tokens.format_page_label(10, 12) == "10 / 12"


def test_output_filename():
    assert tokens.output_filename(1, 4, "cover") == "01-cover.png"
    assert tokens.output_filename(3, 4, "quote") == "03-quote.png"
    assert tokens.output_filename(4, 4, "cta") == "04-cta.png"
```

- [ ] **Step 4: 執行測試,確認失敗**

```bash
cd fa-daily-brief
python -m pytest tests/ig_cards/test_tokens.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.ig_cards.tokens'`(因為 `tokens.py` 還沒建立)。

- [ ] **Step 5: 建立 `tokens.py`**

```python
"""Design tokens for IG card templates.

See docs/specs/2026-07-06-ig-card-style-design.md for the source of these values.
"""

CARD_WIDTH = 1080
CARD_HEIGHT = 1350
CONTENT_MARGIN = 86

FONT_FAMILY = "Noto Sans TC"
FONT_IMPORT_URL = (
    "https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap"
)

COLOR_TEXT_PRIMARY = "#f5f3ee"
COLOR_TEXT_BODY = "#c7cdd6"
COLOR_ACCENT_GOLD_LINE = "#c9a86a"
COLOR_ACCENT_GOLD_TEXT = "#e8c98a"
COLOR_TEXT_META = "#6b7480"

FONT_SIZE_HEADLINE = 97
FONT_SIZE_QUOTE = 68
FONT_SIZE_BODY = 45
FONT_SIZE_CTA_TEXT = 58
FONT_SIZE_CTA_LINE = 65
FONT_SIZE_META = 36

CATEGORY_BG_COLORS = {
    "investment": "#0f1620",
    "insurance": "#16181c",
    "finance": "#10201a",
    "legacy": "#1c140f",
}
DEFAULT_CATEGORY = "investment"


def bg_color_for_category(category: str) -> str:
    return CATEGORY_BG_COLORS.get(category, CATEGORY_BG_COLORS[DEFAULT_CATEGORY])


def format_page_label(index: int, total: int) -> str:
    return f"{index:02d} / {total:02d}"


def output_filename(index: int, total: int, card_type: str) -> str:
    return f"{index:02d}-{card_type}.png"
```

- [ ] **Step 6: 執行測試,確認通過**

```bash
python -m pytest tests/ig_cards/test_tokens.py -v
```

Expected: 4 個測試全部 `PASS`。

- [ ] **Step 7: Commit**

```bash
git add requirements.txt scripts/__init__.py scripts/ig_cards/__init__.py scripts/ig_cards/tokens.py tests/__init__.py tests/ig_cards/__init__.py tests/ig_cards/test_tokens.py
git commit -m "Add design tokens module for IG cards"
```

---

## Task 2: HTML 樣板模組(封面卡 / 內文金句卡 / CTA 卡)

**Files:**
- Create: `fa-daily-brief/scripts/ig_cards/templates.py`
- Test: `fa-daily-brief/tests/ig_cards/test_templates.py`

**Interfaces:**
- Consumes: `tokens.CARD_WIDTH`, `tokens.CARD_HEIGHT`, `tokens.CONTENT_MARGIN`, `tokens.FONT_FAMILY`, `tokens.FONT_IMPORT_URL`, `tokens.COLOR_TEXT_PRIMARY`, `tokens.COLOR_TEXT_BODY`, `tokens.COLOR_ACCENT_GOLD_LINE`, `tokens.COLOR_ACCENT_GOLD_TEXT`, `tokens.COLOR_TEXT_META`, `tokens.FONT_SIZE_*`(全部,來自 Task 1)
- Produces: `templates.render_cover_card(headline: str, handle: str, page_label: str, bg_color: str) -> str`, `templates.render_quote_card(quote: str, body: str, handle: str, page_label: str, bg_color: str) -> str`, `templates.render_cta_card(text: str, line: str, handle: str, page_label: str, bg_color: str) -> str`

- [ ] **Step 1: 寫失敗的樣板測試**

建立 `tests/ig_cards/test_templates.py`:

```python
from scripts.ig_cards import templates


def test_render_cover_card_contains_headline_bg_handle_and_page_label():
    html = templates.render_cover_card(
        headline="如果你做完手術\n當天就回家,\n你的醫療險\n賠得到嗎?",
        handle="@sghongfire",
        page_label="01 / 04",
        bg_color="#16181c",
    )
    assert "#16181c" in html
    assert "如果你做完手術<br>當天就回家,<br>你的醫療險<br>賠得到嗎?" in html
    assert "@sghongfire" in html
    assert "01 / 04" in html
    assert "財務顧問手記" not in html  # 已確認拿掉頂部標籤


def test_render_quote_card_contains_quote_and_body():
    html = templates.render_quote_card(
        quote="醫療進步了,\n保單卻沒跟上。",
        body="前陣子有客戶做內視鏡手術,當天就出院。",
        handle="@sghongfire",
        page_label="02 / 04",
        bg_color="#16181c",
    )
    assert "醫療進步了,<br>保單卻沒跟上。" in html
    assert "前陣子有客戶做內視鏡手術,當天就出院。" in html
    assert "02 / 04" in html


def test_render_cta_card_contains_text_and_line():
    html = templates.render_cta_card(
        text="不確定自己的保單\n現在賠不賠得到?",
        line="歡迎加我 LINE,\n免費幫你看一次保單",
        handle="@sghongfire",
        page_label="04 / 04",
        bg_color="#16181c",
    )
    assert "不確定自己的保單<br>現在賠不賠得到?" in html
    assert "歡迎加我 LINE,<br>免費幫你看一次保單" in html
    assert "04 / 04" in html


def test_text_with_ampersand_is_escaped():
    html = templates.render_cover_card(
        headline="退休金 & 保單健檢",
        handle="@sghongfire",
        page_label="01 / 04",
        bg_color="#16181c",
    )
    assert "退休金 &amp; 保單健檢" in html
```

- [ ] **Step 2: 執行測試,確認失敗**

```bash
python -m pytest tests/ig_cards/test_templates.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.ig_cards.templates'`。

- [ ] **Step 3: 建立 `templates.py`**

```python
"""HTML card templates. Positions/sizes derived from
docs/specs/2026-07-06-ig-card-style-design.md.
"""

import html as html_lib

from . import tokens


def _text_to_html(text: str) -> str:
    return html_lib.escape(text).replace("\n", "<br>")


def _wrap_card(bg_color: str, inner_html: str, handle: str, page_label: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('{tokens.FONT_IMPORT_URL}');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{
    width: {tokens.CARD_WIDTH}px;
    height: {tokens.CARD_HEIGHT}px;
    overflow: hidden;
    font-family: '{tokens.FONT_FAMILY}', sans-serif;
  }}
  .card {{
    width: {tokens.CARD_WIDTH}px;
    height: {tokens.CARD_HEIGHT}px;
    position: relative;
    background: {bg_color};
  }}
  .footbar {{
    position: absolute;
    bottom: 65px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    padding: 0 {tokens.CONTENT_MARGIN}px;
    font-size: {tokens.FONT_SIZE_META}px;
    color: {tokens.COLOR_TEXT_META};
    letter-spacing: 4px;
  }}
</style>
</head>
<body>
  <div class="card">
    {inner_html}
    <div class="footbar"><span>{handle}</span><span>{page_label}</span></div>
  </div>
</body>
</html>"""


def render_cover_card(headline: str, handle: str, page_label: str, bg_color: str) -> str:
    inner = f"""
    <div style="position:absolute; top:0; left:0; right:0; bottom:0;
                 display:flex; align-items:center; justify-content:center;">
      <div style="text-align:center; padding:0 {tokens.CONTENT_MARGIN}px;
                   color:{tokens.COLOR_TEXT_PRIMARY}; font-size:{tokens.FONT_SIZE_HEADLINE}px;
                   font-weight:900; line-height:1.6;">
        {_text_to_html(headline)}
      </div>
    </div>
    <div style="position:absolute; bottom:187px; left:{tokens.CONTENT_MARGIN}px;
                 right:{tokens.CONTENT_MARGIN}px; height:4px;
                 background:{tokens.COLOR_ACCENT_GOLD_LINE};"></div>
    """
    return _wrap_card(bg_color, inner, handle, page_label)


def render_quote_card(quote: str, body: str, handle: str, page_label: str, bg_color: str) -> str:
    inner = f"""
    <div style="position:absolute; top:108px; left:{tokens.CONTENT_MARGIN}px;
                 font-size:122px; color:#3a4552; font-weight:900;">&ldquo;</div>
    <div style="position:absolute; top:202px; left:0; right:0;
                 padding:0 {tokens.CONTENT_MARGIN}px; text-align:center;
                 color:{tokens.COLOR_ACCENT_GOLD_TEXT}; font-size:{tokens.FONT_SIZE_QUOTE}px;
                 font-weight:700; line-height:1.5;">
      {_text_to_html(quote)}
    </div>
    <div style="position:absolute; top:569px; left:0; right:0;
                 padding:0 {tokens.CONTENT_MARGIN}px; text-align:left;
                 color:{tokens.COLOR_TEXT_BODY}; font-size:{tokens.FONT_SIZE_BODY}px;
                 font-weight:400; line-height:1.85;">
      {_text_to_html(body)}
    </div>
    """
    return _wrap_card(bg_color, inner, handle, page_label)


def render_cta_card(text: str, line: str, handle: str, page_label: str, bg_color: str) -> str:
    inner = f"""
    <div style="position:absolute; top:324px; left:0; right:0;
                 padding:0 {tokens.CONTENT_MARGIN}px; text-align:center;
                 color:{tokens.COLOR_TEXT_PRIMARY}; font-size:{tokens.FONT_SIZE_CTA_TEXT}px;
                 font-weight:500; line-height:1.9;">
      {_text_to_html(text)}
    </div>
    <div style="position:absolute; top:900px; left:0; right:0;
                 text-align:center; color:{tokens.COLOR_ACCENT_GOLD_TEXT};
                 font-size:{tokens.FONT_SIZE_CTA_LINE}px; font-weight:900; letter-spacing:4px;">
      {_text_to_html(line)}
    </div>
    """
    return _wrap_card(bg_color, inner, handle, page_label)
```

- [ ] **Step 4: 執行測試,確認通過**

```bash
python -m pytest tests/ig_cards/test_templates.py -v
```

Expected: 4 個測試全部 `PASS`。

- [ ] **Step 5: Commit**

```bash
git add scripts/ig_cards/templates.py tests/ig_cards/test_templates.py
git commit -m "Add HTML templates for cover/quote/CTA cards"
```

---

## Task 3: 內容組裝邏輯(cards.json → 卡片清單)

**Files:**
- Create: `fa-daily-brief/scripts/ig_cards/card_builder.py`
- Test: `fa-daily-brief/tests/ig_cards/test_card_builder.py`

**Interfaces:**
- Consumes: `tokens.bg_color_for_category`, `tokens.format_page_label`, `tokens.output_filename`(Task 1); `templates.render_cover_card`, `templates.render_quote_card`, `templates.render_cta_card`(Task 2)
- Produces: `card_builder.build_cards(data: dict) -> list[dict]`,每個 dict 有 `"filename": str` 與 `"html": str` 兩個 key

- [ ] **Step 1: 寫失敗的測試**

建立 `tests/ig_cards/test_card_builder.py`:

```python
from scripts.ig_cards import card_builder

SAMPLE_DATA = {
    "category": "insurance",
    "handle": "@sghongfire",
    "cover": {"headline": "如果你做完手術\n當天就回家,\n你的醫療險\n賠得到嗎?"},
    "quotes": [
        {"quote": "醫療進步了,\n保單卻沒跟上。", "body": "案例段落一。"},
        {"quote": "保障邏輯,\n要跟著醫療方式一起升級。", "body": "解法段落二。"},
    ],
    "cta": {
        "text": "不確定自己的保單\n現在賠不賠得到?",
        "line": "歡迎加我 LINE,\n免費幫你看一次保單",
    },
}


def test_build_cards_returns_cover_quotes_and_cta_in_order():
    cards = card_builder.build_cards(SAMPLE_DATA)
    filenames = [c["filename"] for c in cards]
    assert filenames == [
        "01-cover.png",
        "02-quote.png",
        "03-quote.png",
        "04-cta.png",
    ]


def test_build_cards_html_contains_correct_content_per_card():
    cards = card_builder.build_cards(SAMPLE_DATA)
    assert "如果你做完手術" in cards[0]["html"]
    assert "01 / 04" in cards[0]["html"]
    assert "醫療進步了" in cards[1]["html"]
    assert "02 / 04" in cards[1]["html"]
    assert "保障邏輯" in cards[2]["html"]
    assert "03 / 04" in cards[2]["html"]
    assert "歡迎加我 LINE" in cards[3]["html"]
    assert "04 / 04" in cards[3]["html"]


def test_build_cards_uses_category_bg_color():
    cards = card_builder.build_cards(SAMPLE_DATA)
    for card in cards:
        assert "#16181c" in card["html"]  # insurance 底色


def test_build_cards_supports_variable_quote_count():
    data = dict(SAMPLE_DATA)
    data["quotes"] = [{"quote": "只有一句金句。", "body": "只有一段內文。"}]
    cards = card_builder.build_cards(data)
    filenames = [c["filename"] for c in cards]
    assert filenames == ["01-cover.png", "02-quote.png", "03-cta.png"]
```

- [ ] **Step 2: 執行測試,確認失敗**

```bash
python -m pytest tests/ig_cards/test_card_builder.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.ig_cards.card_builder'`。

- [ ] **Step 3: 建立 `card_builder.py`**

```python
"""Turns a day's structured IG content into an ordered list of
{filename, html} card specs. Pure logic, no file or network IO."""

from . import tokens, templates


def build_cards(data: dict) -> list[dict]:
    handle = data["handle"]
    bg_color = tokens.bg_color_for_category(data["category"])
    quotes = data["quotes"]
    total = 2 + len(quotes)  # cover + quotes + cta

    cards = []

    index = 1
    cards.append({
        "filename": tokens.output_filename(index, total, "cover"),
        "html": templates.render_cover_card(
            headline=data["cover"]["headline"],
            handle=handle,
            page_label=tokens.format_page_label(index, total),
            bg_color=bg_color,
        ),
    })

    for quote_data in quotes:
        index += 1
        cards.append({
            "filename": tokens.output_filename(index, total, "quote"),
            "html": templates.render_quote_card(
                quote=quote_data["quote"],
                body=quote_data["body"],
                handle=handle,
                page_label=tokens.format_page_label(index, total),
                bg_color=bg_color,
            ),
        })

    index += 1
    cards.append({
        "filename": tokens.output_filename(index, total, "cta"),
        "html": templates.render_cta_card(
            text=data["cta"]["text"],
            line=data["cta"]["line"],
            handle=handle,
            page_label=tokens.format_page_label(index, total),
            bg_color=bg_color,
        ),
    })

    return cards
```

- [ ] **Step 4: 執行測試,確認通過**

```bash
python -m pytest tests/ig_cards/test_card_builder.py -v
```

Expected: 4 個測試全部 `PASS`。

- [ ] **Step 5: Commit**

```bash
git add scripts/ig_cards/card_builder.py tests/ig_cards/test_card_builder.py
git commit -m "Add card content builder"
```

---

## Task 4: Playwright 截圖模組

**Files:**
- Create: `fa-daily-brief/scripts/ig_cards/renderer.py`
- Test: `fa-daily-brief/tests/ig_cards/test_renderer.py`

**Interfaces:**
- Consumes: `tokens.CARD_WIDTH`, `tokens.CARD_HEIGHT`(Task 1)
- Produces: `renderer.render_to_png(html: str, output_path: str) -> None`

- [ ] **Step 1: 寫失敗的測試**

建立 `tests/ig_cards/test_renderer.py`:

```python
from PIL import Image

from scripts.ig_cards import renderer

MINIMAL_HTML = """<!DOCTYPE html>
<html><head><style>
  html, body { margin:0; padding:0; width:1080px; height:1350px; background:#16181c; }
</style></head>
<body></body></html>"""


def test_render_to_png_creates_file_with_correct_dimensions(tmp_path):
    output_path = tmp_path / "test-card.png"

    renderer.render_to_png(MINIMAL_HTML, str(output_path))

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.size == (1080, 1350)
```

- [ ] **Step 2: 執行測試,確認失敗**

```bash
python -m pytest tests/ig_cards/test_renderer.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.ig_cards.renderer'`。

- [ ] **Step 3: 建立 `renderer.py`**

```python
"""Renders a card's HTML string to a PNG file using headless Chromium."""

from playwright.sync_api import sync_playwright

from . import tokens


def render_to_png(html: str, output_path: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": tokens.CARD_WIDTH, "height": tokens.CARD_HEIGHT}
        )
        page.set_content(html, wait_until="networkidle")
        page.wait_for_timeout(500)
        page.screenshot(path=output_path)
        browser.close()
```

- [ ] **Step 4: 執行測試,確認通過**

```bash
python -m pytest tests/ig_cards/test_renderer.py -v
```

Expected: 1 個測試 `PASS`(這個測試會真的開一個無頭瀏覽器,大約需要幾秒鐘)。

- [ ] **Step 5: Commit**

```bash
git add scripts/ig_cards/renderer.py tests/ig_cards/test_renderer.py
git commit -m "Add Playwright PNG renderer for IG cards"
```

---

## Task 5: CLI 入口(串起 tokens → templates → card_builder → renderer)

**Files:**
- Create: `fa-daily-brief/scripts/ig_cards/generate.py`
- Test: `fa-daily-brief/tests/ig_cards/test_generate.py`

**Interfaces:**
- Consumes: `card_builder.build_cards`(Task 3)、`renderer.render_to_png`(Task 4)
- Produces: `generate.load_cards_data(cards_file: Path) -> dict`、`generate.run(cards_file: Path, output_dir: Path) -> list[Path]`(回傳實際寫出的 PNG 路徑清單)、CLI 入口 `python -m scripts.ig_cards.generate <date>`

- [ ] **Step 1: 寫失敗的測試**

建立 `tests/ig_cards/test_generate.py`:

```python
import json

from scripts.ig_cards import generate

SAMPLE_DATA = {
    "category": "insurance",
    "handle": "@sghongfire",
    "cover": {"headline": "測試標題"},
    "quotes": [{"quote": "測試金句", "body": "測試內文"}],
    "cta": {"text": "測試 CTA", "line": "測試導流句"},
}


def test_load_cards_data_reads_json(tmp_path):
    cards_file = tmp_path / "cards.json"
    cards_file.write_text(json.dumps(SAMPLE_DATA, ensure_ascii=False), encoding="utf-8")

    data = generate.load_cards_data(cards_file)

    assert data == SAMPLE_DATA


def test_run_writes_expected_png_files(tmp_path):
    cards_file = tmp_path / "cards.json"
    cards_file.write_text(json.dumps(SAMPLE_DATA, ensure_ascii=False), encoding="utf-8")
    output_dir = tmp_path

    written = generate.run(cards_file, output_dir)

    written_names = sorted(p.name for p in written)
    assert written_names == ["01-cover.png", "02-quote.png", "03-cta.png"]
    for path in written:
        assert path.exists()
        assert path.stat().st_size > 0
```

- [ ] **Step 2: 執行測試,確認失敗**

```bash
python -m pytest tests/ig_cards/test_generate.py -v
```

Expected: `ModuleNotFoundError: No module named 'scripts.ig_cards.generate'`。

- [ ] **Step 3: 建立 `generate.py`**

```python
"""CLI entrypoint: reads ig/<date>/cards.json, generates the card PNGs
into the same folder.

Usage (run from the fa-daily-brief repo root):
    python -m scripts.ig_cards.generate 2026-07-06
"""

import argparse
import json
from pathlib import Path

from . import card_builder, renderer


def load_cards_data(cards_file: Path) -> dict:
    return json.loads(cards_file.read_text(encoding="utf-8"))


def run(cards_file: Path, output_dir: Path) -> list[Path]:
    data = load_cards_data(cards_file)
    cards = card_builder.build_cards(data)

    written = []
    for card in cards:
        output_path = output_dir / card["filename"]
        renderer.render_to_png(card["html"], str(output_path))
        written.append(output_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate IG carousel card PNGs from ig/<date>/cards.json"
    )
    parser.add_argument("date", help="Date folder under ig/, format YYYY-MM-DD")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    cards_dir = repo_root / "ig" / args.date
    cards_file = cards_dir / "cards.json"

    written = run(cards_file, cards_dir)
    for path in written:
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 執行測試,確認通過**

```bash
python -m pytest tests/ig_cards/test_generate.py -v
```

Expected: 2 個測試全部 `PASS`(`test_run_writes_expected_png_files` 一樣會真的開瀏覽器渲染 3 張圖,需要幾秒鐘)。

- [ ] **Step 5: 執行完整測試套件,確認整體沒有壞掉**

```bash
python -m pytest tests/ -v
```

Expected: 目前為止所有測試(tokens、templates、card_builder、renderer、generate)全部 `PASS`。

- [ ] **Step 6: Commit**

```bash
git add scripts/ig_cards/generate.py tests/ig_cards/test_generate.py
git commit -m "Add CLI entrypoint wiring card generation pipeline"
```

---

## Task 6: 第一個真實案例 —— 2026-07-06 手術險文案出圖

**Files:**
- Create: `fa-daily-brief/ig/2026-07-06/cards.json`
- Create (generated, not hand-written): `fa-daily-brief/ig/2026-07-06/01-cover.png`, `02-quote.png`, `03-quote.png`, `04-cta.png`

**Interfaces:**
- Consumes: `generate.main()` / `python -m scripts.ig_cards.generate`(Task 5)

- [ ] **Step 1: 用今天的文案內容建立 `ig/2026-07-06/cards.json`**

內容取自 `ig/2026-07-06.md`(案例導入 / 解決做法 / CTA 三段式文案),對應到 2 張內文金句卡:

```bash
mkdir -p ig/2026-07-06
```

建立 `ig/2026-07-06/cards.json`:

```json
{
  "category": "insurance",
  "handle": "@sghongfire",
  "cover": {
    "headline": "如果你做完手術\n當天就回家,\n你的醫療險\n賠得到嗎?"
  },
  "quotes": [
    {
      "quote": "醫療進步了,\n保單卻沒跟上。",
      "body": "前陣子有客戶做內視鏡手術,當天就出院,結果理賠時才發現保單是用「住院天數」算錢的——沒住院,很多項目根本賠不到。\n\n金管會也說明:一日「住院」手術要符合三要件才能比照住院理賠,沒辦住院手續的一律當門診手術認定。"
    },
    {
      "quote": "保障邏輯,\n要跟著醫療方式一起升級。",
      "body": "給你 2 個檢查方向:\n\n1. 翻開保單找「實支實付醫療險」條款,看清楚門診手術、特定醫療處置有沒有涵蓋,理賠條件是什麼。\n\n2. 如果保單是 10 年以上的老保單,大概率沒把「一日手術」這類新型態醫療考慮進去,建議找時間做個保單健檢。"
    }
  ],
  "cta": {
    "text": "醫療方式一直在變,\n保障邏輯也該跟著調整。\n\n不確定自己的保單\n現在賠不賠得到?",
    "line": "歡迎加我 LINE,\n免費幫你看一次保單"
  }
}
```

- [ ] **Step 2: 執行 CLI 產生圖片**

```bash
cd fa-daily-brief
python -m scripts.ig_cards.generate 2026-07-06
```

Expected: 印出 4 行 `Saved ...`,分別對應 `01-cover.png`、`02-quote.png`、`03-quote.png`、`04-cta.png`,檔案都寫入 `ig/2026-07-06/` 資料夾。

- [ ] **Step 3: 人工視覺檢查(這一步沒有自動化測試,是設計驗收)**

打開這 4 張 PNG,對照 `docs/specs/2026-07-06-ig-card-style-design.md` 檢查:

- 尺寸是否為 1080×1350
- 封面卡標題是否置中、沒有頂部標籤文字,金線是否對齊左右邊界(不是置中短線)
- 金句是否為金色、內文是否為淺灰藍色、清楚可讀
- 每張卡片底部是否都有 `@sghongfire` 與正確頁碼(`01 / 04` ~ `04 / 04`)
- 底色是否為保險類別的鐵灰霧面(`#16181c`)
- 中文字有沒有正確顯示(不是方框缺字),行距、字級是否舒適

如果有任何一項不符合,回到對應的 Task(通常是 Task 2 的 `templates.py`)調整,重新執行 Step 2 出圖再檢查一次。

- [ ] **Step 4: Commit**

```bash
git add ig/2026-07-06/cards.json ig/2026-07-06/01-cover.png ig/2026-07-06/02-quote.png ig/2026-07-06/03-quote.png ig/2026-07-06/04-cta.png
git commit -m "Generate first IG card set for 2026-07-06 surgical insurance post"
```
