# Fauquier Community Theatre — fauquiertheater.org

Static website for Fauquier Community Theatre (Warrenton, VA). This is a rebuild
of the content from the theater's previous site (fctstage.org, domain access
lost), redesigned as a responsive static site for deployment on Cloudflare Pages.

## How it works

- The deployable site is the **repo root**: plain HTML/CSS/JS, no framework,
  no dependencies. `index.html`, `shows/`, `about/`, etc. are the pages;
  `css/style.css` holds all styling and `js/nav.js` the mobile menu.
- Page **content** lives in `src/pages/` as HTML fragments (the `<main>`
  content plus a small `<!-- meta -->` block for title/description/active
  nav item). The shared header, nav, and footer live in `build.py`.
- `python3 build.py` wraps every fragment with the shared shell and writes the
  finished pages (plus `sitemap.xml`) to the repo root. **Generated pages are
  committed**, so no build step is needed at deploy time.

To edit a page: change the fragment in `src/pages/`, run `python3 build.py`,
and commit both. To change the nav or footer: edit `build.py` and rebuild.

## News archive

The `/news/` archive (index + one page per post, `/news/<slug>/`) is generated
by `build.py` from `src/news.json` — a committed data file holding each post's
title, date, primary image, excerpt, and cleaned body HTML. Post images live in
`assets/images/news/`. `build.py` has no third-party dependencies; the data is
pre-cleaned so no HTML parsing happens at build time.

The data was scraped from the old WordPress site's REST API
(`/wp-json/wp/v2/posts`). To refresh it, re-run the scratchpad `extract.py`
(which needs `beautifulsoup4`) against a fresh API pull, re-download the images
listed in its `image_urls.txt`, and replace `src/news.json`. Editing a single
post afterward is just a JSON edit + `python3 build.py`.

## Local preview

```sh
python3 -m http.server 8737
# then open http://localhost:8737
```

## Cloudflare Pages setup

1. Create a Pages project pointed at this repo.
2. Build command: **none** — leave empty. Build output directory: `/`.
3. Add the custom domain `fauquiertheater.org` (and `www.fauquiertheater.org`).

`404.html` at the root is picked up automatically by Cloudflare Pages for
not-found routes.

## External services still in use

- **ThunderTix** — ticketing, donations, memberships, gift cards
  (`fctstage.thundertix.com`)
- **JotForm** — audition/registration/scholarship/director-proposal forms
- **FlippingBook** — playbill flipbooks

Note: all contact email on the site points to `info@fauquiertheater.org`.
Ticketing links still point at `fctstage.thundertix.com` (carried over from
the old site) and should be revisited if ticketing hosting changes.
