# Collected Writings — PDF builder

A small, version-controlled system for gathering your writings across different
fields into **chronological PDF books** — one PDF per field, plus a combined
master PDF of everything. Add a Markdown file, rebuild, and the piece drops into
the collection in date order automatically.

## Layout

```
writings/<field>/YYYY-MM-DD-slug.md   your writings, one file per piece
config.json                            author name + collection title
tools/build_pdfs.py                    the generator
output/<field>.pdf                     one chronological PDF per field
output/all-writings.pdf                every field combined (built when >1 field)
```

A "field" is just a subfolder of `writings/` — `essays`, `poetry`, `letters`,
`notes`, whatever you like. Create a new folder to start a new field.

## Adding a piece of writing

1. Create a Markdown file under the right field folder. Name it with the date
   first so it sorts naturally, e.g. `writings/essays/2026-07-01-on-rivers.md`.
2. Optionally add a front-matter block at the top:

   ```markdown
   ---
   title: On Rivers
   date: 2026-07-01
   field: essays        # optional; defaults to the folder name
   format: verse        # optional; "verse" preserves line breaks (auto for poetry)
   ---

   Your writing in Markdown...
   ```

   Anything you omit is inferred: the **date** from the filename prefix, the
   **title** from the first `# heading` or the filename, the **field** from the
   folder.

3. Rebuild (see below). The piece is inserted in chronological order.

## Building the PDFs

```bash
bash tools/bootstrap.sh      # one-time per environment: installs fpdf2
python3 tools/build_pdfs.py  # rebuilds every PDF in output/
```

Commit the regenerated files in `output/` so the books persist — this
environment is ephemeral and only committed files survive.

## Formatting supported

Standard Markdown within a piece: `# headings`, `**bold**`, `*italic*`,
`> block quotes`, `- bullet` and `1. numbered` lists, `---` horizontal rules,
and ```` ``` ```` fenced code blocks. Prose paragraphs are justified in a serif
face; **verse** (the `poetry` field, or `format: verse`) keeps your line breaks
exactly as written.

Each field PDF and the combined PDF open with a cover page and a clickable table
of contents, with PDF bookmarks for every piece.
