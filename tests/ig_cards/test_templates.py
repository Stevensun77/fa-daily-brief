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
