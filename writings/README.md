# writings/

Your writings, organised as **books → sections → pieces**:

```
writings/<book>/<NN-section>/YYYY-MM-DD-slug.md
```

- Top-level folders (`individual`, `academic`, `published`) are **books**, each
  declared in [`../config.json`](../config.json) and built into its own PDF.
- Subfolders are **sections** (`§ SECTION` dividers); a numeric prefix sets
  their order. Add a `_section.md` to give a section a title and lead.
- Each Markdown file is one **piece**; the `YYYY-MM-DD` prefix sets its place in
  the chronological sequence.

See [`../WRITINGS.md`](../WRITINGS.md) for the full guide. `README.md` and
`_section.md` files are not treated as pieces.
