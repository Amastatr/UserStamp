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
FRAUNCES = "Fraunces"   # display serif (Quarry / individual)
CORMORANT = "Cormorant"  # display serif (Curriculum / academic)
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
        self.display = FRAUNCES  # display face; set CORMORANT for the academic book

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
        self.add_font(CORMORANT, "", f + "/Cormorant-SemiBold.ttf")
        self.add_font(CORMORANT, "B", f + "/Cormorant-SemiBold.ttf")
        self.add_font(CORMORANT, "I", f + "/Cormorant-MediumItalic.ttf")

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
        self.set_font(self.display, "", _fit_title_size(self, title))
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
        self.set_font(self.display, "", 34)
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
        self.set_font(self.display, "", 21)
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
        self.set_font(self.display, "", size)
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

    # ------------------------------------------------------------------ #
    # The Curriculum (academic) — transcript-shaped frame                #
    # ------------------------------------------------------------------ #
    SLOT_INDENT = 22.0  # mm; aligns deposits/slots under the course title

    def _need(self, space):
        """Page-break before a block that should not be split near the foot."""
        if self.get_y() + space > self.h - self.b_margin:
            self.add_page()

    def masthead(self, rail, eyebrow, title, subtitle, byline):
        self._chrome = False
        self.add_page()
        # Top rail, dark rule beneath.
        self.set_font(MONO, "", 7.5)
        self.set_text_color(80, 84, 88)
        self.set_char_spacing(1.2)
        self.cell(self.content_width / 2, 5, rail[0].upper(), align="L")
        self.cell(self.content_width / 2, 5, rail[1].upper(), align="R")
        self.set_char_spacing(0)
        self.ln(6.5)
        self._dark_rule()
        self.ln(11)
        # Eyebrow.
        self._mono(eyebrow, 8.5, CRIMSON, align="L", spacing=2.6, h=5)
        self.ln(4)
        # Title — big, left, with a crimson period.
        self._masthead_title(title)
        self.ln(2)
        if subtitle:
            self.set_font(CORMORANT, "I", 19)
            self.set_text_color(*GREY)
            self.multi_cell(0, 8.5, subtitle, new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*INK)
        self.ln(3)
        if byline:
            self._mono(byline, 8, GREY_LT, align="L", spacing=1.2, h=5)
        self.ln(5)
        self._dark_rule()
        self.ln(7)
        self._chrome = True

    def _masthead_title(self, title):
        size = 76.0
        self.set_font(CORMORANT, "", size)
        while size > 34 and self.get_string_width(title + ".") > self.content_width:
            size -= 2
            self.set_font(CORMORANT, "", size)
        y = self.get_y()
        self.set_text_color(*INK_TRUE)
        self.set_x(self.l_margin)
        self.cell(self.get_string_width(title), size * 0.5, title)
        self.set_text_color(*CRIMSON)
        self.cell(self.get_string_width("."), size * 0.5, ".", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.set_y(y + size * 0.5)

    def _dark_rule(self, color=(60, 63, 66), thickness=0.4):
        y = self.get_y()
        self.set_draw_color(*color)
        self.set_line_width(thickness)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.set_draw_color(0)

    def intro_paragraph(self, text, first=False):
        self.set_font(NEWS, "", 11.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 6.6, _inline(text), markdown=True, align="J",
                        new_x="LMARGIN", new_y="NEXT")
        self.ln(2.5)

    def stat_strip(self, stats):
        self.ln(3)
        n = len(stats)
        w = self.content_width / n
        h = 18.0
        x0, y0 = self.l_margin, self.get_y()
        self._need(h + 4)
        x0, y0 = self.l_margin, self.get_y()
        self.set_draw_color(60, 63, 66)
        self.set_line_width(0.4)
        self.rect(x0, y0, self.content_width, h)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        for i, st in enumerate(stats):
            x = x0 + i * w
            if i:
                self.line(x, y0, x, y0 + h)
            self.set_xy(x, y0 + 4.5)
            self.set_font(CORMORANT, "", 22)
            self.set_text_color(*INK_TRUE)
            self.cell(w, 8, st["n"], align="C")
            self.set_xy(x, y0 + 12.5)
            self.set_font(MONO, "", 6.5)
            self.set_text_color(*GREY_LT)
            self.set_char_spacing(1.2)
            self.cell(w, 4, st["k"].upper(), align="C")
            self.set_char_spacing(0)
        self.set_draw_color(0)
        self.set_y(y0 + h)
        self.ln(2)

    def institution(self, name, sub):
        self._need(26)
        self.ln(9)
        self.set_font(CORMORANT, "", 25)
        self.set_text_color(*INK_TRUE)
        self.multi_cell(0, 11, name, new_x="LMARGIN", new_y="NEXT")
        self.ln(1.5)
        self._dark_rule(color=(60, 63, 66), thickness=0.5)
        self.ln(2.5)
        if sub:
            self._mono(sub.upper(), 7.5, GREY_LT, align="L", spacing=1.3, h=5)
        self.ln(1)

    def term(self, name, note=""):
        self._need(16)
        self.ln(5)
        y = self.get_y()
        self.set_font(MONO, "", 12)
        self.set_text_color(*CRIMSON)
        self.cell(6, 6, "§")
        self.set_font(MONO, "", 10)
        self.set_text_color(*INK_TRUE)
        self.set_char_spacing(2.0)
        label = name.upper()
        self.cell(self.get_string_width(label) + 4, 6, label)
        self.set_char_spacing(0)
        if note:
            self.set_font(MONO, "", 8)
            self.set_text_color(*GREY_LT)
            self.set_char_spacing(1.0)
            self.cell(0, 6, "·  " + note.upper())
            self.set_char_spacing(0)
        self.set_text_color(*INK)
        self.set_y(y + 6)
        self.ln(2.5)

    def course(self, code, title, equiv="", inprog=False):
        self._need(14)
        indent = self.SLOT_INDENT
        y0 = self.get_y()
        right_note = "IN PROGRESS" if inprog else (equiv or "")
        note_w = 0.0
        if right_note:
            self.set_font(MONO, "", 8)
            note_w = self.get_string_width(right_note) + 3
        # Course code (left gutter).
        self.set_xy(self.l_margin, y0 + 1.5)
        self.set_font(MONO, "", 9)
        self.set_text_color(*OXBLOOD)
        self.cell(indent, 6, code)
        # Title (wraps within the column, leaving room for the right note).
        self.set_font(CORMORANT, "", 16)
        self.set_text_color(*INK_TRUE)
        title_w = self.content_width - indent - note_w
        self.set_xy(self.l_margin + indent, y0)
        self.multi_cell(title_w, 7, title, new_x="LMARGIN", new_y="NEXT")
        title_bottom = self.get_y()
        # Right note on the first line.
        if right_note:
            self.set_font(MONO, "", 8)
            self.set_text_color(*(CRIMSON if inprog else GREY_LT))
            self.set_xy(self.w - self.r_margin - note_w, y0 + 1.5)
            self.cell(note_w, 5, right_note, align="R")
        self.set_text_color(*INK)
        self.set_y(title_bottom)

    def empty_slot(self, label="essay slot · awaiting deposit"):
        indent = self.SLOT_INDENT
        self.ln(1.5)
        self._need(10)
        x = self.l_margin + indent
        w = self.content_width - indent
        y = self.get_y()
        h = 7.5
        self.set_draw_color(180, 182, 184)
        self.set_line_width(0.25)
        self.set_dash_pattern(dash=1.2, gap=1.2)
        self.rect(x, y, w, h)
        self.set_dash_pattern()
        # crimson left edge
        self.set_draw_color(*CRIMSON)
        self.set_line_width(0.6)
        self.line(x, y, x, y + h)
        self.set_draw_color(0)
        self.set_line_width(0.2)
        self.set_xy(x, y + 1.7)
        self.set_font(MONO, "", 7.5)
        self.set_text_color(*GREY_LT)
        self.set_char_spacing(1.6)
        self.cell(w, 4, label.upper(), align="C")
        self.set_char_spacing(0)
        self.set_text_color(*INK)
        self.set_y(y + h)
        self.ln(2)

    def deposits(self, items):
        indent = self.SLOT_INDENT
        self.ln(1.5)
        x = self.l_margin + indent
        w = self.content_width - indent
        for dep in items:
            self._need(16)
            top = self.get_y()
            # Title.
            self.set_xy(x + 4, top)
            self.set_font(CORMORANT, "", 13)
            self.set_text_color(*INK_TRUE)
            self.multi_cell(w - 4, 6, dep["title"], new_x="LMARGIN", new_y="NEXT")
            # Meta line (+ optional label tag and grade).
            self.set_xy(x + 4, self.get_y() + 0.5)
            self.set_font(MONO, "", 8)
            self.set_text_color(*GREY_LT)
            self.set_char_spacing(1.0)
            label = dep.get("label", "")
            meta_txt = "  ·  ".join(
                s for s in [dep.get("meta", ""), f"[{label}]" if label else ""] if s
            )
            if meta_txt:
                self.cell(self.get_string_width(meta_txt.upper()) + 2, 5, meta_txt.upper())
            if dep.get("grade"):
                self.set_text_color(*CRIMSON)
                self.cell(0, 5, "   " + dep["grade"])
            self.set_char_spacing(0)
            self.set_text_color(*INK)
            self.ln(5)
            if dep.get("note"):
                self.set_xy(x + 4, self.get_y())
                self._mono(dep["note"].upper(), 7, GREY_LT, align="L", spacing=0.8, h=4)
            # crimson left edge for this deposit (survives page breaks).
            bottom = self.get_y()
            self.set_draw_color(*CRIMSON)
            self.set_line_width(0.6)
            self.line(x, top, x, bottom)
            self.set_draw_color(0)
            self.set_line_width(0.2)
            self.ln(2.5)
        self.ln(0.5)

    def colophon(self, kick, h2, paras, footer_lines):
        self._need(60)
        self.ln(12)
        self._dark_rule(color=(60, 63, 66), thickness=0.3)
        self.ln(4)
        self._mono(kick.upper(), 8.5, CRIMSON, align="L", spacing=2.4, h=5)
        self.ln(2)
        self.set_font(CORMORANT, "", 22)
        self.set_text_color(*INK_TRUE)
        self.multi_cell(0, 10, h2, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.ln(2)
        for p in paras:
            self.set_font(NEWS, "", 11)
            self.set_text_color(*INK)
            self.multi_cell(0, 6.4, _inline(p), markdown=True, align="J",
                            new_x="LMARGIN", new_y="NEXT")
            self.ln(1.5)
        self.ornament(gap_above=8, gap_below=6)
        for line in footer_lines:
            self._mono(line.upper(), 7, GREY_LT, align="C", spacing=1.2, h=4)


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def _title_leading(pdf, title) -> float:
    return _fit_title_size(pdf, title) * 0.46


def _fit_title_size(pdf, title) -> float:
    """Scale a cover title down until the longest word fits the text column."""
    size = 58.0
    longest = max(title.split(), key=len) if title.split() else title
    pdf.set_font(pdf.display, "", size)
    while size > 26 and pdf.get_string_width(longest) > pdf.content_width:
        size -= 2
        pdf.set_font(pdf.display, "", size)
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
