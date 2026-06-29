# The Lexicon — writings → PDF dossiers

A version-controlled system that compiles your writings into **chronological PDF
books in the Haus style** — the editorial look of *The Quarry*: three typefaces
(Fraunces display, Newsreader text, JetBrains Mono labels) over an oxblood /
crimson accent palette, with a cover, § section dividers, and a running header.

There are three books, each built independently:

| Book | Collects | Output |
|------|----------|--------|
| `individual` | personal writing | `output/individual.pdf` |
| `academic`   | scholarship and inquiry | `output/academic.pdf` |
| `published`  | released work, by publication date | `output/published.pdf` |

## Layout

```
config.json                                   books, titles, author, imprint
assets/fonts/                                 bundled OFL fonts (Fraunces, etc.)
tools/haus_style.py                           the typographic engine
tools/build_pdfs.py                           the builder
writings/<book>/<NN-section>/YYYY-MM-DD-slug.md   your writings
output/<book>.pdf                             the built dossiers
```

- A **book** is a top-level folder under `writings/` named in `config.json`.
- A **section** is a subfolder (becomes a `§ SECTION` divider). Prefix it with a
  number to order it, e.g. `01-philosophy`, `02-history`.
- A **piece** is one Markdown file. The `YYYY-MM-DD` filename prefix sets its
  place in the chronological order.

## Adding a piece

1. Drop a Markdown file in the right section, dated first in the name:
   `writings/academic/01-philosophy/2026-02-10-on-time-and-entropy.md`
2. Optional front matter (anything omitted is inferred):

   ```markdown
   ---
   title: On Time and Entropy
   date: 2026-02-10
   format: verse        # preserve line breaks (automatic for a "poetry" section)
   ---

   Your writing in Markdown…
   ```

3. Rebuild.

### Naming a section

Add a `_section.md` to a section folder to set its title, descriptive lead, and
order:

```markdown
---
title: Philosophy
lead: Arguments made carefully, with their premises on the page.
order: 1
---
```

## The academic book — *The Curriculum*

The `academic` book is special: instead of section folders, it is driven by a
single data file, **`writings/academic/curriculum.json`**, which holds the whole
transcript — institutions → terms → courses → essay *slots*. It renders as *The
Curriculum*: every course in the order it was taken, each with a slot that is
either empty (`essay slot · awaiting deposit`) or filled with one or more
**deposits**. Its display face is Cormorant Garamond, matching the reference.

### Depositing an essay

Find the course in `curriculum.json` and add an object to its `deposits` array:

```json
{
  "title": "The Destitution of Empire",
  "label": "final paper",          // optional tag, shown as [FINAL PAPER]
  "meta": "Hardy · Schreiner · Carlyle",
  "grade": "100",                  // optional, shown in crimson
  "note": "+ draft and outline on file"   // optional
}
```

Rebuild and the slot fills. Because the JSON is the single source of truth, the
frame and the compiled PDF always stay in sync — the slots fill as the writing
is deposited, exactly as the document describes.

## Building

```bash
bash tools/bootstrap.sh              # one-time per environment: installs fpdf2
python3 tools/build_pdfs.py          # build every book
python3 tools/build_pdfs.py academic # build just one book
```

Commit the regenerated files in `output/` — this environment is ephemeral and
only committed files survive.

## Formatting inside a piece

Standard Markdown: `## headings` (set in Fraunces), `**bold**`, `*italic*`,
`> pull quotes` (rendered at primary size, the way the dossier treats
quotations), `- bullet` / `1. numbered` lists, `---` rules, and ```` ``` ````
code blocks. Prose is justified in Newsreader; **verse** keeps your line breaks.

## Fonts

The three families are open-source (SIL OFL) and bundled as static cuts in
`assets/fonts/`, so builds are reproducible with no network access. Licenses are
alongside them. Fraunces, Newsreader, and JetBrains Mono are the type system of
the Haus style.
