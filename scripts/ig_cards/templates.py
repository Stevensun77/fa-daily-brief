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
