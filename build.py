#!/usr/bin/env python3
"""Assemble the static site: wrap each fragment in src/pages/ with the shared
header/footer and write it to the matching path in the repo root.

Usage: python3 build.py

Each fragment starts with a metadata comment:

    <!-- meta
    title: Page Title
    description: Meta description.
    active: /about/
    -->

followed by the page's <main> content. `active` marks the top-nav item that
gets aria-current="page".
"""
import re
import json
import html as _html
from pathlib import Path
from itertools import groupby

ROOT = Path(__file__).parent
SRC = ROOT / "src" / "pages"
NEWS_DATA = ROOT / "src" / "news.json"

NAV_ITEMS = [
    ("/shows/", "Shows &amp; Tickets"),
    ("/auditions/", "Auditions"),
    ("/summer-camps/", "Summer Camps"),
    ("/get-involved/", "Get Involved"),
    ("/support/", "Support Us"),
    ("/about/", "About"),
    ("/contact/", "Contact"),
]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="stylesheet" href="/css/style.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/">
      <img src="/assets/images/fct-star.png" alt="" width="48" height="48">
      <span class="brand-name">Fauquier<small>Community Theatre</small></span>
    </a>
    <nav class="site-nav" id="site-nav" aria-label="Main navigation">
      <ul>
{nav_items}      </ul>
    </nav>
    <div class="header-actions">
      <a class="btn-tickets" href="https://fctstage.thundertix.com/">Buy Tickets</a>
      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">&#9776;</button>
    </div>
  </div>
</header>

<main id="main">
"""

FOOT = """</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h3>Fauquier Community Theatre</h3>
        <p>Vint Hill Theatre<br>4225 Aiken Drive, Warrenton, VA 20187<br>
        Mail: PO Box 3046, Warrenton, VA 20188</p>
        <div class="social-row">
          <a href="https://www.facebook.com/FCTStage/">Facebook</a>
          <a href="https://www.instagram.com/fauquiertheatre">Instagram</a>
        </div>
      </div>
      <div>
        <h3>Visit</h3>
        <ul>
          <li><a href="/shows/">Shows &amp; Tickets</a></li>
          <li><a href="https://fctstage.thundertix.com/">Buy Tickets Online</a></li>
          <li><a href="/faq/">FAQs</a></li>
          <li><a href="/contact/">Contact Us</a></li>
        </ul>
      </div>
      <div>
        <h3>Take Part</h3>
        <ul>
          <li><a href="/auditions/">Auditions</a></li>
          <li><a href="/get-involved/">Volunteer</a></li>
          <li><a href="/summer-camps/">Summer Camps</a></li>
          <li><a href="/support/">Donate &amp; Membership</a></li>
        </ul>
      </div>
      <div>
        <h3>About</h3>
        <ul>
          <li><a href="/about/">Mission &amp; History</a></li>
          <li><a href="/about/board/">Board of Directors</a></li>
          <li><a href="/about/standards/">Standards of Behavior</a></li>
          <li><a href="/news/">News</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-note">
      <p>Fauquier Community Theatre is a 501(c)(3) non-profit organization. All donations are tax-deductible.</p>
      <p>FCT's programs and projects are supported in part by the Virginia Commission for the Arts, which receives support from the Virginia General Assembly and the National Endowment for the Arts, a federal agency.</p>
      <p>Fauquier Community Theatre is an Equal Opportunity Employer/Program. Auxiliary aids and services are available upon request to individuals with disabilities.</p>
    </div>
  </div>
</footer>
<script src="/js/nav.js"></script>
</body>
</html>
"""

META_RE = re.compile(r"<!--\s*meta\s*\n(.*?)-->\s*\n?", re.DOTALL)


def parse_fragment(text):
    m = META_RE.match(text)
    if not m:
        raise ValueError("fragment missing <!-- meta --> block")
    meta = {}
    for line in m.group(1).strip().splitlines():
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip()
    return meta, text[m.end():]


def nav_html(active):
    lines = []
    for href, label in NAV_ITEMS:
        current = ' aria-current="page"' if href == active else ""
        lines.append(f'        <li><a href="{href}"{current}>{label}</a></li>\n')
    return "".join(lines)


def render(title, description, active, body):
    return (
        HEAD.format(title=title, description=description, nav_items=nav_html(active))
        + body.rstrip()
        + "\n"
        + FOOT
    )


def attr_text(s):
    """Plain-text (attribute-safe) version of a string that may contain HTML."""
    s = re.sub(r"<[^>]+>", "", s)
    s = _html.unescape(s)
    return (
        s.replace("&", "&amp;").replace('"', "&quot;")
        .replace("<", "&lt;").replace(">", "&gt;")
    )


def news_card(p):
    if p["image"]:
        media = f'<img src="{p["image"]}" alt="" loading="lazy">'
    else:
        media = '<span class="news-card-noimg">FCT</span>'
    return (
        f'<a class="news-card card-link" href="/news/{p["slug"]}/">\n'
        f'  <div class="news-card-media">{media}</div>\n'
        f'  <div class="news-card-body">\n'
        f'    <p class="news-date">{p["date"]}</p>\n'
        f'    <h3>{p["title"]}</h3>\n'
        f'    <p class="news-excerpt">{p["excerpt"]}</p>\n'
        f'  </div>\n'
        f'</a>'
    )


def build_news(emit):
    posts = json.loads(NEWS_DATA.read_text())

    # Individual post pages, in blog-post format, with older/newer navigation.
    for i, p in enumerate(posts):
        hero = (
            f'<img class="post-hero" src="{p["image"]}" alt="">' if p["image"] else ""
        )
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        older_lnk = (
            f'<a class="post-nav-older" href="/news/{older["slug"]}/">'
            f'<span>&larr; Older</span>{older["title"]}</a>' if older else "<span></span>"
        )
        newer_lnk = (
            f'<a class="post-nav-newer" href="/news/{newer["slug"]}/">'
            f'<span>Newer &rarr;</span>{newer["title"]}</a>' if newer else "<span></span>"
        )
        body = (
            f'<article class="post">\n'
            f'  <div class="wrap post-wrap">\n'
            f'    <p class="post-back"><a href="/news/">&larr; All News</a></p>\n'
            f'    <p class="eyebrow">{p["date"]}</p>\n'
            f'    <h1>{p["title"]}</h1>\n'
            f'    {hero}\n'
            f'    <div class="prose post-body">\n{p["body"]}\n</div>\n'
            f'    <nav class="post-nav">{older_lnk}{newer_lnk}</nav>\n'
            f'  </div>\n'
            f'</article>'
        )
        title = attr_text(p["title"])
        desc = attr_text(p["excerpt"] or p["title"])
        emit(
            Path("news") / p["slug"] / "index.html",
            render(f"{title} — Fauquier Community Theatre", desc, "", body),
        )

    # Archive index, grouped by year.
    sections = []
    for year, group in groupby(posts, key=lambda p: p["year"]):
        cards = "\n".join(news_card(p) for p in group)
        sections.append(
            f'<h2 class="news-year">{year}</h2>\n'
            f'<div class="news-grid">\n{cards}\n</div>'
        )
    body = (
        '<div class="page-hero">\n  <div class="wrap">\n'
        '    <h1>News &amp; Announcements</h1>\n'
        '    <p>Cast announcements, reviews, season news, and community happenings '
        'from Fauquier Community Theatre.</p>\n  </div>\n</div>\n\n'
        '<div class="section">\n  <div class="wrap">\n'
        + "\n".join(sections)
        + "\n  </div>\n</div>"
    )
    emit(
        Path("news") / "index.html",
        render(
            "News &amp; Announcements — Fauquier Community Theatre",
            "News and announcements from Fauquier Community Theatre — cast "
            "announcements, reviews, and season news since 2013.",
            "",
            body,
        ),
    )


def build():
    urls = []

    def emit(rel, page_html):
        rel = Path(rel)
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page_html)
        if rel.name == "index.html":
            path = "/" if rel.parent == Path(".") else f"/{rel.parent.as_posix()}/"
            urls.append(f"https://fauquiertheater.org{path}")
        print(f"built {rel}")

    for frag in sorted(SRC.rglob("*.html")):
        meta, body = parse_fragment(frag.read_text())
        rel = frag.relative_to(SRC)
        emit(rel, render(meta["title"], meta["description"],
                         meta.get("active", ""), body))

    build_news(emit)

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{u}</loc></url>" for u in sorted(urls)]
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n")
    print("built sitemap.xml")


if __name__ == "__main__":
    build()
