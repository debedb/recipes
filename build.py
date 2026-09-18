#!/usr/bin/env python3
"""Render the recipe markdown into static HTML carrying schema.org Recipe JSON-LD.

The point of the JSON-LD is import: a recipe page with machine-readable
ingredients and steps is what recipe importers (Cronometer's among them) look
for. The markdown stays the source of truth; this only projects it.

The markdown dialect is the one CLAUDE.md defines, nothing wider: frontmatter,
one '# Title', intro prose, '## Ingredients' as a bullet list, '## Steps' as a
numbered list, then optional prose sections. Anything else is rendered as
paragraphs.

Usage:
    python3 build.py [outdir]     # default outdir: _site
    python3 build.py --selftest
"""

import html
import json
import os
import re
import sys

SKIP = {"README.md", "CLAUDE.md"}
SITE_URL = os.environ.get("SITE_URL", "https://recipes.debedb.com")

CSS = """
:root { color-scheme: light dark; --fg: #1a1a1a; --bg: #fff; --mut: #666; }
@media (prefers-color-scheme: dark) {
  :root { --fg: #e8e8e8; --bg: #161616; --mut: #9a9a9a; }
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--fg); margin: 0 auto; padding: 2rem 16px;
  max-width: 42rem; line-height: 1.55;
  font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
h1 { font-size: 1.7rem; margin: 0 0 .25rem; }
h2 { font-size: 1.1rem; margin: 2rem 0 .5rem; text-transform: uppercase;
  letter-spacing: .06em; color: var(--mut); }
a { color: inherit; }
ul, ol { padding-left: 1.3rem; }
li { margin: .3rem 0; }
.meta { color: var(--mut); font-size: .85rem; margin-bottom: 1.5rem; }
.meta code { font-size: .85rem; }
footer { margin-top: 3rem; color: var(--mut); font-size: .85rem; }
"""


def parse_front_matter(text):
    """Return (meta, body). Tiny YAML subset: scalars and [a, b] lists."""
    meta = {}
    if not text.startswith("---\n"):
        return meta, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return meta, text
    for line in text[4:end].splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, val = line.partition(":")
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        meta[key.strip()] = val
    return meta, text[end + 5:]


def parse_sections(body):
    """Return (title, intro_lines, [(heading, lines), ...])."""
    title, intro, sections, cur = "", [], [], None
    for line in body.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("## "):
            cur = (line[3:].strip(), [])
            sections.append(cur)
        elif cur is not None:
            cur[1].append(line)
        else:
            intro.append(line)
    return title, intro, sections


def _gather(lines, pattern):
    """Collect list items matching pattern, folding indented continuations."""
    items = []
    for line in lines:
        m = pattern.match(line)
        if m:
            items.append(m.group(1).strip())
        elif items and line.strip() and line[:1].isspace():
            items[-1] += " " + line.strip()
        elif not line.strip():
            continue
    return items


BULLET = re.compile(r"^- (.*)")
NUMBER = re.compile(r"^\d+\. (.*)")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BARE = re.compile(r"(?<![\"'>=])(https?://[^\s<)]+)")
MD_LINK_FILE = re.compile(r"(?<![\w/\">])([a-z0-9-]+)\.md\b")


def md_inline(text):
    out = html.escape(text)
    out = LINK.sub(lambda m: '<a href="%s">%s</a>' % (html.escape(m.group(2)), m.group(1)), out)
    out = BARE.sub(lambda m: '<a href="%s">%s</a>' % (m.group(1), m.group(1)), out)
    out = MD_LINK_FILE.sub(lambda m: '<a href="%s.html">%s.md</a>' % (m.group(1), m.group(1)), out)
    return out


def render(lines):
    """Render a block of markdown lines: bullet lists, numbered lists, paragraphs."""
    out, para = [], []

    def flush():
        if para:
            out.append("<p>%s</p>" % md_inline(" ".join(para)))
            para.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        if BULLET.match(line) or NUMBER.match(line):
            flush()
            pat = BULLET if BULLET.match(line) else NUMBER
            tag = "ul" if pat is BULLET else "ol"
            block = []
            while i < len(lines) and (pat.match(lines[i]) or
                                      (block and lines[i].strip() and lines[i][:1].isspace())):
                block.append(lines[i])
                i += 1
            items = _gather(block, pat)
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % md_inline(x) for x in items), tag))
            continue
        if not line.strip():
            flush()
        else:
            para.append(line.strip())
        i += 1
    flush()
    return "\n".join(out)


def json_ld(meta, title, intro, sections, slug):
    ings = steps = None
    for heading, lines in sections:
        low = heading.lower()
        if low == "ingredients":
            ings = _gather(lines, BULLET)
        elif low == "steps":
            steps = _gather(lines, NUMBER)

    # Refuse rather than emit a hollow Recipe. An importer fed an empty
    # recipeIngredient does not error, it creates an empty recipe.
    if not ings:
        raise ValueError("%s.md: no parseable '## Ingredients' bullet list" % slug)
    if not steps:
        raise ValueError("%s.md: no parseable '## Steps' numbered list" % slug)

    prose = " ".join(x.strip() for x in intro if x.strip())
    data = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": title,
        "url": "%s/%s.html" % (SITE_URL, slug),
        "recipeIngredient": ings,
        "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in steps],
    }
    if prose:
        data["description"] = prose.split(". ")[0] + "."
    m = re.search(r"Serves [^.]+", prose)
    if m:
        data["recipeYield"] = m.group(0).strip()
    tags = meta.get("tags")
    if tags:
        data["keywords"] = ", ".join(tags) if isinstance(tags, list) else tags
    if meta.get("cooked"):
        data["datePublished"] = meta["cooked"]
    return data, ings, steps


def page(title, body_html, jsonld=None):
    head = ""
    if jsonld is not None:
        head = '<script type="application/ld+json">%s</script>' % json.dumps(jsonld, indent=1)
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n%s\n</head>\n<body>\n%s\n"
        '<footer><a href="index.html">All recipes</a> &middot; '
        '<a href="https://github.com/debedb/recipes">source</a></footer>\n'
        "</body>\n</html>\n" % (html.escape(title), CSS, head, body_html)
    )


def build(srcdir, outdir):
    os.makedirs(outdir, exist_ok=True)
    built, unquantified = [], []

    for name in sorted(os.listdir(srcdir)):
        if not name.endswith(".md") or name in SKIP:
            continue
        raw = open(os.path.join(srcdir, name), encoding="utf-8").read()
        meta, body = parse_front_matter(raw)
        if not meta:
            continue
        slug = name[:-3]
        title, intro, sections = parse_sections(body)
        data, ings, _ = json_ld(meta, title, intro, sections, slug)

        for ing in ings:
            if not any(c.isdigit() for c in ing):
                unquantified.append("%s: %s" % (name, ing))

        bits = ["<h1>%s</h1>" % html.escape(title)]
        meta_bits = []
        if meta.get("status"):
            meta_bits.append("status: %s" % meta["status"])
        if meta.get("cooked"):
            meta_bits.append("cooked: %s" % meta["cooked"])
        if meta.get("adapted_from"):
            meta_bits.append('adapted from <a href="%s.html">%s</a>'
                             % (meta["adapted_from"][:-3], meta["adapted_from"]))
        if meta.get("cronometer"):
            meta_bits.append('<a href="%s">cronometer</a>' % html.escape(meta["cronometer"]))
        tags = meta.get("tags") or []
        if tags:
            meta_bits.append("tags: %s" % ", ".join(tags))
        if meta_bits:
            bits.append('<div class="meta">%s</div>' % " &middot; ".join(meta_bits))
        bits.append(render(intro))
        for heading, lines in sections:
            bits.append("<h2>%s</h2>" % html.escape(heading))
            bits.append(render(lines))

        with open(os.path.join(outdir, slug + ".html"), "w", encoding="utf-8") as fh:
            fh.write(page(title, "\n".join(b for b in bits if b), data))
        built.append((slug, title, meta))

    rows = []
    for slug, title, meta in built:
        note = ""
        if meta.get("adapted_from"):
            note = " <small>(adapted from %s)</small>" % html.escape(meta["adapted_from"][:-3])
        rows.append('<li><a href="%s.html">%s</a>%s</li>' % (slug, html.escape(title), note))
    with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page("recipes", "<h1>recipes</h1>\n<ul>%s</ul>" % "".join(rows)))

    print("built %d recipes into %s" % (len(built), outdir))
    if unquantified:
        print("\n%d ingredient lines carry no quantity; these import wrong:"
              % len(unquantified), file=sys.stderr)
        for u in unquantified:
            print("  " + u, file=sys.stderr)
    return len(built)


SAMPLE = """---
tags: [keto, side]
status: tested
cooked: 2026-09-17
adapted_from: parent.md
---

# Test Dish

A thing. Serves 5-6 as a side.

## Ingredients

- 2 lb carrots, cut into
  coins
- Salt

## Steps

1. Do the first thing,
   which continues here.
2. Do the second thing.

## Sources

- https://example.com/x
"""


def selftest():
    meta, body = parse_front_matter(SAMPLE)
    assert meta["tags"] == ["keto", "side"], meta
    assert meta["adapted_from"] == "parent.md", meta
    title, intro, sections = parse_sections(body)
    assert title == "Test Dish", title
    data, ings, steps = json_ld(meta, title, intro, sections, "test-dish")
    assert ings == ["2 lb carrots, cut into coins", "Salt"], ings
    assert steps[0] == "Do the first thing, which continues here.", steps
    assert len(steps) == 2, steps
    assert data["recipeYield"] == "Serves 5-6 as a side", data
    assert data["recipeInstructions"][1]["text"] == "Do the second thing."
    assert data["datePublished"] == "2026-09-17"
    # The refusal is the point: a hollow Recipe must not be emitted.
    try:
        json_ld({}, "X", [], [("Ingredients", ["- 1 thing"])], "x")
    except ValueError as exc:
        assert "Steps" in str(exc), exc
    else:
        raise AssertionError("missing Steps should have raised")
    out = render(["- https://example.com/x", "", "See parent.md for more."])
    assert '<a href="https://example.com/x">' in out, out
    assert '<a href="parent.html">parent.md</a>' in out, out
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        args = [a for a in sys.argv[1:] if not a.startswith("-")]
        sys.exit(0 if build(os.path.dirname(os.path.abspath(__file__)),
                            args[0] if args else "_site") else 1)
