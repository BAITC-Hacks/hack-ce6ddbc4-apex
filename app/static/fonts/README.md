# Local Geist font

`Geist-Variable.woff2` is the original unmodified variable sans font from official npm package `geist@1.7.2`, published from https://github.com/vercel/geist-font. It is distributed under the SIL Open Font License 1.1; retain `Geist-OFL.txt` with copies. No application npm dependency was added.

Package URL: https://registry.npmjs.org/geist/-/geist-1.7.2.tgz. The package tarball was checked against the SHA-512 integrity value returned by the npm registry before extraction. `geist-provenance.json` records the local font checksum and coverage checks.

Use:

```css
@font-face {
  font-family: "Geist";
  src: url("/static/fonts/Geist-Variable.woff2") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}

body {
  font-family: "Geist", Arial, sans-serif;
}
```

## Character coverage check

The Unicode character map in the corresponding `Geist-Variable.ttf` from the same npm package was parsed. Its map covers 728 codepoints. Every letter in the test strings below maps to a nonzero glyph:

- English: `ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`
- Russian: `АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя`
- Kazakh-specific letters: `ӘҒҚҢӨҰҮҺІәғқңөұүһі`

The tenge currency sign `₸` is missing from that character map, so the browser must retain its system fallback. This check tests letter presence, not full language shaping, every punctuation mark, or every Unicode character. The WOFF2 file itself was not separately decompressed; the test was on its matching TTF distribution from the same verified package. Include a visible RU/KZ/EN specimen and `₸` in browser QA.

The variable `wght` axis is 100 to 900 with default 400. All supplied Figma weights (Light 300, Regular 400, Medium 500) are supported.
