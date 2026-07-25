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
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src" / "pages"

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
<div class="topbar">
  <div class="wrap">
    <span>4225 Aiken Drive, Warrenton, VA 20187</span>
    <a href="tel:+15403498760">(540) 349-8760</a>
  </div>
</div>
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
        Mail: PO Box 3046, Warrenton, VA 20188<br>
        <a href="tel:+15403498760">(540) 349-8760</a></p>
        <div class="social-row">
          <a href="https://www.facebook.com/FCTStage/">Facebook</a>
          <a href="https://www.instagram.com/fctmedia">Instagram</a>
          <a href="https://www.youtube.com/channel/UCks6GnLSL9EQZD54or1jcOA">YouTube</a>
          <a href="https://twitter.com/FCTStage">Twitter</a>
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
          <li><a href="/about/board/">Board &amp; Staff</a></li>
          <li><a href="/about/standards/">Standards of Behavior</a></li>
          <li><a href="/news/">News</a></li>
          <li><a href="http://visitor.r20.constantcontact.com/d.jsp?llr=o9cdr5cab&amp;p=oi&amp;m=1102683671374&amp;sit=tohmxqneb&amp;f=771fb9f8-ef8d-42d6-a7e6-dcb7e3aaf2c2">Subscribe to the Spotlight Newsletter</a></li>
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


def build():
    urls = []
    for frag in sorted(SRC.rglob("*.html")):
        meta, body = parse_fragment(frag.read_text())
        rel = frag.relative_to(SRC)
        out = ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        html = (
            HEAD.format(
                title=meta["title"],
                description=meta["description"],
                nav_items=nav_html(meta.get("active", "")),
            )
            + body.rstrip()
            + "\n"
            + FOOT
        )
        out.write_text(html)
        if rel.name == "index.html":
            path = "/" if rel.parent == Path(".") else f"/{rel.parent.as_posix()}/"
            urls.append(f"https://fauquiertheater.org{path}")
        print(f"built {rel}")

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap += [f"  <url><loc>{u}</loc></url>" for u in sorted(urls)]
    sitemap.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sitemap) + "\n")
    print("built sitemap.xml")


if __name__ == "__main__":
    build()
