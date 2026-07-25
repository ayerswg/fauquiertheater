#!/usr/bin/env python3
"""Extract & sanitize FCT WordPress posts into a clean posts.json + image list.

Outputs:
  out/posts.json          list of {slug,date,iso,title,image,excerpt,body}
  out/image_urls.txt      "localname<TAB>remoteurl" for every image to fetch
Image src values in body/image are already rewritten to /assets/images/news/<localname>.
"""
import json, glob, re, os, html
from datetime import datetime
from bs4 import BeautifulSoup, NavigableString

OUT = "out"
os.makedirs(OUT, exist_ok=True)

posts = []
for f in sorted(glob.glob("blog/posts-*.json")):
    posts += json.load(open(f))

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

images = {}  # localname -> remote url


def localname(url):
    m = re.search(r"/uploads/(.+)$", url)
    base = m.group(1) if m else url.rsplit("/", 1)[-1]
    # strip WP size suffix like -1024x292 to prefer original where we fetch full
    name = base.replace("/", "_")
    name = re.sub(r"[?#].*$", "", name)
    return name


def register(url):
    """Record an image to download; return its local site path."""
    if not url or not url.startswith("http"):
        return None
    ln = localname(url)
    images.setdefault(ln, url)
    return "/assets/images/news/" + ln


def featured_url(p):
    fm = p.get("_embedded", {}).get("wp:featuredmedia", [])
    if not fm or not isinstance(fm[0], dict):
        return None
    md = fm[0].get("media_details", {}) or {}
    sizes = md.get("sizes", {}) or {}
    for key in ("large", "medium_large", "1536x1536"):
        if key in sizes and sizes[key].get("source_url"):
            return sizes[key]["source_url"]
    return fm[0].get("source_url")


ALLOWED = {"p", "a", "ul", "ol", "li", "h2", "h3", "h4", "strong", "b",
           "em", "i", "blockquote", "br", "hr", "img", "figure", "figcaption"}


def clean_body(html_src, drop_img_src=None):
    soup = BeautifulSoup(html_src, "html.parser")

    for bad in soup(["script", "style"]):
        bad.decompose()

    # video embeds -> link
    for ifr in soup.find_all("iframe"):
        src = ifr.get("src", "")
        if src:
            a = soup.new_tag("a", href=src)
            a.string = "Watch the video"
            p = soup.new_tag("p")
            p.append(a)
            ifr.replace_with(p)
        else:
            ifr.decompose()

    # demote stray h1
    for h1 in soup.find_all("h1"):
        h1.name = "h2"

    # rewrite / register images; drop the one promoted to hero
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if drop_img_src and src == drop_img_src:
            (img.find_parent("figure") or img).decompose()
            continue
        newsrc = register(src)
        alt = img.get("alt", "")
        img.attrs = {}
        if newsrc:
            img["src"] = newsrc
            img["alt"] = alt
            img["loading"] = "lazy"

    # unwrap everything not allowed (divs, headers, spans, time, etc.)
    for tag in soup.find_all(True):
        if tag.name not in ALLOWED:
            tag.unwrap()
        else:
            keep = {}
            if tag.name == "a" and tag.get("href"):
                href = re.sub(r"[?&](fbclid|utm_[a-z]+)=[^&]*", "", tag["href"])
                href = re.sub(r"\?$", "", href)
                keep["href"] = href
                if href.startswith("http"):
                    keep["rel"] = "noopener"
            if tag.name == "img":
                keep = tag.attrs
            tag.attrs = keep

    # wrap loose top-level text (left by unwrapped time/div/span) in <p>
    for node in list(soup.contents):
        if isinstance(node, NavigableString) and node.strip():
            p = soup.new_tag("p")
            node.wrap(p)

    # collapse whitespace-only text, drop empty blocks
    for tag in soup.find_all(["p", "h2", "h3", "h4", "li", "figcaption"]):
        if not tag.get_text(strip=True) and not tag.find("img"):
            tag.decompose()

    out = str(soup)
    out = re.sub(r"(\s*<br/>\s*){2,}", "<br/>", out)
    out = re.sub(r"\n{2,}", "\n", out).strip()
    return out


def excerpt_of(body_html):
    text = html.unescape(re.sub(r"<[^>]+>", " ", body_html))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 200:
        text = text[:200].rsplit(" ", 1)[0] + "…"
    return text


records = []
for p in posts:
    raw = p["content"]["rendered"]
    feat = featured_url(p)
    drop = None
    if not feat:
        m = re.search(r'<img[^>]+src="([^"]+)"', raw)
        if m:
            feat = m.group(1)
            drop = feat
    image_local = register(feat) if feat else None
    body = clean_body(raw, drop_img_src=drop)
    d = datetime.fromisoformat(p["date"])
    records.append({
        "slug": p["slug"],
        "iso": p["date"][:10],
        "date": f"{MONTHS[d.month]} {d.day}, {d.year}",
        "year": d.year,
        "title": p["title"]["rendered"].strip(),
        "image": image_local,
        "excerpt": excerpt_of(body) if body else "",
        "body": body,
    })

records.sort(key=lambda r: r["iso"], reverse=True)
json.dump(records, open(f"{OUT}/posts.json", "w"), indent=1, ensure_ascii=False)
with open(f"{OUT}/image_urls.txt", "w") as fh:
    for ln, url in sorted(images.items()):
        fh.write(f"{ln}\t{url}\n")

print("posts:", len(records))
print("with image:", sum(1 for r in records if r["image"]))
print("images to fetch:", len(images))
print("years:", sorted({r["year"] for r in records}))
