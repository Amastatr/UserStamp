# CLAUDE.md · Amastatr repo

Read before editing. This repo holds two products side by side.

## What lives here

1. **The Haus front door (v20)**: `index.html`, one static page, no framework, no build step. Inline CSS and JS, self-hosted subset fonts in `assets/fonts/`, the vector emblem in `assets/emblem.svg`, the social card in `assets/og-card.png`.
2. **The UserStamp extension**: `manifest.json`, `content.js`, `background.js`, `popup.html`, `popup.js`, `icons/`. Third instrument in the AI stamps line after TimeStamp and GeoStamp. Do not move these files; the extension loads unpacked from the repo root.
3. **The archive**: `legacy/haus_about_html_19.html` is the previous site (the About exhibition, v19), preserved byte for byte. Old URLs stay alive: `haus_about_html_19.html` and `amastatr_haus_about.html` at root are redirect stubs. Never edit anything under `legacy/`; it keeps its own rules (its em dashes are historical and stay).

## Preview

```
python3 -m http.server 8000
```

Then open http://localhost:8000/. Use HTTP, not file://, or the font preloads log CORS errors.

## Design register (v20)

- Graphite atmosphere, near-black ink, crimson `#C8102E` as the working accent.
- Silver brightwork, sparingly: gradient `#C4C8CB` to `#A9ADB1` on dark grounds (the social card), darkened to `#A9ADB1` to `#7C8288` on the light page where the bright pair washes out.
- Two font families only: Newsreader (display and body, variable, roman + italic) and JetBrains Mono (labels, datelines, status lines). Latin subsets, preloaded, metric-matched fallbacks hold the layout.
- The folio sheet: the content column carries a light wash (`rgba(250,251,252,0.5)`) so ink stays legible over every depth of the fixed gradient. Do not remove it.

## The emblem

`assets/emblem.svg`, original mark: a drafted gable A. Two ink legs crossing in an X overshoot at the apex, a silver datum line through as the crossbar, a crimson registration tick at baseline right. Four strokes, one module. The inline copy in `index.html` animates: strokes draw in order (left leg, right leg, datum, tick stamped hard), about two seconds, once per session via `sessionStorage`, skipped entirely under `prefers-reduced-motion`, never blocking text. The gradient uses `gradientUnits="userSpaceOnUse"`; a bounding-box gradient is invisible on a horizontal line, so do not "simplify" that.

## Copy rules (hard, for all new text including comments, alt text, aria labels)

- Never use an em dash anywhere. Use middots, colons, or restructure.
- Never use the words "genuinely", "honestly", "actually".
- Never use "forgive", "sacred", "cathedral", or religious vocabulary for the work.
- Prose over bullets in page copy. No filler adverbs. No manifesto cadence beyond the Doctrine.
- Do not address the owner by name in page copy. He writes his own founder lines.
- Calibration over flattery: leave version and status claims as they are unless verified.
- The armor vow is bounded: armor-only is an innovation direction, not a renunciation of weapons as objects or of the defense industry. "The vow is on the drafting table, not in the gun safe." Do not flatten this into pacifism and do not scrub force from the page.
- Every prose block in `index.html` is marked with an HTML comment `COPY:DRAFT` until the owner confirms it. Keep the markers until told to remove them.

## Ventures are data

The Register renders from the `VENTURES` array at the bottom of `index.html`. Add or edit ventures there, not in markup. Each entry: `name`, `thesis`, `status`, accents `a` and `b`, `tint`, optional `bracket` (the AI Contextualizers numeral wears brackets).

## Budgets (acceptance criteria, keep them honest)

- Total transfer under 500KB (currently about 285KB). Lighthouse 95+ across categories, LCP under 1.5s on 4G.
- If you add an image, subset it hard or it blows the budget; the old inline-everything pattern belongs to `legacy/` only.
- The emblem animation animates `stroke-dashoffset`, `transform`, `opacity` only. Keep it that way for 60fps.

## v19 (legacy) notes

The old page is one 5.3MB self-contained artifact: 28 base64 images, 3 base64 PDFs, five embedded sub-documents (so `<footer>`, `</body>`, `<style>` are not unique in it). If you must read it, work by anchors and never print the base64 blobs. Its instruments (Biographage, Historiotempo, the Desk) still function there.
