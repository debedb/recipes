# recipes — working notes

## What this is

Personal recipe collection, two streams:

1. Mom's recipes. Preserving them, and adjusting them (for simplicity, for
   diet). The adjusting is part of the point, not a betrayal of the original:
   she likes being listened to, and she likes seeing what comes back.
2. Things found online, synthesized and adapted.

Long game is adapting dishes for other diets - keto, paleo, kosher. That takes
actually cooking the thing. Scraping the internet only supplies a starting
point; it does not produce a recipe that works.

## Format

- One markdown file per recipe.
- Sections: title, yield, ingredients, numbered steps, optional serving note,
  sources.
- No life story, no SEO preamble, no video, no stock photography. Greg's own
  photos of the finished dish are welcome once they exist.
- Every ingredient gets an explicit quantity on its own line. Recipes should be
  importable into cronometer.com personal recipes later without a rewrite.
- Terse. Steps say what to do and why only where the why prevents a failure.

## Frontmatter

```yaml
---
tags: [keto]
status: synthesized
cooked: 2026-09-17
adapted_from: cauliflower-polenta.md
cronometer: https://cronometer.com/...
---
```

- `tags`: diet and category labels - keto, paleo, kosher, side, mom.
- `status`: `synthesized` (from sources, not yet cooked) or `tested` (cooked;
  quantities are what was actually used, not what the source claimed).
- `cooked`: date of the cook the quantities come from. Only on `tested`.
- `adapted_from`: filename of the parent recipe. Only on adaptations.
- `cronometer`: link to the recipe in Cronometer, once it exists. Optional.

## Adaptations

An adaptation is its own file, not a section in the parent. Vegetarian, keto,
paleo, kosher, or just what was in the house that day.

- Name it `<parent>-<what-changed>.md`.
- `adapted_from:` points at the parent.
- A `## Changes from the original` section lists each swap and what it cost.
  A swap that changes cooking time or seasoning says so; that is the part the
  parent recipe cannot tell you.
- The parent gets one line under `## Adaptations` pointing back.
- The ingredient list stays complete. An adaptation is a recipe you can cook
  without opening the parent, and a block you can paste into Cronometer whole.

## Publishing

`build.py` renders every `.md` with frontmatter into `_site/` as HTML carrying
schema.org Recipe JSON-LD, and `.github/workflows/pages.yml` deploys that to
GitHub Pages on push to `main`. The JSON-LD is what recipe importers read.

- `python3 build.py --selftest` checks the parser. CI runs it before building.
- The build refuses a recipe whose `## Ingredients` or `## Steps` it cannot
  parse, rather than publishing a hollow Recipe - an importer fed an empty
  ingredient list does not error, it silently creates an empty recipe.
- It warns on ingredient lines with no quantity. Salt-to-taste is fine; a real
  ingredient without a number is a line that imports wrong.
- Markdown dialect is only what is written here. Quantity goes first on the
  line so an ingredient list pastes into an importer as-is.

Flat layout for now. Folders when the flat listing gets annoying.
