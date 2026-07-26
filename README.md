# Fauquier Community Theatre — fauquiertheatre.org

Static website for Fauquier Community Theatre (Warrenton, VA). It's a rebuild of
the content from the theatre's previous site (fctstage.org, whose domain access
was lost), redesigned as a responsive, dependency-free static site hosted on
Cloudflare.

- **Live site:** https://fauquiertheatre.org
- **Repo:** github.com/ayerswg/fauquiertheater
- **Hosting:** Cloudflare (Git-connected — every push to `main` auto-deploys)

## Repo layout

```
build.py             Generator: wraps page fragments in the shared shell, emits
                     the finished HTML + sitemap.xml. Pure Python stdlib.
src/pages/*.html     Page CONTENT fragments (the <main> body + a <!-- meta --> block).
                     Directory structure here mirrors the final URL structure.
src/news.json        Data for the /news/ archive (one entry per post).
css/style.css        All styling.
js/nav.js            Mobile nav toggle.
assets/images/       Images (logo, show art, historic photos).
assets/images/news/  Per-post news images.
tools/news_extract.py  One-off scraper that produced src/news.json (see below).

# Generated + committed (do not hand-edit — rerun build.py instead):
index.html, shows/, about/, news/, ... , sitemap.xml

# Deploy config:
wrangler.jsonc       Cloudflare Workers static-assets config.
package.json         No-op build script (Cloudflare runs `npm run build`).
.assetsignore        Keeps source files out of the published upload.
robots.txt, favicon.png, 404.html
```

## How the build works

Pages are assembled by `build.py`, which has **no third-party dependencies** (it
uses only the Python standard library):

1. Each file in `src/pages/` is a fragment: the page's `<main>` content preceded
   by a small metadata block:
   ```html
   <!-- meta
   title: Shows & Tickets — Fauquier Community Theatre
   description: ...
   active: /shows/     ← which top-nav item gets highlighted
   -->
   ```
   The fragment's path under `src/pages/` becomes its URL (e.g.
   `src/pages/shows/index.html` → `/shows/`).
2. The shared **header, nav, and footer** live as templates inside `build.py`
   (not in the fragments), so a change there updates every page at once.
3. `build.py` wraps each fragment in that shell, injects a per-page
   `<link rel="canonical">`, and writes the finished page to the repo root. It
   also generates the `/news/` archive from `src/news.json` and writes
   `sitemap.xml`.

**Generated pages are committed to the repo**, so the deploy is just a file
upload — nothing is built on Cloudflare's side beyond copying the files.

### Common edits

- **Edit a page's text:** change the fragment in `src/pages/…`, run
  `python3 build.py`, commit both the fragment and the regenerated page.
- **Change the nav, header, or footer:** edit the templates in `build.py`, then
  rebuild (this touches every page).
- **Edit or add a news post:** edit `src/news.json` (and drop any image into
  `assets/images/news/`), then rebuild.
- **Add an image:** put it in `assets/images/`, reference it with an absolute
  path (`/assets/images/…`), rebuild. All images are served locally — nothing
  hotlinks off-site.

### Build & preview locally

```sh
python3 build.py                 # regenerate all pages + sitemap
python3 -m http.server 8737      # then open http://localhost:8737
```

## Deployment (Cloudflare)

The site is deployed through **Cloudflare's Git integration (Workers Builds)**.
On every push to `main`, Cloudflare runs:

1. Build command: `npm run build` — a **no-op** (`package.json`); the real HTML
   is already generated and committed.
2. Deploy command: `npx wrangler deploy` — reads `wrangler.jsonc` and uploads
   the repo root as a static-assets-only Worker.

`wrangler.jsonc` sets `assets.directory: "."` and `not_found_handling:
"404-page"` (so `404.html` is served for unknown routes). `.assetsignore` keeps
build sources (`src/`, `tools/`, `build.py`, etc.) out of the published upload.

There is **no build step to configure** beyond what's in these files — if you
fork/recreate the project, point Cloudflare at the repo, keep the build command
as `npm run build` and the deploy command as `npx wrangler deploy`, and set the
root directory to `/`.

## Domains

Both spellings are registered and point at the site to catch typos:

- **`fauquiertheatre.org`** ("theatre") is **canonical** — the sitemap and every
  page's `<link rel="canonical">` point here. Served directly by the project.
- **`fauquiertheater.org`** ("theater", the original misspelling) 301-redirects
  to the canonical domain via a Cloudflare **Redirect Rule** (in that zone:
  Rules → Redirect Rules → all requests → `https://fauquiertheatre.org` +
  path, 301).
- **`www.` on both** redirects to the bare canonical domain the same way.

Redirect hostnames need a **proxied** (orange-cloud) DNS record so Cloudflare's
edge can intercept them; the rule returns the redirect before any origin fetch.

## Email

Contact email on the site is **info@fauquiertheatre.org**, delivered via
**Cloudflare Email Routing** on the `fauquiertheatre.org` zone: it forwards to a
verified destination inbox (currently an `@fctstage.org` address). This is
forward-only (incoming mail); to change where it lands, update the destination
in the zone's Email Routing panel — no site change needed.

## External services still in use

- **ThunderTix** — ticketing, donations, memberships, gift cards
  (`fctstage.thundertix.com`)
- **JotForm** — audition / registration / scholarship / director-proposal forms
- **FlippingBook** — playbill flipbooks

Ticketing links still point at `fctstage.thundertix.com` (carried over from the
old site); revisit if ticketing hosting ever changes.

## Refreshing the news archive

`src/news.json` was scraped from the old WordPress site's REST API
(`/wp-json/wp/v2/posts`) by `tools/news_extract.py`. That script needs
`beautifulsoup4` (run it in a virtualenv) and is **not** part of the normal
build — the cleaned `src/news.json` and its images are committed, so day-to-day
edits are just JSON changes. To do a full refresh, re-run the extractor against a
fresh API pull, re-download the images it lists, and replace `src/news.json`.
