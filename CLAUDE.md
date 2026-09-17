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
---
```

- `tags`: diet and category labels - keto, paleo, kosher, side, mom.
- `status`: `synthesized` (from sources, not yet cooked) or `tested` (cooked;
  quantities are what was actually used, not what the source claimed).

Flat layout for now. Folders when the flat listing gets annoying.
