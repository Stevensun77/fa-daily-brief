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
