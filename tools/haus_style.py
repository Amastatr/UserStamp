"""The Haus style — typographic system for AMASTATR INNOVATION HAUS dossiers.

Reproduces the look of the reference document (The Quarry): three typefaces
(Fraunces display, Newsreader text, JetBrains Mono labels) and an oxblood /
crimson accent palette over near-black ink.

`HausBook` is an FPDF subclass exposing the building blocks — kicker, title,
ornament, section divider, headings, body, pull quote, citation — that the
PDF builder composes into a book.
"""
from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# --- page geometry (US Letter, in mm) -------------------------------------- #
PAGE = ("Letter",)
MARGIN_X = 26.7
MARGIN_TOP = 24.0
MARGIN_BOT = 22.0

# --- palette (RGB), lifted from the reference document --------------------- #
INK = (29, 29, 31)        # #1D1D1F  body text
INK_TRUE = (10, 10, 10)   # #0A0A0A  display headings
OXBLOOD = (138, 10, 30)   # #8A0A1E  title, strongest accent
CRIMSON = (200, 16, 46)   # #C8102E  ornaments, section markers
GREY = (74, 77, 80)       # #4A4D50  italic lead-ins, subtitle
GREY_MID = (110, 113, 116)  # #6E7174 citations
GREY_LT = (122, 125, 128)   # #7A7D80 faint metadata
RULE = (210, 210, 212)

# --- font families --------------------------------------------------------- #
FRAUNCES = "Fraunces"   # display serif: title + headings
NEWS = "News"           # text serif: body, quotes, lead-ins
MONO = "Mono"           # labels, citations, kickers
ORN = "Orn"             # ornaments only

ORNAMENT = "❦"      # ❦ floral heart


class HausBook(FPDF):
    def __init__(self, short_title: str, organization: str):
        super().__init__(format="Letter")
        self.short_title = short_title.upper()
        self.organization = organization.upper()
        self.set_margins(MARGIN_X, MARGIN_TOP, MARGIN_X)
        self.set_auto_page_break(auto=True, margin=MARGIN_BOT)
        self._register_fonts()
        self.set_font(NEWS, "", 11)
        self._chrome = True  # whether running header/footer should print

    # ------------------------------------------------------------------ #
    def _register_fonts(self):
        f = str(FONT_DIR)
        self.add_font(FRAUNCES, "", f + "/Fraunces-Display.ttf")
        self.add_font(FRAUNCES, "B", f + "/Fraunces-Display-Semibold.ttf")
        self.add_font(NEWS, "", f + "/Newsreader-Regular.ttf")
        self.add_font(NEWS, "B", f + "/Newsreader-Bold.ttf")
        self.add_font(NEWS, "I", f + "/Newsreader-Italic.ttf")
        self.add_font(NEWS, "BI", f + "/Newsreader-BoldItalic.ttf")
        self.add_font(MONO, "", f + "/JetBrainsMono-Regular.ttf")
        self.add_font(MONO, "B", f + "/JetBrainsMono-Bold.ttf")
        self.add_font(ORN, "", f + "/Ornaments.ttf")

    @property
    def content_width(self) -> float:
        return self.w - self.l_margin - self.r_margin

    # ------------------------------------------------------------------ #
    # Running chrome                                                      #
    # ------------------------------------------------------------------ #
    def header(self):
        if not self._chrome or self.page_no() == 1:
            return
        self.set_y(13)
        self.set_font(MONO, "", 7)
        self.set_text_color(*GREY_LT)
        self.set_char_spacing(0.6)
        self.cell(self.content_width / 2, 5, self.short_title, align="L")
        self.cell(self.content_width / 2, 5, self.organization, align="R")
        self.set_char_spacing(0)
        self.ln(6)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.set_text_color(*INK)
        self.set_y(MARGIN_TOP)

    def footer(self):
        if not self._chrome or self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font(MONO, "", 7.5)
        self.set_text_color(*GREY_MID)
        self.set_char_spacing(1.0)
        self.cell(0, 8, f"{self.page_no()}", align="C")
        self.set_char_spacing(0)
        self.set_text_color(*INK)

    # ------------------------------------------------------------------ #
    # Primitives                                                          #
    # ------------------------------------------------------------------ #
    def _mono(self, text, size, color, align="C", spacing=1.6, h=5):
        self.set_font(MONO, "", size)
        self.set_text_color(*color)
        self.set_char_spacing(spacing)
        self.multi_cell(0, h, text, align=align, new_x="LMARGIN", new_y="NEXT")
        self.set_char_spacing(0)
        self.set_text_color(*INK)

    def rule(self, frac=0.16, color=CRIMSON, thickness=0.5, gap_above=3, gap_below=3):
        self.ln(gap_above)
        w = self.content_width * frac
        x0 = (self.w - w) / 2
        y = self.get_y()
        self.set_draw_color(*color)
        self.set_line_width(thickness)
        self.line(x0, y, x0 + w, y)
        self.set_draw_color(0)
        self.ln(gap_below)

    def ornament(self, gap_above=4, gap_below=4, color=CRIMSON, size=15):
        self.ln(gap_above)
        self.set_font(ORN, "", size)
        self.set_text_color(*color)
        self.cell(0, 6, ORNAMENT, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.ln(gap_below)

    # ------------------------------------------------------------------ #
    # Cover                                                               #
    # ------------------------------------------------------------------ #
    def cover(self, kicker, title, subtitle, meta_lines):
        self._chrome = False
        self.add_page()
        self.ln(24)
        self._mono(kicker, 8.5, CRIMSON, spacing=2.4, h=5)
        self.ln(10)
        # Title — Fraunces, oxblood, large and centered (wraps if long).
        self.set_font(FRAUNCES, "", _fit_title_size(self, title))
        self.set_text_color(*OXBLOOD)
        self.multi_cell(0, _title_leading(self, title), title, align="C",
                        new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.ln(3)
        if subtitle:
            self.set_font(NEWS, "I", 15)
            self.set_text_color(*GREY)
            self.multi_cell(0, 8, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*INK)
        self.ornament(gap_above=8, gap_below=8)
        for line in meta_lines:
            self._mono(line, 8, GREY_MID, spacing=1.4, h=5)
        self._chrome = True

    # ------------------------------------------------------------------ #
    # Sections & pieces                                                  #
    # ------------------------------------------------------------------ #
    def section_divider(self, label, name, lead=None):
        self.add_page()
        self.ln(6)
        self._mono(f"§   {label}", 9, CRIMSON, align="L", spacing=2.0, h=6)
        self.ln(2)
        self.set_font(FRAUNCES, "", 34)
        self.set_text_color(*INK_TRUE)
        self.multi_cell(0, 15, name, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        if lead:
            self.ln(1)
            self.set_font(NEWS, "I", 11.5)
            self.set_text_color(*GREY)
            self.multi_cell(0, 6.4, lead, new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*INK)
        self.rule(frac=0.16, gap_above=5, gap_below=6)

    def piece_heading(self, title, meta=None):
        self.set_font(FRAUNCES, "", 21)
        self.set_text_color(*INK_TRUE)
        self.multi_cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        if meta:
            self.ln(0.5)
            self._mono(meta, 8, GREY_MID, align="L", spacing=1.2, h=5)
        self.ln(2.5)

    def heading(self, text, level):
        self.ln(2)
        size = {2: 16, 3: 13}.get(level, 12)
        self.set_font(FRAUNCES, "", size)
        self.set_text_color(*INK_TRUE)
        self.multi_cell(0, size * 0.5, text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.ln(1.5)

    def lead_in(self, text):
        self.set_font(NEWS, "I", 10.5)
        self.set_text_color(*GREY)
        self.multi_cell(0, 6, _inline(text), markdown=True,
                        new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.ln(1)

    def body(self, text):
        self.set_font(NEWS, "", 11.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 6.6, _inline(text), markdown=True, align="J",
                        new_x="LMARGIN", new_y="NEXT")
        self.ln(2.2)

    def pull_quote(self, text):
        self.set_font(NEWS, "", 13)
        self.set_text_color(*INK)
        left = self.l_margin
        self.set_left_margin(left + 7)
        self.set_x(left + 7)
        self.multi_cell(0, 7, _inline(text), markdown=True,
                        new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(left)
        self.ln(1.5)

    def citation(self, text):
        self._mono(text, 8, GREY_MID, align="L", spacing=0.8, h=5)
        self.ln(2)

    def list_item(self, text, marker):
        self.set_font(NEWS, "", 11.5)
        self.set_text_color(*INK)
        left = self.l_margin
        self.set_x(left + 3)
        self.set_text_color(*CRIMSON)
        self.cell(6, 6.6, marker)
        self.set_text_color(*INK)
        self.set_left_margin(left + 9)
        self.set_x(left + 9)
        self.multi_cell(0, 6.6, _inline(text), markdown=True,
                        new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(left)

    def verse(self, lines):
        self.set_font(NEWS, "", 12)
        self.set_text_color(*INK)
        for ln in lines:
            self.multi_cell(0, 6.6, _inline(ln), markdown=True,
                            new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def code_block(self, lines):
        self.set_font(MONO, "", 9)
        self.set_fill_color(245, 245, 246)
        self.set_text_color(*INK)
        for ln in lines:
            self.multi_cell(0, 5, ln or " ", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def _title_leading(pdf, title) -> float:
    return _fit_title_size(pdf, title) * 0.46


def _fit_title_size(pdf, title) -> float:
    """Scale a cover title down until the longest word fits the text column."""
    size = 58.0
    longest = max(title.split(), key=len) if title.split() else title
    pdf.set_font(FRAUNCES, "", size)
    while size > 26 and pdf.get_string_width(longest) > pdf.content_width:
        size -= 2
        pdf.set_font(FRAUNCES, "", size)
    return size


import re

_SPANS_RE = re.compile(r"\x00(\d+)\x00")


def _inline(text: str) -> str:
    """Translate standard inline Markdown emphasis to fpdf2's marker dialect.

    fpdf2 uses ** for bold and __ for italics; standard Markdown uses * or _
    for italics. Tokenise so the two never reprocess each other.
    """
    spans: list[tuple[str, str]] = []

    def stash(kind):
        def repl(m):
            spans.append((kind, m.group(1)))
            return f"\x00{len(spans) - 1}\x00"
        return repl

    text = re.sub(r"`([^`]+)`", lambda m: m.group(1), text)
    text = re.sub(r"\*\*(.+?)\*\*", stash("b"), text)
    text = re.sub(r"(?<!_)__(.+?)__(?!_)", stash("b"), text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", stash("i"), text)
    text = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", stash("i"), text)

    def restore(m):
        kind, inner = spans[int(m.group(1))]
        return f"**{inner}**" if kind == "b" else f"__{inner}__"

    return _SPANS_RE.sub(restore, text)
