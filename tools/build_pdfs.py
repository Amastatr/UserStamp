#!/usr/bin/env python3
"""Build chronological PDF dossiers from Markdown writings, in the Haus style.

Each *book* (individual / academic / published / …) is a folder of *sections*,
each section a folder of Markdown *pieces*:

    writings/<book>/<NN-section>/YYYY-MM-DD-slug.md

The book, its title and metadata are declared in config.json. Output:

    output/<book>.pdf

Run:  python3 tools/build_pdfs.py            # build every book in config
      python3 tools/build_pdfs.py academic  # build one book
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import haus_style as hs
from haus_style import HausBook

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
CONFIG_PATH = ROOT / "config.json"

DATE_IN_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})")
ORDER_PREFIX = re.compile(r"^(\d+)[-_.]\s*")
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]


# --------------------------------------------------------------------------- #
# Model                                                                       #
# --------------------------------------------------------------------------- #
@dataclass
class Piece:
    section: str
    date: dt.date
    title: str
    body: str
    path: Path
    verse: bool = False


@dataclass
class Section:
    name: str            # display name
    order: int
    lead: str
    pieces: list[Piece] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Markdown parsing                                                            #
# --------------------------------------------------------------------------- #
def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return {}, text
    meta: dict[str, str] = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return meta, "\n".join(lines[i + 1:]).lstrip("\n")
        if ":" in lines[i]:
            k, _, v = lines[i].partition(":")
            meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return {}, text


def _parse_date(s: str) -> dt.date | None:
    s = s.strip().strip('"').strip("'")
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %B %Y", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _first_heading(body: str) -> str | None:
    for line in body.splitlines():
        m = re.match(r"^#\s+(.+)", line.strip())
        if m:
            return m.group(1).strip()
    return None


def _slug_to_title(stem: str) -> str:
    stem = DATE_IN_NAME.sub("", stem).lstrip("-_ ")
    return stem.replace("-", " ").replace("_", " ").strip().title() or stem


def _strip_leading_title(body: str) -> str:
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if re.match(r"^#\s+", line.strip()):
            return "\n".join(lines[i + 1:]).lstrip("\n")
        break
    return body


def load_piece(path: Path, section_name: str) -> Piece:
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(raw)
    date = _parse_date(meta.get("date", "")) if "date" in meta else None
    if date is None:
        m = DATE_IN_NAME.match(path.name)
        date = _parse_date(m.group(1)) if m else None
    if date is None:
        date = dt.date.fromtimestamp(path.stat().st_mtime)
    title = meta.get("title") or _first_heading(body) or _slug_to_title(path.stem)
    body = _strip_leading_title(body)
    fmt = meta.get("format", meta.get("type", "")).lower()
    verse = fmt in ("verse", "poem", "poetry") or section_name.lower() in ("poetry", "verse", "lyrics")
    return Piece(section=section_name, date=date, title=title, body=body, path=path, verse=verse)


def load_section(folder: Path) -> Section | None:
    raw_name = folder.name
    m = ORDER_PREFIX.match(raw_name)
    order = int(m.group(1)) if m else 999
    display = ORDER_PREFIX.sub("", raw_name).replace("-", " ").replace("_", " ").strip().title()
    lead = ""
    meta_file = folder / "_section.md"
    if meta_file.exists():
        meta, _ = parse_front_matter(meta_file.read_text(encoding="utf-8"))
        display = meta.get("title", display)
        lead = meta.get("lead", "")
        if "order" in meta:
            try:
                order = int(meta["order"])
            except ValueError:
                pass
    pieces = [
        load_piece(f, display)
        for f in folder.glob("*.md")
        if f.name.lower() not in ("readme.md", "_section.md")
    ]
    if not pieces:
        return None
    pieces.sort(key=lambda p: (p.date, p.path.name))
    return Section(name=display, order=order, lead=lead, pieces=pieces)


def collect_book(writings_dir: Path) -> list[Section]:
    if not writings_dir.exists():
        return []
    sections = []
    for folder in sorted(p for p in writings_dir.iterdir() if p.is_dir()):
        s = load_section(folder)
        if s:
            sections.append(s)
    sections.sort(key=lambda s: (s.order, s.name))
    return sections


# --------------------------------------------------------------------------- #
# Rendering                                                                   #
# --------------------------------------------------------------------------- #
def render_body(pdf: HausBook, body: str, verse: bool):
    lines = body.split("\n")
    i = 0
    para: list[str] = []

    def flush():
        nonlocal para
        if para:
            if verse:
                pdf.verse([s.rstrip() for s in para])
            else:
                pdf.body(" ".join(s.strip() for s in para))
            para = []

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if s.startswith("```"):
            flush()
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            pdf.code_block(block)
            i += 1
            continue
        if not s:
            flush()
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            flush()
            pdf.rule(frac=0.16, gap_above=2, gap_below=4)
            i += 1
            continue
        m = re.match(r"^(#{2,6})\s+(.+)", s)
        if m:
            flush()
            pdf.heading(m.group(2).strip(), len(m.group(1)))
            i += 1
            continue
        if s.startswith(">"):
            flush()
            quote = [re.sub(r"^>\s?", "", s)]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            pdf.pull_quote(" ".join(quote))
            continue
        m = re.match(r"^[-*+]\s+(.+)", s)
        if m:
            flush()
            pdf.list_item(m.group(1).strip(), "•")
            i += 1
            continue
        m = re.match(r"^(\d+)[.)]\s+(.+)", s)
        if m:
            flush()
            pdf.list_item(m.group(2).strip(), f"{m.group(1)}.")
            i += 1
            continue
        para.append(line)
        i += 1
    flush()


def span_label(pieces: list[Piece]) -> str:
    if not pieces:
        return ""
    lo, hi = min(p.date for p in pieces), max(p.date for p in pieces)
    if lo == hi:
        return lo.strftime("%B %Y")
    if lo.year == hi.year:
        return f"{lo.strftime('%B')}–{hi.strftime('%B %Y')}"
    return f"{lo.strftime('%b %Y')}–{hi.strftime('%b %Y')}"


def _fmt_date(d: dt.date) -> str:
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def build_book(key: str, book: dict, cfg: dict) -> Path | None:
    writings_dir = ROOT / book.get("writings", f"writings/{key}")
    sections = collect_book(writings_dir)
    if not sections:
        print(f"  {key}: no writings under {writings_dir.relative_to(ROOT)} — skipped")
        return None

    all_pieces = [p for s in sections for p in s.pieces]
    title = book.get("title", key.title())
    pdf = HausBook(short_title=book.get("short_title", title), organization=cfg["organization"])
    pdf.set_title(title)
    pdf.set_author(cfg.get("author", ""))

    kicker = f"{cfg['organization']}   ·   {cfg.get('imprint', '')}".strip(" ·")
    meta_lines = []
    if book.get("dossier_line"):
        meta_lines.append(book["dossier_line"].upper())
    if cfg.get("author"):
        meta_lines.append(cfg["author"].upper())
    place_year = "   ·   ".join(
        x for x in [cfg.get("place", "").upper(), _roman_year(all_pieces)] if x
    )
    if place_year:
        meta_lines.append(place_year)
    meta_lines.append(
        f"{len(all_pieces)} PIECE{'S' if len(all_pieces) != 1 else ''}"
        f"   ·   {span_label(all_pieces).upper()}"
    )
    pdf.cover(kicker, title, book.get("subtitle", ""), meta_lines)

    for idx, section in enumerate(sections):
        label = f"SECTION {ROMAN[idx]}" if idx < len(ROMAN) else f"SECTION {idx + 1}"
        pdf.section_divider(label, section.name, lead=section.lead or None)
        pdf.start_section(section.name)
        for piece in section.pieces:
            pdf.ln(2)
            pdf.piece_heading(piece.title, meta=f"{section.name}   ·   {_fmt_date(piece.date)}")
            pdf.start_section(f"{piece.title}", level=1)
            render_body(pdf, piece.body, piece.verse)
            pdf.ornament(gap_above=3, gap_below=3, color=hs.RULE, size=11)

    out = OUTPUT_DIR / f"{key}.pdf"
    pdf.output(str(out))
    print(f"  {key}: {len(sections)} section(s), {len(all_pieces)} piece(s) -> output/{key}.pdf")
    return out


def _roman_year(pieces: list[Piece]) -> str:
    if not pieces:
        return ""
    return _to_roman(max(p.date for p in pieces).year)


def _to_roman(n: int) -> str:
    vals = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
            (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
            (5, "V"), (4, "IV"), (1, "I")]
    out = []
    for v, sym in vals:
        while n >= v:
            out.append(sym)
            n -= v
    return "".join(out)


# --------------------------------------------------------------------------- #
# Entry point                                                                 #
# --------------------------------------------------------------------------- #
def main(argv: list[str]) -> int:
    if not CONFIG_PATH.exists():
        print("config.json not found.")
        return 1
    cfg = json.loads(CONFIG_PATH.read_text())
    cfg.setdefault("organization", "")
    OUTPUT_DIR.mkdir(exist_ok=True)

    books = cfg.get("books", {})
    wanted = argv or list(books)
    built = []
    for key in wanted:
        if key not in books:
            print(f"  {key}: not defined in config.books — skipped")
            continue
        out = build_book(key, books[key], cfg)
        if out:
            built.append(out)
    print(f"Built {len(built)} book(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
