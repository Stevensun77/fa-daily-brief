from scripts.ig_cards import tokens


def test_bg_color_for_known_category():
    assert tokens.bg_color_for_category("insurance") == "#3d3d41"
    assert tokens.bg_color_for_category("investment") == "#24314c"
    assert tokens.bg_color_for_category("finance") == "#1a2919"
    assert tokens.bg_color_for_category("legacy") == "#342016"


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
