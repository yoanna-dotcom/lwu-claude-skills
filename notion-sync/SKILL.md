---
name: notion-sync
description: >
  Batch-syncs all research outputs to Notion in a single run. Reads local .md files
  (BRAND-INTELLIGENCE.md, PERSONA-STRATEGY.md, AUDIENCE-VOC.md, COMPETITOR-BRIEF.md,
  STRATEGIC-BRIEF.md) and creates/updates Notion pages for each. Run this after all
  research skills are complete. Trigger on: "sync to Notion", "push to Notion",
  "update Notion", "notion sync", or "run notion-sync".
---

# Notion Sync

> `[client-folder]` = the current working directory.

This skill creates Notion pages for all research outputs in a single batch run.
It reads local .md files only — no web scraping, no analysis, no re-derivation.

---

## Step 0 — Find the client workspace in Notion

Use `notion-search` with the brand name (inferred from BRAND-INTELLIGENCE.md or the folder name).
If found, create all pages inside the client's parent page. If not found, create at workspace root.

---

## Step 1 — Scan for available outputs

Check which files exist in `[client-folder]`:

| File | Notion page to create |
|---|---|
| `research/brand-research-*.md` | Brand + Product Research |
| `BRAND-INTELLIGENCE.md` | (included in above) |
| `PERSONA-STRATEGY.md` | Audience Research & Persona Strategy |
| `AUDIENCE-VOC.md` | Audience VOC Research |
| `COMPETITOR-BRIEF.md` | Competitor Intelligence |
| `STRATEGIC-BRIEF.md` | Strategic Brief |

Only create pages for files that exist. Note any missing files at the end.

---

## Step 2 — Create Notion pages

Create each page using a single `notion-create-pages` call per document. Keep pages compact —
Notion is the quick-reference, not a full duplication — EXCEPT for Brand + Product Research,
which pushes the full deep report so all research is documented in Notion.

### Brand + Product Research page

**Title:** `[CLIENT NAME] — Brand + Product Research [YYYY-MM-DD]`

**Source:** Read `research/brand-research-*.md` (the full deep research file, NOT BRAND-INTELLIGENCE.md).
Push the COMPLETE report to Notion — do not summarise or compress. This is the team's primary
research reference and must contain all verbatim quotes, tables, and analysis.

BRAND-INTELLIGENCE.md is the inter-skill handover file that downstream skills read. It stays
local and is NOT what goes to Notion. The full report goes to Notion.

**Structure — push all of the following from the full report:**

1. Callout (blue): "Generated: [date] | `/d2c-research` deep pass"
2. H1: Stage 1 — Brand Research (full output: overview, TOV, positioning, formality table, brand story, USPs with verdicts, mechanisms, proof points, summary statement)
3. H1: Stage 2 — Product Research (full output: per-product tables)
4. H1: Stage 3 — Review Mining (full output: ranked pain points, failed solutions, benefits, persona signals, VOC glossary, review mining summary)
5. H1: Stage 4 — Reddit Research (full output: brand mentions, category pain points, failed solutions, competitor sentiment, dream states, subreddit map, Reddit vs Review comparison, Reddit summary)
6. H1: USP → Buyer Fear Map (full table with review + Reddit evidence columns)
7. H1: Language to Avoid (full section including "do not write like" rule)
8. Callout (yellow): "Next step: Run d2c-persona-strategist"

### Persona Strategy page

**Title:** `[CLIENT NAME] — Audience Research & Persona Strategy`

1. Callout (blue): "Full interactive report: [Brand Name] Audience Research.html"
2. H1: Persona Summary
3. Per persona: H2 with archetype name + tagline, callout with who she is, toggles for pain points / hooks / formats
4. H2: Cross-Persona Insights
5. Callout (yellow): "Next step: Run audience-research and competitor-research"

### Audience VOC page

**Title:** `[CLIENT NAME] — Audience VOC Research [YYYY-MM-DD]`

1. Callout (blue): "Full report: [path]"
2. H2: Enriched VOC per persona
3. H2: Validated Findings
4. H2: New Insights from Reddit/TikTok
5. H2: Failed Solutions Confirmed
6. H2: VOC Enrichment Glossary

### Competitor Intelligence page

**Title:** `[CLIENT NAME] — Competitor Intelligence [YYYY-MM-DD]`

1. Callout (blue): "Full report: [path]"
2. H2: Per-Competitor Summary
3. H2: USP Whitespace Map
4. H2: Differentiation Strategies
5. H2: Competitor Failure Quotes — Hook Territory
6. H2: Cross-Competitor Emotional Pattern

### Strategic Brief page

**Title:** `[CLIENT NAME] — Strategic Brief [YYYY-MM-DD]`

1. Callout (blue): "Full brief: [path]"
2. H2: The One Thing
3. H2: Tiered Angles — Tier 1 only
4. H2: Persona-to-Hook Map (condensed)
5. H2: Hard Constraints
6. H2: Saturated Angles
7. H2: Priority SKU Queue
8. Callout (red): "MUST-READ-SCRIPTING.md must be read before any scripting session"

---

## Step 3 — Log results

Output a summary:

```
Notion sync complete — [CLIENT NAME]

Pages created:
- [Page name] — [Notion URL]
- [Page name] — [Notion URL]

Missing (no local file found):
- [file name]
```
