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
