---
name: reddit-audience-mining
description: Mine Reddit for unprompted voice-of-customer language, pain points, failed solutions, and golden quotes about a brand, product category, or audience segment. Uses the LWU Perplexity MCP to run brand-specific, category, and competitor searches then synthesises findings into a structured audience intelligence report. Use when the user says "reddit research", "voice of customer", "audience mining", "voc research", "mine reddit", "reddit listening", "/reddit-audience-mining", or asks to find what real customers say about a brand/product/category on Reddit. Do NOT use for Trustpilot scraping (use lwu-research instead) or for running full 5-stage client research (use /lwu-research).
---

# Reddit Audience Mining

## What this skill does

Runs a focused Reddit voice-of-customer mining session for a brand, product category, or audience segment. Synthesises raw Reddit language into brand-specific creative intelligence — not just what people are saying, but what it means for this brand's positioning and what to do about it.

The output is built around the Rise & Fall Audience Research standard: every theme is a named strategic conclusion, every hidden gem has a hook concept attached, and next steps include written copy, not generic advice.

## Required Claude Desktop connectors

- **`perplexity-mcp`** (LWU Cloud Run) — Reddit search via Perplexity Sonar. If not connected, stop immediately.
- **`notion`** — only needed if writing output to a Notion page.

---

## Step 0 — Connector check

Before doing anything else, verify `perplexity-mcp` is available. If not:

> "I can't run this — the `perplexity-mcp` connector isn't enabled in your Claude Desktop. Go to Settings → Connectors and enable it, then try again."

---

## Step 1 — Gather inputs

Use `AskUserQuestion` for the following. Group into 2 question rounds maximum — don't make them answer 5 questions one by one.

**Round 1 — Core brief (ask all at once):**

1. **Research subject** — brand name, product category, or audience segment
2. **Brand brief** — 3-5 sentences: what does the brand sell, who is the core customer, what makes them different, what creative territory are we trying to unlock or validate? (This is what turns generic Reddit findings into brand-specific insights. If the user is unsure, ask for the brief from any existing research doc.)
3. **Research depth:**
   - **Quick scan (3 searches)** — brand-only. ~2 min.
   - **Standard (6 searches)** — brand + category + competitors. ~4 min. Default.
   - **Deep (10 searches)** — full sweep including problem-first, failed solutions, emotional state. ~7 min.

**Round 2 — Optional refinements (ask all at once):**

4. **Competitors** — specific names to look up, or "auto-discover"
5. **Persona focus** — e.g. "new mums", "crossfit regulars", "hot sleepers". Leave blank for general.
6. **Output destination:**
   - Chat only
   - Chat + Notion page (written to Client Research Summaries database)

---

## Step 2 — Confirm and run

Summarise before proceeding:

> "Here's what I'm about to run:
> - Subject: [subject]
> - Brand brief: [brief]
> - Depth: [N] searches — ~[X] min
> - Competitors: [list / auto-discover]
> - Persona focus: [focus / general]
> - Output: [chat / chat + Notion]
>
> Proceed?"

---

## Step 3 — Run the searches

Load the search prompts from `references/prompts.md`. Substitute:
- `{SUBJECT}` — brand/category/segment
- `{BRAND_BRIEF}` — the user's brand brief (used to focus synthesis)
- `{COMPETITORS}` — competitor list or "auto-discover"
- `{PERSONA}` — persona focus or "general audience"

Run via `perplexity_ask`. Collect every response + citation list. Show progress: "✓ 3/6 — Category conversation search done".

**Search plan by depth:**

**Quick (3 searches):**
1. Brand-specific mention search
2. Brand-specific pain points search
3. Brand-specific golden quotes search

**Standard (6 searches) — Quick + :**
4. Category conversation search
5. Competitor mentions search
6. Community language search

**Deep (10 searches) — Standard + :**
7. Problem-first phrasing search
8. Failed solutions search
9. Persona signal search
10. Emotional state search

---

## Step 4 — Synthesise

After all searches complete, synthesise into the structured output. The synthesis must go beyond reporting — it must interpret findings through the brand brief.

**Synthesis rules:**

1. **Brand-first interpretation.** Every section should answer "so what for [brand]?" not just "here's what Reddit says." The brand brief is your filter.

2. **Key Themes are strategic conclusions, not observations.** A theme is NOT "people complain about price." It IS "The affordable luxury gap is wide open — the market has two poles: cheap synthetics and overpriced DTC brands. [Brand] sits exactly in the gap, but nobody knows it yet." Each theme must state: the finding, why it matters, and the creative implication.

3. **Hidden Gems must include ready-made hook ideas.** Each gem = one specific, high-signal moment from the research (a quote, a thread, a statistic) + the ad it would make + the persona it maps to + the messaging bucket. If you can't attach a hook idea to it, it's not a gem.

4. **Capture engagement signals.** When Perplexity reports upvote counts or "X upvotes", include them. High upvote counts are validation — they prove the pain point resonates, not just that it exists.

5. **Quotes must be verbatim.** Never paraphrase. If Perplexity didn't name a subreddit, write "source not specified."

6. **Suggested Next Steps = written hooks, not advice.** Each next step must include: a written hook concept (the actual words), which persona to target, which format to test first (UGC/brand video/static), and one sentence on why this specific data justifies it.

---

## Step 5 — Output

### Format — both chat and Notion output use this structure:

```markdown
# Reddit Audience Mining — [Subject]
*[Depth] | [N] searches | [Date]*

---

## Why This Research Matters
[2-3 sentences grounding the research in the brand brief — what gap does this brand fill, and why is Reddit the right place to validate it? This is not boilerplate. It should be specific to this brand and this moment.]

**Subreddits mined:** [list]
**Threads read:** [number if known]

---

## Key Themes
[4-6 themes. Each theme follows this format:]

**[N]. [Theme name — a strategic conclusion, not a description]**
[2-4 sentences: the finding, why it matters for this brand specifically, and the creative implication. Minimum 1 verbatim quote with subreddit + upvote count if available.]

---

## Hidden Gems
[5-7 specific high-signal moments. Each gem follows this format:]

**[Gem name — a short, evocative label]**
[The verbatim quote or specific finding that makes this a gem, with subreddit source and upvote count if known.]

**Hook idea:** [A written-out ad hook based directly on this gem — actual copy, not a description of the copy.]
**Persona:** [which persona this maps to]
**Messaging bucket:** [Pain Point / Trigger Moment / Competitor Gap / Benefit / Social Proof / Misconception / Objection]

---

## Coverage Summary

| Opportunity | # Quotes | Top Messaging Bucket | Quality |
|---|---|---|---|
| [opportunity] | [N] | [bucket] | [Strongest / Strong / Moderate — 1 sentence on why] |

> [1-2 sentence callout: which 2-3 categories are richest for immediate creative production and why.]

---

## Community Language
[8-15 exact verbatim phrases in a grouped table or list. Group by theme: "Describing the problem", "Describing success", "Expressing frustration", "What they want". Include subreddit source for each.]

---

## Pain Points (ranked by frequency)

[For each pain point:]
**[N]. [Pain point label]** *(frequency indicator)*
"[Verbatim quote]" — r/[subreddit] [upvotes if known]
"[Verbatim quote]" — r/[subreddit]

---

## Failed Solutions
[For each failed solution:]
- **[Solution name]** — [why it failed, in their words]. "[Verbatim quote]" — r/[subreddit]

---

## Problem-First Phrasing
*How people describe the problem before they know [brand] exists*
- "[Phrase]"
[Include why this is useful for cold-audience hook writing.]

---

## Persona Signals
- **Demographics:** [findings with supporting evidence]
- **Lifestyle:** [findings with supporting evidence]
- **Psychographics:** [findings with supporting evidence]
- **Digital footprint:** [subreddits + other platforms]

---

## Golden Quotes
*Verbatim, high-signal, creative-ready*

[Number each. For each:]
"[Full verbatim quote]" — u/[username if available], r/[subreddit] [[N upvotes if known]]

---

## Competitor Snapshot

| Brand | Reddit Sentiment | What they're known for | Weakness to exploit |
|---|---|---|---|
| [Brand] | [Very positive / Positive / Mixed / Negative] (X%) | [Positioning in community] | [Specific gap or complaint] |

**Key gap:** [1-2 sentences on what no competitor owns that this brand could claim.]

---

## Gaps & Caveats
[Honest flagging of thin results, failed searches, low-confidence findings, or areas where Reddit data was limited.]

---

## Suggested Next Steps

[3-5 concrete, specific recommendations. Each must follow this format:]

**[N]. [Action title]**
**Hook to test:** *"[Written-out hook — actual copy]"*
**Persona:** [which persona]
**Format:** [UGC / brand video / static / carousel]
**Why:** [1-2 sentences connecting this directly to the research finding that justifies it — quote the specific Reddit signal.]
```

---

### Always save REDDIT-VOC.md (handover to d2c-persona-strategist)

After producing the chat output, save a condensed handover file for downstream skills:

```
Save to: [client-folder]/REDDIT-VOC.md
```

```markdown
# [Brand Name] — Reddit VOC Handover
Generated: [YYYY-MM-DD] | Source: reddit-audience-mining | Depth: [standard/deep] | Searches: [N]

---

## Key Themes (strategic conclusions)
[Copy the Key Themes section — each theme with finding, brand implication, and top verbatim quote]

---

## Pain Points (ranked by frequency)
[Copy full pain points section with verbatim quotes and subreddit sources]

---

## Failed Solutions
[Copy full failed solutions section with verbatim quotes]

---

## Community Language
[Copy full community language section — grouped verbatim phrases]

---

## Golden Quotes (creative-ready)
[Copy all golden quotes with attribution]

---

## Hidden Gems (with hook ideas)
[Copy all hidden gems with hook ideas and persona mapping]

---

## Competitor Gaps
[Copy competitor snapshot table + key gap statement]

---

## Persona Signals
[Copy persona signals: demographics, lifestyle, psychographics, digital footprint]

---

## Instructions for downstream skills

**-> d2c-persona-strategist:** Use pain points, failed solutions, and community language to ground persona definitions in real audience language — not just review language. Reddit surfaces how people talk BEFORE they buy (pre-purchase language), while reviews capture post-purchase language. Both are needed. Use persona signals to validate or challenge review-derived persona splits. Use golden quotes in hook banks.

**-> strategic-brief-builder:** Hidden gems with hook ideas are ready-made creative angles. Competitor gaps identify whitespace. Community language feeds directly into hook writing.
```

Log the file path. This file is read by the d2c-persona-strategist skill if it exists.

---

### If output destination = Chat + Notion page:

After the chat output, create a Notion page:
1. Fetch Client Research Summaries database: `286f6443-7f9b-800b-a341-d3980fd99d6f`
2. Create page titled: `[Subject] — Reddit Audience Mining — [YYYY-MM-DD]`
3. Populate with the full structured output in Notion blocks
4. Return the Notion URL at the bottom of the chat response

---

## Constraints

- **Never fabricate quotes.** Every quote must come from an actual Perplexity response with a citation. If a section is thin, say so.
- **Never invent subreddit sources.** Write "source not specified" if Perplexity didn't name one.
- **Keep quotes verbatim.** Reddit language is the point. Do not edit.
- **Always run all searches for the chosen depth.** Don't stop early.
- **Every Hidden Gem must have a hook idea.** If you can't write a hook from it, it's not a gem — put it in Golden Quotes instead.
- **Next Steps must include written copy.** "Test hooks about X" is not acceptable. Write the hook.
- **Surface gaps honestly.** Thin data on a niche brand is a real finding — report it, don't pad.

---

## Reference files

- `references/prompts.md` — search prompts and synthesis guidance. Load on demand at Step 3.
