# Embico reference and extracted asset inventory

## Source and verification

Source: `/Users/k4ssym/Downloads/embico.pdf/embico.pdf`. The file supplied locally is a 29-page PDF. Each page is 1920 x 1080 PDF points and contains one embedded 1920 x 1080 raster image. The original PDF has no font resources, text layer, separate illustration objects, or reusable vector components. It was inspected in its entirety using page overview renders, then all extraction regions were visually inspected at native resolution.

Referenced Figma URL: https://www.figma.com/design/Qw7e2YZbnTtyiH1b25A820/embico?node-id=42-2. This inventory concerns the local PDF, not a verified complete export of the live Figma node. The relationship, completeness, and most recent state of the two sources must be checked separately.

Source SHA-256: `5cb430c10a7943be55d882e60a9cf3bf9a22d575248f9eb3a9ba4936f6a1247b`.

The nine PDF assets below are lossless rectangular document-region extractions. They preserve the source pixels, color, shadows, and backgrounds. No transparency was manufactured, and no illustration was redrawn. They are not original transparent Figma exports. The package also contains the locally supplied original `fluid-card.png`, recorded separately below.

## Selected wave background — 23 September 2026

The user selected the brighter blue wave behind the glass tiles in their screenshot. The matching local artwork is `/Users/k4ssym/Downloads/fluid-card.png`, copied byte-for-byte to `app/static/assets/embico/fluid-card.png`. It is a 1536 x 1024 RGB PNG, 1,869,098 bytes, with an opaque background and no glass icon tiles. SHA-256: `e61c0756f36a9d631e8443287d8f0351d5c104cf127d469b44ef1f4752fb7fe3`.

This original was visually matched to the supplied screenshot; it was not newly exported from live Figma, and its exact Figma node is unverified. It is the selected background for the current designbook hero, authentication samples and screen samples, replacing the pale wave in those placements. Preserve its proportions and use layout cropping without recoloring or stretching. The nine PDF crops remain in the asset archive and have not been overwritten. The gallery displays the selected original and eight PDF crops; the replaced pale `glass-wave-wide.png` remains archived only. `fluid-card` is received and must not be requested again.

## Exact sampled source palette

Values were measured from dominant repeated pixel colors. They are observed source colors, not claimed Figma variable names.

| Role | Observed hex | Source pages | Use |
| --- | --- | --- | --- |
| Brand blue | `#2B5FE3` | 1, 7, 25 | Primary brand field, active indicators |
| Ink | `#111318` | 5, 17 | Headlines, body text |
| Deep navy | `#0E1626` | 1 | Primary UI buttons and dark information panels |
| Muted source text | `#7C818C` | 5, 17 | Large secondary text; do not automatically reuse for small copy |
| White | `#FFFFFF` | Most pages | Main page and card backgrounds |
| Alternate panel | `#FAFAFB` | 5, 17 | Middle column of three-card composition |
| UI surface | `#EEF1F6` | 1 | Soft inner panels and controls |
| Secondary UI surface | `#F7F7F8` | 1 | Browser header and light chrome |
| Divider | `#E6E7EB` | 5, 17 | Fine panel separators |
| UI divider | `#E3E7EF` | 1 | Inner interface edges |
| Grid line | `#4D79E7` | 7, 25 | Decorative blue field grid |

Contrast ratios against white, calculated from these colors: brand blue 5.46:1, ink 18.58:1, deep navy 18.08:1, muted source text 3.91:1. The muted reference gray is below 4.5:1, so small readable body copy in Tandau needs a darker derived token. Decorative separators are not sufficient by themselves for interactive input boundaries.

## Live Figma verification supplement

The live Figma inspection completed in the same task subsequently verified these styles. They supersede visual guesses for the interface design; the PDF palette above remains an exact record of sampled pixels from the presentation export.

| Figma style | Verified value |
| --- | --- |
| Font family | Geist |
| Display | 56 px, Regular |
| H1 | 44 px, Regular |
| H2 | 32 px, Regular |
| H3 | 22 px, Medium |
| Body | 17 px, Light |
| Label | 14 px, Regular |
| Numbers | 44 px, Light |
| Surface | `#FFFFFF` |
| Card | `#ECF1F6` |
| Page | `#E3E7EF` |
| Navy | `#0E1626` |
| Navy card | `#1A2437` |
| Slate | `#3E5266` |
| Blue | `#2B5FE3` |
| Blue on dark | `#9DB4FF` |

The exact official Geist variable font is vendored under `app/static/fonts/` from npm package `geist@1.7.2`, alongside its SIL Open Font License and provenance record. This is an official upstream font distribution, not a font extracted from the flattened PDF. The variable axis supports weights 100 through 900. The corresponding TTF character map includes the tested English, Russian, and Kazakh alphabets. The tenge sign (`₸`) is absent; preserve a system fallback in the CSS font stack. See `app/static/fonts/README.md` for the test method and exact coverage limitations.

## Typography and composition observations

- The primary face is a neutral sans serif/grotesk. Its family cannot be recovered from the flattened PDF alone; the subsequent live Figma inspection identified Geist.
- Some display panels use an italic serif, notably the large “Why now?” on page 7 and “Appendix” on page 25. Treat it as an editorial accent; do not use it for forms, data, or dense interface text.
- Large headings combine muted and near-black words in one line. UI text has a more compact hierarchy.
- Main pitch pages use generous white margins, disciplined columns, thin borders, and almost no container shadows. The 3D objects provide depth themselves.
- Page 1 shows a pale interface shell with rounded inner cards, capsule buttons, navy primary controls, light gray tabs/chips, and small blue accents. Screen visual measurements are illustrative; the PDF cannot provide component constraints or exact design-token values.
- The glass wave appears as atmospheric edge artwork on pages 1 and 24. It should not sit behind essential paragraph text or form fields.
- Blue grid fields with fine lines and cross intersections appear on pages 7 and 25. They work as occasional editorial panels, not as a universal background.
- The 3D family uses satin silver/gray bodies, cobalt accents, softened corners, and a consistent upper-left highlight. Keep natural proportions.

## Extracted illustrations and decorative assets

All implementation files are in `app/static/assets/embico/`. Coordinates below are `[left, top, right, bottom]` in pixels from the top-left of the embedded page image; right and bottom are exclusive. No resampling was applied.

| File | PDF page / image xref | Crop rectangle | Native size | Background | Intended Tandau use |
| --- | --- | --- | --- | --- | --- |
| `documents-3d.png` | 5 / 40 | `[112, 320, 352, 560]` | 240 x 240 | `#FFFFFF` | Brief intake and structured project information |
| `chain-3d.png` | 5 / 40 | `[704, 320, 944, 560]` | 240 x 240 | `#FAFAFB` | Explain gaps or missing requirements; do not imply successful connection |
| `restricted-cube-3d.png` | 5 / 40 | `[1288, 320, 1528, 560]` | 240 x 240 | `#FFFFFF` | Unsupported or blocked state; do not use as a success or trust badge |
| `timer-3d.png` | 17 / 136 | `[112, 316, 352, 556]` | 240 x 240 | `#FFFFFF` | Fast shortlist / delivery time |
| `stack-3d.png` | 17 / 136 | `[688, 316, 928, 556]` | 240 x 240 | `#FAFAFB` | Comparison and layered evidence |
| `grid-3d.png` | 17 / 136 | `[1288, 316, 1528, 556]` | 240 x 240 | `#FFFFFF` | Categories and dashboard modules |
| `glass-wave-wide.png` | 24 / 192 | `[0, 700, 1920, 1080]` | 1920 x 380 | `mixed white and translucent blue` | Archived pale-wave reference; superseded by `fluid-card.png` for current hero/auth/screen backgrounds |
| `glass-wave-blue-edge.png` | 1 / 9 | `[0, 0, 200, 1080]` | 200 x 1080 | `mixed blue` | Decorative edge only; native width is 200 pixels |
| `cobalt-grid-strip.png` | 25 / 200 | `[0, 200, 1920, 380]` | 1920 x 180 | `#2B5FE3` | Decorative blue band |

The six square illustrations are 240 x 240 pixels including their margins. Recommended screen display size is 88-120 CSS pixels, leaving enough density for ordinary high-density screens. Do not enlarge a square to a full-screen hero. Use the selected original `fluid-card.png` for the current large wave backgrounds, within its native-resolution limits.

`chain-3d.png` and `stack-3d.png` have a solid `#FAFAFB` background; place them on that exact surface. The other four square illustrations have white backgrounds. Avoid dark surfaces and arbitrary tinted panels behind these rectangular assets. CSS `mix-blend-mode` is not required and can change the source appearance.

Use `alt=""` when an illustration duplicates nearby wording and is decorative. If it conveys a unique meaning, use a localized label. The broken chain illustrates a gap; the restricted cube illustrates an unavailable or blocked state. Do not assign those images a positive meaning that contradicts their visible content.

## Page-by-page reference map

| Page | Visual reference / content category | Image xref |
| --- | --- | --- |
| 1 | Cobalt hero, blue glass wave, large product interface mockup | 9 |
| 2 | White split layout and photo | 16 |
| 3 | Large statistic and five-bar diagram | 24 |
| 4 | Four statistic quadrants | 32 |
| 5 | Three columns: documents, broken chain, restricted cube | 40 |
| 6 | Dark bar-chart panel and white text column | 48 |
| 7 | White narrative with blue grid and italic display | 56 |
| 8 | Tablet product mockup and floating white chips | 64 |
| 9 | Large application screenshot beside short text | 72 |
| 10 | Four-cell benefit grid | 80 |
| 11 | Compact module list | 88 |
| 12 | Dark evidence card beside narrative | 96 |
| 13 | Comparison table | 104 |
| 14 | Application screenshot beside narrative | 112 |
| 15 | Black concentric-circle diagram and white statistic area | 120 |
| 16 | Vertical three-step narrative | 128 |
| 17 | Three pricing cards: timer, stacked slabs, four blocks | 136 |
| 18 | Three revenue metrics | 144 |
| 19 | Large blue metric and star decoration | 152 |
| 20 | Eight-phase grid | 160 |
| 21 | Four portrait cards | 168 |
| 22 | Risk list in white cards | 176 |
| 23 | Large blue metric and dark side panel | 184 |
| 24 | White closing composition with blue glass wave | 192 |
| 25 | Full cobalt grid and italic display | 200 |
| 26 | Compact two-row requirements matrix | 208 |
| 27 | White/black split data-flow schematic | 216 |
| 28 | Four quadrants of technical text | 224 |
| 29 | Source bibliography | 232 |

Full-page intermediate images and overview sheets were kept outside the repository at `/tmp/tandau-embico-reference/`. The repository includes the nine reusable extracted regions, the selected local original `fluid-card.png`, and their machine-readable `manifest.json`.

## Export requests to complete Figma fidelity

The current assets support a visible working designbook. To match the original editable design exactly and use the illustrations on arbitrary backgrounds, request these specific items:

1. Transparent PNG or WebP at 2x (or SVG when truly vector) for the six 3D illustrations, retaining their soft shadows. Prefer at least 512 x 512 pixels.
2. `fluid-card.png` is received and selected; no further request is needed for that background. `cover-hero` and `fluid-auth` remain outside the imported package and require separate source verification/integration. Any needed transparent variants should be requested specifically, without replacing the selected `fluid-card` background automatically.
3. The font family and main type styles have now been verified in live Figma and official Geist files are included locally. Request any further custom type styles only if they appear in additional frames.
4. The main color styles have now been verified in live Figma. Request additional exported spacing/radius tokens if exact component geometry is needed beyond the inspected frames.
5. Any Tandau-specific wordmark, logo artwork, or icon set that should replace the reference brand.

The reference product wordmark, clinical screens, portraits, and claims are not Tandau product assets. They were not exported into the implementation asset folder. The locally provided reference and the user request establish the working source; this inventory does not assert broader rights beyond that provided authorization.

## Reproducibility

`manifest.json` records the source checksum, every extracted file checksum, all page image xrefs, native dimensions, region coordinates, backgrounds, and suggested usage. Re-export from the original page image with the same crop rectangle to obtain the same visible region. PNG container checksums can differ between encoders while the decoded pixels remain equal.
