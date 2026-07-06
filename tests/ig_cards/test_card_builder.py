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
        assert "#3d3d41" in card["html"]  # insurance 底色


def test_build_cards_supports_variable_quote_count():
    data = dict(SAMPLE_DATA)
    data["quotes"] = [{"quote": "只有一句金句。", "body": "只有一段內文。"}]
    cards = card_builder.build_cards(data)
    filenames = [c["filename"] for c in cards]
    assert filenames == ["01-cover.png", "02-quote.png", "03-cta.png"]
