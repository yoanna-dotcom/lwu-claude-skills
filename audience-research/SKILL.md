---
name: audience-research
description: >
  Generic D2C audience research skill. Researches real audience conversations on Reddit and
  TikTok for any brand. Reads BRAND-INTELLIGENCE.md and PERSONA-STRATEGY.md first to search
  for specific people with specific problems — not category keywords. Outputs ranked VOC,
  validated persona findings, and AUDIENCE-VOC.md handover for the strategic-brief-builder.
  Trigger on: "audience research", "find customer language", "Reddit research", "VOC research",
  "what does our audience say", or when PERSONA-STRATEGY.md exists but AUDIENCE-VOC.md does not.
---

# Audience Research Skill

> **Note:** This is a research-heavy skill. Expect significant web searching across platforms.
> `[client-folder]` = the current working directory.

This skill enriches and validates what persona research found in reviews, using real unprompted
platform conversations. It does not start cold — it reads the handover docs first and searches
for specific people, not categories.

**[PRODUCT]** = the client's primary product category, pulled from BRAND-INTELLIGENCE.md.

---

## Step 0 — Read handover documents (mandatory — do not skip)

Read in parallel:
- `[client-folder]/BRAND-INTELLIGENCE.md`
- `[client-folder]/PERSONA-STRATEGY.md`

If neither exists: stop and ask for them. Do not run audience research cold — generic searches
produce generic output.

Extract and hold in context:
- **[PRODUCT]** — the primary product category
- **Persona signals** (priority-ranked) — WHO to search for
- **Exact VOC phrases per persona** — use these as search queries, not category keywords
- **"What to validate in audience research"** per persona — your research questions
- **Top pain points verbatim** — search for these exact phrases on Reddit
- **Failed solutions** — look for these being discussed unprompted
- **Competitor names** — use for comparison searches

---

## Step 1 — Platform research (Sonnet subagent)

**Do NOT run web searches in the main conversation.** Launch a single Sonnet subagent using the
Agent tool (`model: "sonnet"`) to handle all WebSearch calls. This keeps raw search content out
of the Opus context and uses Sonnet's separate rate limits.

**Build the subagent prompt from PERSONA-STRATEGY.md data.** For each persona (in priority order),
include the exact search queries derived from the handover docs.

**Subagent prompt — include all of the following:**

> You are researching real audience conversations on Reddit and TikTok for a D2C brand.
> Search for specific people with specific problems — not category keywords.
> Return ONLY structured findings with verbatim quotes.
>
> **Brand: [brand name]**
> **Product category: [PRODUCT]**
>
> **For each persona below, run ALL search queries in parallel:**
>
> ### [Persona name — from PERSONA-STRATEGY.md]
>
> **Reddit searches (use WebSearch):**
> - `site:reddit.com "[exact VOC phrase from PERSONA-STRATEGY.md]"`
> - `site:reddit.com "[exact pain point phrase from BRAND-INTELLIGENCE.md]"`
> - `site:reddit.com "[competitor name] [problem]"`
> - `site:reddit.com "[PRODUCT] [pain point keyword]"`
>
> **TikTok searches (use WebSearch):**
> - `site:tiktok.com "[exact VOC phrase]"`
> - `site:tiktok.com "[PRODUCT] [persona signal]"`
>
> [Repeat for each persona]
>
> **For every result, collect verbatim — do not paraphrase:**
>
> **Reddit format per quote:**
> - Exact quote (preserve all phrasing)
> - Subreddit
> - Upvotes + comment count (if visible)
> - Context: question / rant / success story / comparison
> - Category: pain point / failed solution / competitor comparison / dream state / persona signal
>
> **TikTok format per video:**
> - Hook (first 3 seconds — exact words)
> - Core message
> - Views, likes, comments (if visible)
> - Top 3 comment themes
> - Creator type
>
> **Return format — use this exact structure:**
>
> ```
> AUDIENCE RESEARCH RESULTS
>
> ## [Persona Name]
>
> ### Reddit
> Pain point quotes:
> 1. "[exact quote]" — r/[subreddit] — [upvotes] — [context type]
>
> Failed solution quotes:
> 1. "[exact quote]" — r/[subreddit] — [context]
>
> Competitor comparison quotes:
> 1. "[exact quote]" — r/[subreddit]
>
> Dream state quotes:
> 1. "[exact quote]" — r/[subreddit]
>
> Persona signal quotes:
> 1. "[exact quote]" — r/[subreddit]
>
> Subreddits with most results: [list]
>
> ### TikTok
> [per video found]
>
> ### TikTok patterns
> Hook styles with best engagement: ...
> Repeating language in comments: ...
> Unmet desires in comments: ...
> Creator formats this persona responds to: ...
>
> [Repeat for each persona]
>
> ## Sources blocked or empty
> [list any that failed — especially TikTok if blocked]
> ```

When the subagent returns, proceed to Step 2 using the structured data it provided.
Do not re-search anything. If TikTok was blocked, note the gap and proceed with Reddit data.

---

## Step 2 — Synthesise, analyse language, and validate

Combine all platform findings into a single synthesis pass:

**Layer 1 — Raw quotes by category** (exact language, no cleanup)

**Layer 2 — Product language analysis:**

| Category | Exact phrases found | Frequency |
|---|---|---|
| Benefits (what they love about [PRODUCT]) | "[exact phrase]" | high/med/low |
| Prior pain points (before using [PRODUCT]) | "[exact phrase]" | high/med/low |
| Features (specific things they mention) | "[exact phrase]" | high/med/low |
| Prior objections (why they hesitated) | "[exact phrase]" | high/med/low |
| Failed solutions (what they tried before) | "[exact phrase]" | high/med/low |

**Benefits of people who DO use [PRODUCT] — priority order:**
Rank by mention frequency. For each: benefit in their words, verbatim quote, frequency signal.

**Pain points of people who DON'T use [PRODUCT] — priority order:**
Rank by mention frequency. For each: pain point in their words, verbatim quote, frequency signal,
what they're doing instead (if mentioned).

Every entry must have a verbatim quote.

**Layer 3 — Validation results:**
For each "what to validate" question from PERSONA-STRATEGY.md:
Confirmed / Partially confirmed / Not found — with evidence.

**Layer 4 — New findings** not in PERSONA-STRATEGY.md — anything surfaced that wasn't in review data.

**Layer 5 — VOC Enrichment Glossary:** 20-30 phrases in the audience's own words, ready for
direct use in hooks.

---

## Step 3 — Save AUDIENCE-VOC.md (handover to strategic-brief-builder)

Save to: `[client-folder]/AUDIENCE-VOC.md`

```markdown
# [CLIENT NAME] — Audience VOC Handover
Generated: [YYYY-MM-DD]

## Enriched VOC per persona (new phrases not in PERSONA-STRATEGY.md)
[per persona — verbatim phrases only]

## Validated findings
[per question from PERSONA-STRATEGY.md: Confirmed / Partially confirmed / Not found]

## New insights (not in review data)
[findings from Reddit/TikTok that reviews didn't surface]

## Failed solutions confirmed on Reddit (hook territory)
| What they tried | Why it failed | Verbatim quote |
|---|---|---|

## Benefits of [PRODUCT] users — ranked
1. [benefit] — "[verbatim]"

## Pain points of non-users — ranked
1. [pain] — "[verbatim]"

## Instructions for strategic-brief-builder
- Angles validated by both review + Reddit evidence: [list]
- New angles surfaced by Reddit not in reviews: [list]
- Angles not confirmed by Reddit: [list — flag for caution]
```

Log the file path. If this file cannot be saved, the run is incomplete.

---

## Step 4 — Notion page (deferred — do not run during research)

Notion sync is handled separately after the research run completes. Do not create a Notion page
during this skill. The CS will run the notion-sync skill when ready.
