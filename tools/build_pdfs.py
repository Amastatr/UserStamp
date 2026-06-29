#!/usr/bin/env python3
"""Build chronological PDF collections from Markdown writings.

Layout this script expects:

    writings/<field>/YYYY-MM-DD-slug.md

Each Markdown file is one piece of writing. Date and title come from an
optional YAML-ish front-matter block, falling back to the filename and the
first heading. Output:

    output/<field>.pdf     one chronological PDF per field
    output/all-writings.pdf  every field, each as its own chronological run

Run:  python3 tools/build_pdfs.py
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
WRITINGS_DIR = ROOT / "writings"
OUTPUT_DIR = ROOT / "output"
CONFIG_PATH = ROOT / "config.json"

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")
FONT_FILES = {
    "": FONT_DIR / "LiberationSerif-Regular.ttf",
    "B": FONT_DIR / "LiberationSerif-Bold.ttf",
    "I": FONT_DIR / "LiberationSerif-Italic.ttf",
    "BI": FONT_DIR / "LiberationSerif-BoldItalic.ttf",
}
MONO_FILES = {
    "": FONT_DIR / "LiberationMono-Regular.ttf",
    "B": FONT_DIR / "LiberationMono-Bold.ttf",
}

SERIF = "Serif"
MONO = "Mono"

DATE_IN_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})")


# --------------------------------------------------------------------------- #
# Parsing                                                                      #
# --------------------------------------------------------------------------- #
@dataclass
class Piece:
    field: str
    date: dt.date
    title: str
    body: str  # markdown, front-matter stripped
    path: Path
    verse: bool = False  # preserve single-line breaks (poetry, lyrics, etc.)


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Pull an optional leading `---`-delimited key: value block."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return {}, text
    meta: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return meta, "\n".join(lines[i + 1 :]).lstrip("\n")
        if ":" in lines[i]:
            key, _, val = lines[i].partition(":")
            meta[key.strip().lower()] = val.strip()
    return {}, text  # no closing fence -> treat whole thing as body


def first_heading(body: str) -> str | None:
    for line in body.splitlines():
        m = re.match(r"^#\s+(.+)", line.strip())
        if m:
            return m.group(1).strip()
    return None


def load_piece(path: Path, field: str) -> Piece:
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(raw)

    # Date: front matter wins, else the filename prefix, else file mtime.
    date: dt.date | None = None
    if "date" in meta:
        date = _parse_date(meta["date"])
    if date is None:
        m = DATE_IN_NAME.match(path.name)
        if m:
            date = _parse_date(m.group(1))
    if date is None:
        date = dt.date.fromtimestamp(path.stat().st_mtime)

    title = meta.get("title") or first_heading(body) or _slug_to_title(path.stem)
    # If the title came from a leading `# heading`, drop that line from the body
    # so it is not rendered twice.
    body = _strip_leading_title(body, title)
    fld = meta.get("field", field)
    fmt = meta.get("format", meta.get("type", "")).lower()
    verse = fmt in ("verse", "poem", "poetry") or fld.lower() in ("poetry", "verse", "lyrics")
    return Piece(field=fld, date=date, title=title, body=body, path=path, verse=verse)


def _parse_date(s: str) -> dt.date | None:
    s = s.strip().strip('"').strip("'")
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %B %Y", "%B %d, %Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _slug_to_title(stem: str) -> str:
    stem = DATE_IN_NAME.sub("", stem).lstrip("-_ ")
    return stem.replace("-", " ").replace("_", " ").strip().title() or stem


def _strip_leading_title(body: str, title: str) -> str:
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if re.match(r"^#\s+", line.strip()):
            return "\n".join(lines[i + 1 :]).lstrip("\n")
        break
    return body


# --------------------------------------------------------------------------- #
# Inline markdown -> fpdf2 markdown markers                                    #
# --------------------------------------------------------------------------- #
def to_fpdf_inline(text: str) -> str:
    """Translate standard inline Markdown to fpdf2's marker dialect.

    fpdf2 uses ** for bold, __ for italics. Standard Markdown uses ** / __ for
    bold and * / _ for italics, so we normalise to fpdf2's expectations.
    """
    # Tokenise into placeholders so emphasis markers never reprocess each other.
    spans: list[tuple[str, str]] = []  # (kind, inner)

    def stash(kind: str):
        def repl(m: re.Match) -> str:
            spans.append((kind, m.group(1)))
            return f"\x00{len(spans) - 1}\x00"
        return repl

    text = re.sub(r"`([^`]+)`", lambda m: m.group(1), text)  # inline code -> plain
    text = re.sub(r"\*\*(.+?)\*\*", stash("b"), text)        # **bold**
    text = re.sub(r"(?<!_)__(.+?)__(?!_)", stash("b"), text)  # __strong__
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", stash("i"), text)  # *italic*
    text = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", stash("i"), text)    # _italic_

    def restore(m: re.Match) -> str:
        kind, inner = spans[int(m.group(1))]
        return f"**{inner}**" if kind == "b" else f"__{inner}__"

    return re.sub(r"\x00(\d+)\x00", restore, text)


# --------------------------------------------------------------------------- #
# PDF rendering                                                                #
# --------------------------------------------------------------------------- #
class Book(FPDF):
    def __init__(self, collection_title: str, author: str):
        super().__init__(format="A4")
        self.collection_title = collection_title
        self.author = author
        self.set_title(collection_title)
        self.set_author(author)
        self.set_margins(left=22, top=20, right=22)
        self.set_auto_page_break(auto=True, margin=20)
        for style, fpath in FONT_FILES.items():
            self.add_font(SERIF, style, str(fpath))
        for style, fpath in MONO_FILES.items():
            self.add_font(MONO, style, str(fpath))
        self.set_font(SERIF, size=11)
        self._running_header = ""

    # Footer: centered page number.
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font(SERIF, "I", 9)
        self.set_text_color(120)
        self.cell(0, 10, str(self.page_no()), align="C")
        self.set_text_color(0)

    def header(self):
        if self.page_no() == 1 or not self._running_header:
            return
        self.set_font(SERIF, "I", 9)
        self.set_text_color(140)
        self.cell(0, 8, self._running_header, align="R")
        self.set_text_color(0)
        self.ln(10)

    # ----- block elements ------------------------------------------------- #
    def body_paragraph(self, text: str):
        self.set_font(SERIF, "", 11.5)
        self.set_text_color(0)
        self.multi_cell(
            0, 6.6, to_fpdf_inline(text), markdown=True, align="J",
            new_x="LMARGIN", new_y="NEXT",
        )
        self.ln(2)

    def heading(self, text: str, level: int):
        self.ln(2)
        size = {2: 15, 3: 12.5}.get(level, 11.5)
        self.set_font(SERIF, "B", size)
        self.set_text_color(0)
        self.multi_cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def blockquote(self, text: str):
        self.set_font(SERIF, "I", 11)
        self.set_text_color(70)
        left = self.l_margin
        self.set_left_margin(left + 8)
        self.set_x(left + 8)
        self.multi_cell(0, 6.4, to_fpdf_inline(text), markdown=True, align="L",
                        new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(left)
        self.set_text_color(0)
        self.ln(2)

    def list_item(self, text: str, marker: str):
        self.set_font(SERIF, "", 11.5)
        self.set_text_color(0)
        left = self.l_margin
        self.set_x(left + 4)
        self.cell(6, 6.6, marker)
        self.set_left_margin(left + 10)
        self.set_x(left + 10)
        self.multi_cell(0, 6.6, to_fpdf_inline(text), markdown=True, align="L",
                        new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(left)

    def code_block(self, lines: list[str]):
        self.set_font(MONO, "", 9.5)
        self.set_fill_color(244, 244, 244)
        self.set_text_color(30)
        for ln in lines:
            self.multi_cell(0, 5, ln if ln else " ", fill=True,
                            new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0)
        self.ln(2)

    def verse_stanza(self, lines: list[str]):
        """Render verse: one source line per rendered line, no justification."""
        self.set_font(SERIF, "", 11.5)
        self.set_text_color(0)
        for ln in lines:
            self.multi_cell(0, 6.4, to_fpdf_inline(ln), markdown=True, align="L",
                            new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def rule(self):
        self.ln(1)
        y = self.get_y()
        self.set_draw_color(200)
        self.line(self.l_margin + 30, y, self.w - self.r_margin - 30, y)
        self.set_draw_color(0)
        self.ln(4)


def render_markdown(pdf: Book, body: str, verse: bool = False):
    """Render a (front-matter-stripped) Markdown body block by block."""
    lines = body.split("\n")
    i = 0
    para: list[str] = []

    def flush_para():
        nonlocal para
        if para:
            if verse:
                pdf.verse_stanza([s.rstrip() for s in para])
            else:
                pdf.body_paragraph(" ".join(s.strip() for s in para))
            para = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_para()
            block: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            pdf.code_block(block)
            i += 1
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            flush_para()
            pdf.rule()
            i += 1
            continue

        m = re.match(r"^(#{2,6})\s+(.+)", stripped)
        if m:
            flush_para()
            pdf.heading(m.group(2).strip(), len(m.group(1)))
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            quote = [re.sub(r"^>\s?", "", stripped)]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            pdf.blockquote(" ".join(quote))
            continue

        m = re.match(r"^[-*+]\s+(.+)", stripped)
        if m:
            flush_para()
            pdf.list_item(m.group(1).strip(), "•")
            i += 1
            continue

        m = re.match(r"^(\d+)[.)]\s+(.+)", stripped)
        if m:
            flush_para()
            pdf.list_item(m.group(2).strip(), f"{m.group(1)}.")
            i += 1
            continue

        para.append(line)
        i += 1

    flush_para()


def render_piece(pdf: Book, piece: Piece, section_level: int = 0):
    pdf.add_page()
    # Title block.
    pdf.set_font(SERIF, "B", 20)
    pdf.set_text_color(0)
    pdf.multi_cell(0, 9.5, piece.title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(SERIF, "I", 10.5)
    pdf.set_text_color(120)
    meta = f"{piece.field.title()}  ·  {piece.date.strftime('%B %-d, %Y')}"
    pdf.multi_cell(0, 6, meta, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0)
    pdf.ln(4)
    pdf.start_section(f"{piece.title} ({piece.date.isoformat()})", level=section_level)
    render_markdown(pdf, piece.body, verse=piece.verse)


def cover_page(pdf: Book, title: str, subtitle: str, count: int, span: str):
    pdf.add_page()
    pdf.ln(60)
    pdf.set_font(SERIF, "B", 30)
    pdf.multi_cell(0, 14, title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    if subtitle:
        pdf.set_font(SERIF, "I", 14)
        pdf.set_text_color(90)
        pdf.multi_cell(0, 9, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0)
    pdf.ln(8)
    pdf.set_font(SERIF, "", 12)
    pdf.set_text_color(110)
    detail = f"{count} piece{'s' if count != 1 else ''}"
    if span:
        detail += f"  ·  {span}"
    pdf.multi_cell(0, 8, detail, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0)


def span_label(pieces: list[Piece]) -> str:
    if not pieces:
        return ""
    lo, hi = pieces[0].date, pieces[-1].date
    if lo == hi:
        return lo.strftime("%B %Y")
    if lo.year == hi.year:
        return f"{lo.strftime('%B')}–{hi.strftime('%B %Y')}"
    return f"{lo.strftime('%b %Y')}–{hi.strftime('%b %Y')}"


# --------------------------------------------------------------------------- #
# Build orchestration                                                         #
# --------------------------------------------------------------------------- #
def collect() -> dict[str, list[Piece]]:
    fields: dict[str, list[Piece]] = {}
    if not WRITINGS_DIR.exists():
        return fields
    for field_dir in sorted(p for p in WRITINGS_DIR.iterdir() if p.is_dir()):
        pieces = [
            load_piece(f, field_dir.name)
            for f in field_dir.glob("*.md")
            if f.name.lower() != "readme.md"
        ]
        if pieces:
            pieces.sort(key=lambda p: (p.date, p.path.name))
            fields[field_dir.name] = pieces
    return fields


def build_field_pdf(field: str, pieces: list[Piece], cfg: dict) -> Path:
    pdf = Book(f"{field.title()} — {cfg['collection_title']}", cfg["author"])
    pdf._running_header = f"{field.title()}"
    cover_page(pdf, field.title(), cfg["author"], len(pieces), span_label(pieces))
    pdf._toc_reserved = _toc_pages(len(pieces))
    pdf.insert_toc_placeholder(render_toc, pages=pdf._toc_reserved)
    for piece in pieces:
        render_piece(pdf, piece, section_level=0)
    out = OUTPUT_DIR / f"{field}.pdf"
    pdf.output(str(out))
    return out


def build_combined_pdf(fields: dict[str, list[Piece]], cfg: dict) -> Path:
    pdf = Book(cfg["collection_title"], cfg["author"])
    pdf._running_header = cfg["collection_title"]
    total = sum(len(v) for v in fields.values())
    all_pieces = [p for v in fields.values() for p in v]
    all_pieces.sort(key=lambda p: p.date)
    cover_page(pdf, cfg["collection_title"], cfg["author"], total, span_label(all_pieces))
    pdf._toc_reserved = _toc_pages(total + len(fields))
    pdf.insert_toc_placeholder(render_toc, pages=pdf._toc_reserved)
    for field, pieces in fields.items():
        # Field divider page.
        pdf.add_page()
        pdf.ln(40)
        pdf.set_font(SERIF, "B", 24)
        pdf.multi_cell(0, 12, field.title(), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(SERIF, "I", 11)
        pdf.set_text_color(120)
        pdf.multi_cell(0, 7, span_label(pieces), align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0)
        pdf.start_section(field.title(), level=0)
        for piece in pieces:
            render_piece(pdf, piece, section_level=1)
    out = OUTPUT_DIR / "all-writings.pdf"
    pdf.output(str(out))
    return out


def _toc_pages(entries: int) -> int:
    # Conservative upper bound (assume ~30 entries/page); render_toc pads to fit.
    return max(1, -(-entries // 30))


def render_toc(pdf: Book, outline):
    # The placeholder pages can inherit a shifted margin/cursor from whatever
    # was rendered last, so restore a known-good layout first.
    pdf.set_left_margin(22)
    pdf.set_right_margin(22)
    pdf.set_x(pdf.l_margin)
    start_page = pdf.page_no()
    pdf.set_font(SERIF, "B", 18)
    pdf.set_text_color(0)
    pdf.cell(0, 11, "Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    page_col = 14  # width reserved on the right for the page number
    for section in outline:
        indent = section.level * 6
        pdf.set_font(SERIF, "B" if section.level == 0 else "", 11)
        pdf.set_text_color(0)
        page = str(section.page_number)
        link = pdf.add_link(page=section.page_number)
        y = pdf.get_y()
        # Title (truncated to leave room for the page number column).
        label_w = pdf.w - pdf.l_margin - pdf.r_margin - indent - page_col
        pdf.set_x(pdf.l_margin + indent)
        pdf.cell(label_w, 7, _truncate(pdf, section.name, label_w), link=link)
        # Page number, right-aligned.
        pdf.set_font(SERIF, "", 10)
        pdf.set_text_color(120)
        pdf.set_x(pdf.w - pdf.r_margin - page_col)
        pdf.cell(page_col, 7, page, align="R", link=link, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0)

    # Pad with blank pages so the rendered ToC spans exactly the reserved count.
    reserved = getattr(pdf, "_toc_reserved", 1)
    while pdf.page_no() - start_page + 1 < reserved:
        pdf.add_page()


def _truncate(pdf: Book, text: str, max_w: float) -> str:
    if pdf.get_string_width(text) <= max_w:
        return text
    ell = "…"
    while text and pdf.get_string_width(text + ell) > max_w:
        text = text[:-1]
    return text + ell


def main() -> int:
    cfg = {"author": "", "collection_title": "Collected Writings"}
    if CONFIG_PATH.exists():
        cfg.update({k: v for k, v in json.loads(CONFIG_PATH.read_text()).items() if v})
    OUTPUT_DIR.mkdir(exist_ok=True)

    fields = collect()
    if not fields:
        print("No writings found under writings/<field>/*.md — nothing to build.")
        return 0

    built = []
    for field, pieces in fields.items():
        built.append(build_field_pdf(field, pieces, cfg))
        print(f"  {field}: {len(pieces)} piece(s) -> output/{field}.pdf")

    if len(fields) > 1:
        built.append(build_combined_pdf(fields, cfg))
        print(f"  combined: {sum(len(v) for v in fields.values())} piece(s) -> output/all-writings.pdf")

    print(f"Built {len(built)} PDF(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
