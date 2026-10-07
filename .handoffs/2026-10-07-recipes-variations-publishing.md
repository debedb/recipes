# Handoff: Recipe variations, cook logs, and publishing for import

**Created:** 2026-10-07
**Author:** Claude Code session
**For:** AI Agent
**Status:** Ready to execute — one step is blocked on the user, the rest are open

---

## Summary

`debedb/recipes` is a personal recipe collection in markdown. This session gave
it three things: a way to record what actually went in the pot (`## Cooks`), a
way to record deliberate variations as their own files (`adapted_from:`), and a
static site with schema.org Recipe JSON-LD so a recipe importer can read a page.

The site is live but HTTP-only. The one thing standing between it and a working
HTTPS URL is a DNS record that the harness refuses to let an agent create. The
script is inlined below so it survives this session.

## Project Context

- Plain markdown, one file per dish, flat layout. No framework, no dependencies.
- `build.py` is stdlib-only Python. It parses the markdown dialect that
  `CLAUDE.md` pins and emits `_site/*.html` with JSON-LD.
- `.github/workflows/pages.yml` runs `build.py --selftest`, then `build.py
  _site`, then deploys to GitHub Pages on push to `main`.
- The repo is **public** as of this session (it was private; the user approved
  the change after an audit of the full history found nothing sensitive).
- Read `CLAUDE.md` first. It is the spec, not a description.

## The Plan

There was no `.claude/plans/` file. The plan was shaped in conversation, and
the two structural decisions were made by the user from an explicit menu:

1. **A file is a dish, not a diary entry.** Quantities at the top are the
   current best version. A dated `## Cooks` section underneath records what
   happened on a day. `## Notes` holds what outlives any single cook.
2. **Capture happens twice.** From the kitchen, the user files the **Cooked it**
   issue form (`.github/ISSUE_TEMPLATE/cooked.yml`). Later they hand over the
   issue number, and an agent turns it into the file edit and the PR. This is
   how issue #3 worked, and issue #3 is the only cook log that survived.

## Key Files

| File | Why It Matters |
|------|---------------|
| `CLAUDE.md` | The spec. Frontmatter keys, the `## Cooks` rules, the markdown dialect, the publishing contract. |
| `build.py` | Renderer plus three refusals. `--selftest` covers the parser, both link-check failure paths, and the generated label. |
| `.github/workflows/pages.yml` | Builds and deploys. Runs the self-test first. |
| `.github/ISSUE_TEMPLATE/cooked.yml` | Kitchen capture. Has a dedicated "Not measured" field on purpose. |
| `cauliflower-polenta.md` | Parent recipe. Its `## Adaptations` entry is a bare filename by design. |
| `cauliflower-polenta-vegetarian.md` | The adaptation. Demonstrates `adapted_from:` plus `## Changes from the original`. |
| `tzimmes.md` | Demonstrates a first cook of a previously-`synthesized` recipe landing in `## Cooks`. |

## Current State

**Done:**
- Repo public. GitHub Pages enabled with `build_type=workflow`.
- Site live and verified serving valid JSON-LD: 11 ingredients, 8 steps on the
  vegetarian polenta page.
- Issue #3 closed. PRs #4, #7, #8 merged. `main` is at `1bfe187`.
- `cauliflower-polenta-vegetarian.md` written from issue #3's cook log,
  `status: tested`, `cooked: 2026-09-17`.
- `tzimmes.md` moved from `synthesized` to `tested` with the real cook.
- Issues #5 (Cronometer) and #6 (nutrition API) filed with verified evidence.

**In Progress:**
- **PR #9** (`cooks-convention`) is open and unmerged. It carries the `## Cooks`
  convention, the bare-filename back-link, the build's link refusal, and the
  issue template. The user has not reviewed it. This handoff is committed onto
  the same branch.

**Not Started:**
- The `recipes.debedb.com` DNS record. See Next Steps 1.
- `nutrition.py` (issue #6).
- Testing whether Cronometer's importer reads our JSON-LD (issue #5). Blocked
  on HTTPS, and on whether the user has Cronometer Gold.

## Decisions Made

- **A file is a dish; cooks stack inside it.** Chosen by the user over three
  alternatives: one file per repeatable intent, deltas composed at build time,
  and dish-plus-tags with no lineage. Rationale: the repo exists to adjust
  recipes over time and show the user's mother what came back, so history is
  the point rather than noise. Do not re-litigate.
- **An adaptation back-link is a bare filename and nothing else.** The label on
  the published page is pulled from the child file's own `# Title`. The
  hand-written version drifted within hours of being introduced — it named one
  cheese after the adaptation had grown to two — and PR #7 existed only to fix
  that.
- **A first cook of a `synthesized` recipe is a cook entry, not a new file.**
  There is no tested parent to adapt *from*; the recipe is becoming real. The
  previous convention had no case for this and it came up immediately.
- **Publish via GitHub Pages with JSON-LD** rather than relying on
  paste-the-ingredients. Chosen by the user. Note the caveat in Important
  Context: it is unverified that Cronometer reads JSON-LD at all.
- **`build.py` stays stdlib-only.** No `pyyaml`, no `markdown`. The frontmatter
  subset and the markdown dialect are both small and both pinned by `CLAUDE.md`.

## Important Context

**Three harness gates block things a user's verbal approval does not unblock.**
Do not try to work around any of them; plan around them and hand the step over.

- `YOLT refuses this outright: git push: would push to the default branch (main)`
  — commit locally to `main` if you want, but push a branch and open a PR.
- `[Git Destructive]` — blocked `git commit --amend` on a purely local,
  never-pushed commit. Use an additive commit instead.
- `[DNS / Domain / Cert Changes]` — blocked the Route53 script below, *after*
  the user had said "we can run AWS stuff using debedb profile".

**The Pages HTTPS problem is inherited, not local.** `debedb/debedb.github.io`
has `https_certificate.state = bad_authz` on `www.debedb.com` and serves the
fallback `*.github.io` cert. A project repo with no custom domain of its own
inherits that domain, so `recipes` came up as `http://www.debedb.com/recipes/`
with `cname: null`, and `https://debedb.github.io/recipes/` answers `301` down
to that HTTP URL. The four sibling repos that own their own subdomain
(`8values`, `banana`, `elephants`, `kakabychina`) are all `cert=approved`,
`https=true`. The skill `agent-skills:github-pages-cert-badauthz-fresh-subdomain`
documents this exactly, including the fresh-subdomain fix. Read it before
touching any of it.

**USDA FoodData Central hands you a wrong number that looks right.** Searching
`cauliflower raw` returns fdcId `2685573` (Foundation) with **no Energy field at
all**, and fdcId `169986` (SR Legacy) with Energy twice — `104 kJ` *and*
`25.0 KCAL`. So "first hit, read `Energy`" yields either no calories or kJ read
as kcal, a 4.184x error that looks entirely plausible on vegetables. Select on
`unitName == "KCAL"` explicitly. Issue #6 specifies the required refusal
behavior.

**Open Food Facts:** `cgi/search.pl` returns HTML, not JSON. Use
`api/v2/search`. No key needed. Send a descriptive User-Agent.

**Cronometer, verified:** the Recipe Importer is Gold-only; URL import is
documented only for supported recipe sites; paste-the-ingredients is the
documented fallback; there is **no public API** for creating personal recipes.
Whether the importer reads schema.org JSON-LD from an arbitrary domain is
**not documented anywhere** and remains the open question in issue #5.

**Tooling papercuts:** `gh` has no `--no-pager` flag — passing it fails as
`unknown command "view" for "gh"`, which blames the subcommand. Use
`GH_PAGER=cat`. And `gh pr view --json commits` was stale right after a push;
`gh api repos/OWNER/REPO/pulls/N/commits` was truthful.

**`debedb.com` DNS is not in the default AWS profile.** `list-hosted-zones`
there returns `[]`, which reads like "not in Route53" rather than "wrong
account". It is zone `Z2MZ9QFQFZUXQ7` under `--profile debedb`.

**The user edits files in the GitHub web UI.** Commit `ec206e8` deleted the
`## Serving` section from `cauliflower-polenta.md` while the local clone was
stale. `git pull` before editing anything.

## Next Steps

1. **Get `recipes.debedb.com` serving HTTPS.** The agent cannot do this — the
   DNS write is classifier-gated. Ask the user to run the script below with
   `! bash <path>` or to add a Bash permission rule. Done when
   `gh api repos/debedb/recipes/pages --jq '.https_certificate.state'` is
   `approved` and `curl -sS -o /dev/null -w '%{ssl_verify_result}'
   https://recipes.debedb.com/` returns `0`. Note step 2 of the script makes
   GitHub auto-commit a `CNAME` file to `main`, so `git pull` afterwards.

   ```bash
   #!/usr/bin/env bash
   # Give debedb/recipes its own Pages subdomain, routing around the wedged
   # www.debedb.com certificate (https_certificate.state = bad_authz).
   #
   # Mirrors the four sibling subdomains that already work: CNAME -> debedb.github.io, TTL 300.
   # CHANGES STATE. Run only with the local branch pushed: step 2 makes GitHub
   # auto-commit a CNAME file to main, which puts the local clone behind.
   set -euo pipefail

   ZONE=Z2MZ9QFQFZUXQ7          # debedb.com, in AWS profile "debedb"
   HOST=recipes.debedb.com

   echo "== 1. Route53 UPSERT: $HOST CNAME -> debedb.github.io =="
   aws --no-cli-pager --profile debedb route53 change-resource-record-sets \
     --hosted-zone-id "$ZONE" \
     --change-batch '{
       "Comment": "GitHub Pages for debedb/recipes",
       "Changes": [{
         "Action": "UPSERT",
         "ResourceRecordSet": {
           "Name": "recipes.debedb.com",
           "Type": "CNAME",
           "TTL": 300,
           "ResourceRecords": [{"Value": "debedb.github.io"}]
         }
       }]
     }' --query 'ChangeInfo.Status' --output text

   echo "== waiting for DNS to answer =="
   for i in $(seq 1 20); do
     dig @8.8.8.8 +short "$HOST" | grep -q . && break
     sleep 10
   done
   dig @8.8.8.8 +short "$HOST"

   echo "== 2. set it as the repo's custom domain (auto-commits CNAME to main) =="
   echo '{"cname":"recipes.debedb.com"}' | gh api -X PUT repos/debedb/recipes/pages --input -

   echo "== 3. wait for Let's Encrypt (siblings took ~30s) =="
   for i in $(seq 1 24); do
     state=$(gh api repos/debedb/recipes/pages --jq '.https_certificate.state' 2>/dev/null || echo "?")
     echo "  [$i] cert=$state"
     [ "$state" = "approved" ] && break
     sleep 15
   done

   echo "== 4. enforce https (404 here means no cert yet; do not retry blindly) =="
   echo '{"https_enforced":true}' | gh api -X PUT repos/debedb/recipes/pages --input -

   echo "== verify =="
   curl -sS -o /dev/null -w 'https://%{host}  code=%{http_code}  ssl_verify=%{ssl_verify_result}\n' "https://$HOST/"
   gh api repos/debedb/recipes/pages --jq '{url:.html_url, cname:.cname, cert:.https_certificate.state, enforced:.https_enforced}'
   echo
   echo "NOTE: git pull before your next commit - step 2 added a CNAME file to main."
   ```

2. **Get PR #9 reviewed and merged.** It is the convention change plus this
   handoff. Done when merged squashed and `main` builds green.

3. **Answer issue #5's open question.** Once HTTPS works, have the user paste
   `https://recipes.debedb.com/cauliflower-polenta-vegetarian.html` into
   Cronometer's Recipe Importer. Done when the issue records whether 11
   ingredients came back or nothing. Either result is the deliverable. If it
   fails, the paste-the-ingredients path still works and costs nothing.

4. **Build `nutrition.py` per issue #6.** Reuse `build.py`'s existing ingredient
   parser rather than writing a second one. Done when it prints the matched
   `fdcId` and description for every line, selects energy on
   `unitName == "KCAL"`, and **refuses to print a per-serving total** if any
   line failed to match, failed to convert units, or resolved to a record with
   no energy value — naming the offending lines. A partial total is worse than
   none. `FDC_API_KEY` from the environment, `DEMO_KEY` as the fallback,
   documented in `.env.example`, never committed.

## Constraints

- **Never invent a quantity nobody weighed.** This is the repo's central rule.
  `status: tested` means it was cooked, not that every number was measured. An
  eyeballed quantity keeps its starting figure and the cook entry says it was
  eyeballed. `tzimmes.md`'s carrots are the worked example. Inventing precision
  to make a file look finished is the one thing that makes the collection
  worthless.
- **Put the check in the tool, not in a note.** `build.py` refuses rather than
  emitting a hollow Recipe or a one-directional link. Keep that pattern: a
  generator that declines to print a figure it could not compute beats a
  comment reminding someone to look.
- **Verify a refusal by triggering it.** When this session checked the link
  refusal it first printed `exit=0`, which was `tail`'s exit code through a
  pipe, not python's. Re-run unpiped. The real codes are 1 broken, 0 clean.
- `build.py` stays stdlib-only. No new dependencies.
- Ingredient lines are quantity-first, so the block pastes into an importer
  with no rewrite.
- `### YYYY-MM-DD` under `## Cooks` is the only third-level heading in the
  dialect. Anything else needs a renderer change plus a self-test.
- No tabs in multiline strings. No Unicode emoji in code. Both are standing
  user rules; markdown prose may use emoji.
- Ask before changing a recipe's quantities on inference. When this session
  read "honey 1.3oz" as absolute and only later learned date syrup was also in
  the pot, a claim about sweetening being halved went into a commit message and
  had to be corrected in the next one. State the reading explicitly and let the
  user correct it in one word.
