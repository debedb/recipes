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
  optional notes, optional cook log, sources. Cook log and sources go last.
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

## Cooks

A file is a dish, not a diary entry. The quantities at the top are the current
best version of it; `## Cooks` underneath is what actually happened, dated.

```markdown
## Cooks

### 2026-09-17

First actual cook. Against the starting quantities:

- Coconut oil, 3 oz, in place of 3 tbsp butter.
- Water up a full cup, to 2 1/2.

Carrots were not weighed. A little under 2 lb.
```

- Newest cook first. `### YYYY-MM-DD` per entry.
- An entry says what moved against what was there before, and why it mattered -
  a substitution that changed the timing, the seasoning or the kosher status
  says so. A quantity that merely got more precise does not need a line.
- **Anything eyeballed is named as not weighed.** `status: tested` means it was
  cooked, not that every number in the file was measured. A quantity nobody
  weighed stays at its starting figure and the cook entry says so. Inventing
  precision to make the file look finished is the one thing that makes the
  collection worthless.
- The difference from `## Notes`: Notes says why the recipe is the way it is
  and outlives any one cook. Cooks says what happened on a day.
- A first cook of a `synthesized` recipe belongs here, not in a new file. There
  is no tested parent to adapt from yet - the recipe is simply becoming real.

## Adaptations

A variation you would deliberately cook again gets its own file. One you did
once because of what was in the house is a cook entry, not a new recipe. Promote
it when you repeat it on purpose.

- Name it `<parent>-<what-changed>.md`.
- `adapted_from:` points at the parent.
- A `## Changes from the original` section lists each swap and what it cost.
  A swap that changes cooking time or seasoning says so; that is the part the
  parent recipe cannot tell you.
- The parent lists the child under `## Adaptations` as **a bare filename and
  nothing else**. The label on the published page comes from the child's own
  title, so there is no prose here to drift out of date. It drifted within
  hours the first time it was written by hand.
- The ingredient list stays complete. An adaptation is a recipe you can cook
  without opening the parent, and a block you can paste into Cronometer whole.

## Recording a cook

Two paths, both used:

1. From the kitchen, file the **Cooked it** issue
   (`.github/ISSUE_TEMPLATE/cooked.yml`). Durable, and it survives being
   interrupted - an unsubmitted free-form issue draft does not.
2. Later, hand the issue number over and it becomes the file edit and the PR.

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
- It refuses the build when an `adapted_from:` names a parent that does not
  exist, or a parent that does not list the child under `## Adaptations`. A
  one-directional link rots quietly: the child knows its parent, the parent's
  page never mentions the child, and nobody notices.
- Markdown dialect is only what is written here. Quantity goes first on the
  line so an ingredient list pastes into an importer as-is. `### YYYY-MM-DD`
  under `## Cooks` is the only third-level heading.

Flat layout for now. Folders when the flat listing gets annoying.
