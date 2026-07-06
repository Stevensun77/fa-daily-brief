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
