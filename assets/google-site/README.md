# Google Sites assets

Assets for the Fauquier Community Theatre Google Site, derived from the
current fauquiertheater.org design (`css/style.css`, `assets/images/`).

## Theme colors (Google Sites custom theme)

| Slot      | Hex       | Source on current site                 |
|-----------|-----------|----------------------------------------|
| Primary   | `#1b3a7a` | `--navy` (links, buttons, headings)    |
| Secondary | `#d92b34` | `--red` (star red, hover, accents)     |
| Tertiary  | `#3aa63f` | `--green` (star green, subtitle text)  |

Supporting values if a slot asks for them: dark navy `#12295a`,
gold `#f2b632`, body text `#22304a`, warm background `#f6f7fb`.

## Files

- `fct-logo-google-site-240h.png` — header logo, navy text, transparent (240 px tall)
- `fct-logo-google-site-240h-white.png` — same lockup for a dark header
- `fct-star-icon-512.png` — square star icon (favicon / social)
- `fct-large-banner-google-site-1440x600.jpg` — **Large banner header (use this one).** Full photo fits the
  banner height, navy fade on the sides, 100 px of extra sky above the roof sign so the
  overlaid navigation bar never covers "THEATER". `…-2048x853.jpg` is the same at 2x.
- `fct-banner-google-site-1440x300.jpg` — **Banner header (standard, not large).** Whole photo fits the
  height and fades to solid `#12295a` on all four sides. `…-2880x600.jpg` is the same at 2x.
- `fct-banner-google-site-1440x480.jpg` — earlier 480 px banner, matches the current hero
- `fct-banner-google-site-photo-1440x480.jpg` — full-bleed photo alternative
- `fct-cover-google-site-1440x1024.jpg` — Cover header

Regenerate with `tools/build_google_site_assets.py` and `tools/build_google_site_large_banner.py`,
and `tools/build_google_site_banner_300.py`.
