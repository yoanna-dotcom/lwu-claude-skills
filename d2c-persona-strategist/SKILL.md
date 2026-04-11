---
name: d2c-persona-strategist
description: >
  Build a full D2C audience persona strategy document from customer review data (CSV). Use this skill whenever a user uploads customer reviews, asks for audience research, persona building, VOC analysis, DIP research, or wants to understand who their D2C brand's buyers are and how to reach them. The skill ingests raw review CSVs, synthesises Voice of Customer data into 2-4 micro-personas, layers on a D2C creative strategy framework (TE mapping, cognitive bias, veilance zones, self-concept anchors, labelled hook banks), and outputs a branded interactive HTML report plus an optional Notion page. Trigger this skill any time the words "persona", "audience research", "VOC", "DIP", "customer reviews", "review analysis", or "who is our customer" appear in a request — even if the user doesn't specifically ask for an HTML file.
---

# D2C Persona Strategist

> `[client-folder]` = the current working directory. All file reads and saves use this path.

This skill turns raw customer review data into a complete audience persona strategy document — the kind a D2C growth agency would use to brief creative, write ad hooks, and align the whole team on who the real buyer is.

---

## TOKEN EFFICIENCY ARCHITECTURE — READ THIS FIRST

This skill runs in **two separate invocations**. Analysis is done once, saved to JSON, then a second run builds all outputs from that JSON. Never collapse these into a single pass.

**Operating modes:**

### Run 1 — Analysis pass (default trigger)
Steps 0 through 5.5. Reads BRAND-INTELLIGENCE.md, ingests reviews, synthesises personas, builds emotional layers, trigger events, hook bank, coverage check, saves to JSON.
**HARD STOP after Step 5.5.** Output the handover message defined in Step 5.5. Do not proceed to HTML, Notion, or PERSONA-STRATEGY.md.

### Run 2 — Output pass (separate trigger)
Triggered by: "Run 2", "Run 2 — [brand name]", "build the outputs", "generate the HTML", "create the Notion page"
Steps 6 through 7.5. Reads the saved JSON. Builds HTML, Notion page, PERSONA-STRATEGY.md. Do not re-derive any insights — read from JSON only.

### Deck generation (separate trigger — unchanged)
Only runs when the CS explicitly says: "generate the deck", "make the presentation", "create the client deck", "I need the slides". Never auto-generate on Run 1 or Run 2.

---

## Run 2 — Output pass

**Triggered by:** "Run 2", "Run 2 — [brand name]", "build the outputs", "generate the HTML", "create the Notion page"

**Step R2.0 — Find and read JSON:**
- Search the outputs folder for `[Brand Name]-persona-data.json`
- If not found: stop and tell the CS: "Run 1 JSON not found. Please complete Run 1 first before triggering Run 2."
- Do not re-run analysis. Do not re-derive insights from reviews.

**Then run Steps 6 → 7 → 7.5 in sequence.**

**Model note:** Run 2 is output generation (HTML + Notion + PERSONA-STRATEGY.md). It reads
from saved JSON and does not require strategic reasoning. Use Sonnet for Run 2 to preserve
Opus rate limits — trigger Run 2 in a new conversation or delegate to a Sonnet subagent.

---

## When you're invoked

The user will provide:
- **BRAND-INTELLIGENCE.md** (from the d2c-research skill — read this first if it exists)
- **ACCOUNT-AUDIT.md** (from the audit-interpret skill — read this second if it exists). Contains ROAS per territory, spend allocation, persona gaps, creative health scores, and strategic opportunities.
- A CSV of customer reviews (columns: `review_rating`, `review_title`, `review_text` — adapt to whatever columns exist)
- The brand name (or infer from the data)
- Optionally: brand category
- Optionally: Foreplay board name(s) for creative references

If BRAND-INTELLIGENCE.md exists → read it before anything else. It contains confirmed USPs, ranked pain points, persona signals with priority scores, and instructions for this phase. Do not re-derive what is already confirmed there.

If ACCOUNT-AUDIT.md exists → read it after BRAND-INTELLIGENCE.md. It contains the performance data that determines which personas are commercially important vs just loud in reviews. A persona with 2% of reviews but 8-12x ROAS is more valuable than a persona with 60% of reviews but generic product messaging.

If REDDIT-VOC.md exists → read it after ACCOUNT-AUDIT.md. It contains pre-purchase audience language from Reddit (how people talk BEFORE they buy), which complements the post-purchase language in the CSV reviews. Pain points, failed solutions, community language, and persona signals from Reddit ground personas in real audience conversations, not just buyer feedback.

If Foreplay boards are specified → run Foreplay step first (after reading BRAND-INTELLIGENCE.md).
If not specified → skip Foreplay step entirely.

---

## Step 0A — Read BRAND-INTELLIGENCE.md (run before everything else if file exists)

```
Read: [client-folder]/BRAND-INTELLIGENCE.md
```

Extract and hold in context:
- Persona signals (priority-ranked) — these become your persona hypotheses
- Top pain points verbatim — ground every persona's pain language in these exact phrases
- Top failed solutions verbatim — this is the most underused creative territory; every persona must have a failed solutions section
- Confirmed USPs — only Proven USPs can be used in persona creative angles
- Three Consistent Truths — these apply across all personas
- Instructions for this phase (bottom of BRAND-INTELLIGENCE.md)

If BRAND-INTELLIGENCE.md does not exist: **HARD STOP.** Do not proceed. Tell the CS:

> "BRAND-INTELLIGENCE.md is missing. This file is produced by the d2c-research skill and contains confirmed USPs, ranked pain points, and persona signals that this skill needs to produce qualified output. Without it, personas will be generic and category-derived — not brand-specific. Please run `/d2c-research` first, then re-trigger this skill."

Do not offer to proceed without it. Do not fall back to reviews-only mode. The whole point of the handover chain is that each skill builds on confirmed findings from the previous one. Skipping this produces the kind of surface-level output that any free tool can generate.

---

## Step 0B — Read ACCOUNT-AUDIT.md (run after BRAND-INTELLIGENCE.md if file exists)

```
Read: [client-folder]/ACCOUNT-AUDIT.md
```

Extract and hold in context:
- **ROAS per territory/persona** — which audience segments actually drive return, not just review volume
- **Spend allocation** — % of spend per campaign/territory. Underfunded high-ROAS territories = highest priority personas
- **Persona gaps from audit** — which personas have zero dedicated creative, which are seasonal-only, which are accidental
- **Creative health scores** — overall account health, format mix, concentration risk
- **Strategic opportunities** — the audit's prioritised list of what to fix first
- **Risk signals** — audience saturation, format dependency, concentration fragility

**How this changes persona prioritisation:** The audit data overrides pure review-volume ranking. A persona with 7% of reviews but 8-12x ROAS and zero dedicated creative (like a Culture Curator) outranks a persona with 66% of reviews but surface-level product messaging (like a Matchday Loyalist). The priority score formula in Step 2 accounts for this.

If ACCOUNT-AUDIT.md does not exist: **Do not hard stop.** Proceed with BRAND-INTELLIGENCE.md + reviews, but flag to the CS:

> "ACCOUNT-AUDIT.md not found. Persona priority scoring will be based on review data and brand research only — not account performance. For performance-weighted priorities, run `/audit-interpret` first."

---

## Step 0C — Read REDDIT-VOC.md (run after ACCOUNT-AUDIT.md if file exists)

```
Read: [client-folder]/REDDIT-VOC.md
```

Extract and hold in context:
- **Pain points with verbatim Reddit language** — these are PRE-purchase pain points (how people describe problems before they know the brand exists). Layer these onto the post-purchase pain points from reviews.
- **Failed solutions with Reddit evidence** — often more detailed than review data because Reddit users explain WHY something failed, not just THAT it failed
- **Community language** — exact phrases people use on Reddit. These feed directly into hook banks and should be preferred over review language for cold-audience hooks (Reddit = how they talk before buying; reviews = how they talk after buying)
- **Golden quotes** — creative-ready verbatim quotes for hooks and ad copy
- **Hidden gems with hook ideas** — pre-written hook concepts grounded in Reddit signals. Integrate into the persona hook bank.
- **Persona signals** — demographics, psychographics, lifestyle, digital footprint from Reddit. Use to validate or challenge the persona splits derived from reviews.
- **Competitor gaps** — what no competitor owns. Feed into persona positioning.

If REDDIT-VOC.md does not exist: proceed without it. Reddit data enriches personas but is not required. Note in output: "Reddit VOC not available — personas grounded in review data + brand research only. Run `/reddit-audience-mining` to add pre-purchase language."

---

## Step 0 — Foreplay creative references (ONLY if boards specified)

The CS will name specific Foreplay board(s) in the prompt. Do not search broadly or guess.

```
get_boards()  →  match the named board(s) exactly
get_board_ads(board_id, limit=10)  →  max 10 ads per board
```

Extract ONLY these four fields per ad: `thumbnail_url`, `brand`, `format` (static/video/carousel/UGC — infer if needed), `headline` (first line of copy if available).

Store as: `foreplay_refs = [{brand, format, thumbnail_url, headline}, ...]`

**Hard limit**: 10 ads max per board. Extract only four fields. This step must cost under 2K tokens. If a board returns nothing, log it and continue. Do not retry or broaden the search.

---

## Step 1 — Ingest and parse the reviews

```python
import csv

with open('reviews.csv', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    reviews = list(reader)

print(f"Columns: {reader.fieldnames}")
print(f"Total reviews: {len(reviews)}")
```

Read ALL reviews — do not sample. For 200+ reviews, process in chunks using Python (not the Read tool, which truncates).

---

## Step 1.5 — Identify Macro Personas

Before building micro personas, identify the **2-3 macro persona segments** in the review data. Macros are defined by **primary purchase motivation** — the fundamental reason someone is buying, not the specific emotional flavour.

Common D2C macro segments (use as starting hypotheses, validate against the actual review data):
- **Self-Buyer** — purchasing for their own use (splits further by motivation: functional need vs identity expression)
- **Gift/Proxy Buyer** — purchasing for someone else (different decision framework, different objections, different success metric)
- **Problem Solver** — purchasing to fix a specific, named problem
- **Identity Buyer** — purchasing to express or reinforce who they are

**How to identify macros:**
1. Scan all reviews for the **"for whom"** signal: "I bought this for myself" vs "I bought this for my husband" vs "I needed something to fix X"
2. Group reviews by this primary motivation — most D2C brands have 2-3 macros
3. If a macro contains <10% of reviews, fold it into the closest match

**For each macro, define:**
- **macro_code**: M1, M2, M3
- **macro_name**: e.g. "The Self-Buyer", "The Gift Buyer"
- **shared_motivation**: one sentence — what unites everyone in this macro
- **shared_messaging**: 2-3 messaging themes that work across ALL micros within this macro. These become macro-level ad angles that serve multiple micro personas simultaneously.
- **shared_objections**: 1-2 objections every micro within this macro shares
- **approximate_split**: % of reviews in this macro

**Why this matters:** Macros give the CS a shared messaging layer. Without it, every micro is treated as independent — wasting creative budget on messaging that's redundant at the motivation level. A macro-level ad (e.g. "for fans who buy for themselves") can serve 3 micro personas simultaneously, while micro-level ads target one.

Macros also prevent a common failure mode: micro personas that are too similar. If two micros share the same macro AND the same vailance zone AND the same self-concept anchor, they're not genuinely distinct. The macro layer makes this visible before creative production begins.

**BRAND-INTELLIGENCE.md integration:** If persona signals exist in BRAND-INTELLIGENCE.md, map them to macros first. The persona signals from d2c-research already contain purchase motivation clues — use them as the starting point for macro identification, then validate against the full review set.

Hold the macro definitions in context. They feed into Step 2 (micro personas nest under macros) and Step 5.5 (JSON schema).

---

## Step 2 — Synthesise Micro Personas (within macros)

Read all review texts. Identify dominant themes across:
- Emotional triggers (why they bought)
- Failed solutions (what they tried before)
- Desired outcomes (what they wanted to feel)
- Proof signals (what built trust)
- Language patterns (exact repeating phrases)

Within each macro from Step 1.5, identify **1-3 micro personas** by their specific emotional driver, purchase context, or identity relationship with the product. Total micros across all macros: 2-4. Aim for 15-40% per micro. Fold any micro under 10% into the closest match within the same macro.

**Each micro must be meaningfully distinct from other micros in the same macro.** If two micros share the same vailance zone AND self-concept anchor, they're not distinct enough — merge them or redefine the split.

For each persona define:
- **macro_code**: M1, M2, etc. (which macro this micro belongs to)
- **code**: P1.1, P1.2, etc.
- **colour theme**: rose / purple / teal / amber / slate
- **archetype name**: e.g. "The Skin Reactor"
- **tagline**: one-line emotional drive
- **who she is**: 2-3 vivid sentences (age, context, how she found the brand)
- **review_count** + **percentage**: approximate cluster size
- **priority score**: weighted composite of four inputs. Higher score = higher creative priority.

**Priority score formula:**
1. **Review cluster %** (0-30 pts): raw share of reviews belonging to this persona
2. **Pain point intensity** (0-20 pts): frequency and severity of pain language in reviews
3. **Reddit/BRAND-INTELLIGENCE signal** (0-15 pts): volume of unprompted mentions in external sources
4. **Account performance multiplier** (0-35 pts, from ACCOUNT-AUDIT.md if available):
   - ROAS for this persona's territory: >5x = 35pts, 3-5x = 25pts, 1-3x = 15pts, <1x = 5pts
   - Creative gap bonus: +10pts if persona has ZERO dedicated creative despite proven ROAS signal
   - Spend underweight bonus: +10pts if persona's % of spend is <25% of its % of ROAS contribution
   - Always-on penalty: -10pts if persona already has well-funded, year-round creative

If ACCOUNT-AUDIT.md is not available, the performance multiplier section scores 0 and the score is based on review + brand research data only. Flag this in the output.

**Why this matters:** Without performance weighting, a persona that dominates reviews (e.g. 66% of reviews) will always outrank a persona with fewer reviews but massively better ROAS (e.g. 7% of reviews, 8-12x ROAS). The account performance multiplier corrects this by rewarding underserved, high-performing segments.

Extract for each persona:
- Top 3 pain points — must use verbatim language from reviews or BRAND-INTELLIGENCE.md. No paraphrasing.
- Desired outcome — in their own words
- **Failed solutions** (mandatory — do not skip): what they tried before buying. This is the most valuable creative territory. Minimum 2 specific failed solutions per persona with verbatim language. If reviews don't surface this clearly, note it as a gap.
- Purchase triggers — what finally made them buy
- Before → After state: one sentence each. Before = the specific situation/feeling before purchase. After = the specific change they describe in reviews. Both must be grounded in review evidence.
- 5-8 verbatim VOC quotes (exact language, preserve all phrasing)
- Language patterns (5-8 phrases in her own words)
- What to validate in audience research: 2-3 specific questions this persona raises that Reddit/TikTok research should answer

**Emotional depth layer (required for every persona):**

List 3-5 specific emotional or psychological frustrations this persona experiences before using the product. For each:
- The frustration in their words (verbatim from reviews where possible)
- The core human desire it connects to: confidence / belonging / freedom / self-worth / attractiveness / security / approval / competence / empowerment — pick the closest match and explain WHY this specific desire is being threatened or blocked
- 1-2 story lines that agitate this emotion in a way that feels personal and real — written in the persona's voice, not the brand's

Do not name the framework. Describe the underlying drive in plain language.

Example format:
> Frustration: "I've tried everything and nothing works"
> Desire blocked: Competence — she needs to feel capable of solving her own problems. When repeated failure happens, it signals to her that the problem is her, not the product.
> Story line: "You follow every instruction. You do everything right. And it still doesn't work. At some point you stop blaming the product."

---

## Step 2.5 — Emotional Language Surface (lightweight)

Run across ALL reviews, not per persona. Surface only what hasn't been captured per-persona above.

**5-7 emotionally loaded phrases the brand hasn't used yet:**
- "[exact phrase]" — context: [one sentence on when/why this appears in reviews]

These feed directly into the VOC Enrichment Glossary in PERSONA-STRATEGY.md and into hook writing. Do not write full emotional theme analysis here — that is the audience-research skill's job.

---

## Step 3 — Apply the D2C Creative Strategy Framework

For each persona. Read `references/framework.md` for full definitions.

**TE Map**: Trigger / Exploration / Evaluation / Purchase. Write awareness level + 1-sentence creative implication.

**Cognitive Bias**: Primary + secondary from: Loss Aversion / Authority Bias / Identity Reinforcement / Social Proof / Switching Cost / Bandwagon. Write 1-sentence creative implication.

**Vailance Zone**: Open zone (where she starts) + close zone (where she needs to be). Write 1 sentence on what the ad must do to move her.

**Self-Concept Anchor**: Actual Self / Ideal Self / Ought Self. Write narrative note on how the ad bridges from Actual to Ideal.

**Language Intensity**: Low / Medium / High. See `references/framework.md` for full definitions. Write 1 sentence on why this intensity matches this persona's funnel stage and emotional zone.

---

## Step 3.5 — Trigger Events (Schwartz + Ogilvy)

For each persona: identify the specific moments that move them from passive to active demand.
Two layers — both required.

**Layer 1 — Psychological triggers (Schwartz-style):**
What internal shifts, pain flares, or emotional states suddenly make this product feel urgent?

For each trigger:
- The trigger: what happens internally (the thought, the emotion, the breaking point)
- Why it creates urgency: what psychological need becomes impossible to ignore
- Emotional state that signals it: "I can't take this anymore" / "I need to do something about this" / "I'm done settling"
- Ad angle: how this trigger becomes the opening line or concept

Minimum 3 psychological triggers per persona.

**Layer 2 — Contextual triggers (Ogilvy-style):**
What external events, life moments, or seasonal contexts create natural buying windows?

For each trigger:
- The event or context: specific and real (e.g. "moving into a new home", "hosting for the first time", "just got promoted", "January reset")
- Why it creates receptivity: what changes in their mindset or priorities at this moment
- Where they are when they're most receptive: platform, format, time of day
- Ad angle: how this context becomes the opening frame or targeting signal

Minimum 3 contextual triggers per persona.

**Output format per trigger:**

> **Trigger:** [name it clearly]
> **Why it matters:** [psychological need or context shift]
> **Emotional state / moment:** [the exact feeling or situation]
> **Ad angle:** [one-line direction for how this becomes a hook or concept]

These triggers feed directly into the hook bank and creative format selection.

---

## Step 4 — Build the Hook Bank

For each persona: **8-10 hooks** mapped to emotional territories. Label each clearly.

| Label | Type | Emotional territory |
|---|---|---|
| **FEAR** | Loss / risk / worst case | shame / regret / inadequacy / missing out |
| **DESIRE** | Dream state / aspiration | confidence / belonging / freedom / approval |
| **IDENTITY** | Who they want to be | self-worth / competence / empowerment |
| **TRIGGER** | The moment that flips the switch | pulled from Step 3.5 psychological triggers |
| **PROOF** | Cognitive shortcut | authority / social proof / before-after evidence |

For each hook: one sentence, 15-25 words, written as an opening line. No brand name. Use exact phrases from the VOC. Tag the emotional territory it targets.

**Emotional territory coverage check:** Ensure the hook bank covers at least 4 different emotional territories. If 70%+ of hooks target the same emotion, the bank is psychologically redundant before testing begins.

**Hook testing rule:** Never write variations that say the same thing in different words. Each hook must attack a different emotional input. If one wins and you cannot explain why, the test was wasted.

---

## Step 5 — Creative Formats

For each persona: 3-4 ad formats. For each:
- Format name
- Brief description of what it looks like
- Why it works for this persona (link to bias, zone, or funnel stage)

Write a **brief skeleton** for the strongest format: Hook → Problem → Failed solutions → Solution → CTA, with self-concept arc and vailance zone transition written in.

---

## Step 5.1 — Creative Coverage Check

Run after all personas are built. Map each persona across three dimensions:

| Macro | Persona | Vailance Zone (open) | Self-Concept Anchor | Language Intensity |
|---|---|---|---|---|
| M1 | [P1.1 name] | Zone [X] | [Actual/Ideal/Ought] | [Low/Med/High] |

**Check for clustering — two levels:**
1. **Cross-macro:** If 70%+ of personas share the same vailance zone or self-concept anchor, the creative library will be psychologically redundant before it is built. Meta penalises creative similarity with higher CPMs and suppressed reach.
2. **Within-macro:** If all micros within a single macro share the same vailance zone AND self-concept anchor, they are not meaningfully distinct — merge them or redefine the split. Micros within a macro should differ on at least one psychological dimension.

**Minimum coverage standard:** Ensure at least one persona operates in a positive zone (Zone 1 or 2) and at least one in a negative zone (Zone 3 or 4). If all personas open in Zone 3-4, note it explicitly in the cross-persona insights and flag an aspiration-led Zone 1-2 concept as the first recommended test.

Include the coverage table in `cross_persona` in the JSON and surface it in the Strategy Overview tab of the HTML.

---

## Step 5.5 — SAVE STRUCTURED DATA AS JSON (required before any output)

This is the single source of truth for all downstream outputs. Generate this before writing any HTML, Notion, or PPTX.

```python
import json

persona_data = {
    "brand": "[Brand Name]",
    "date": "[YYYY-MM-DD]",
    "audit_data_available": True,  # False if ACCOUNT-AUDIT.md was not found
    "foreplay_refs": foreplay_refs,  # [] if Step 0 was skipped
    "macros": [
        {
            "macro_code": "M1",
            "macro_name": "The Self-Buyer",
            "shared_motivation": "Purchasing for their own use — identity or functional need",
            "shared_messaging": ["theme 1 that works across all M1 micros", "theme 2"],
            "shared_objections": ["objection shared by all M1 micros"],
            "micro_codes": ["P1.1", "P1.3", "P1.4"],
            "approximate_split": 75  # % of reviews
        }
        # one entry per macro
    ],
    "chart_data": {
        "persona_distribution": [
            {"name": "P1.1 The Archetype", "value": 42, "color": "#f43f5e"},
            # one entry per persona — value is % of total reviews
        ],
        "funnel_stages": [
            {"stage": "Trigger", "count": 0},
            {"stage": "Exploration", "count": 2},
            {"stage": "Evaluation", "count": 1},
            {"stage": "Purchase", "count": 0},
        ],
        "vailance_zones": [
            {"zone": "Zone 2 - Curious", "count": 1},
            {"zone": "Zone 3 - Frustrated", "count": 2},
        ],
        "content_split": [
            {"format": "UGC Testimonial", "recommended": 3},
            {"format": "Before/After", "recommended": 2},
            # aggregated recommended count across all personas
        ]
    },
    "personas": [
        {
            # full persona object — see references/html-template-notes.md for complete schema
        }
    ],
    "cross_persona": {
        "hook_testing_priority": "...",
        "shared_language": ["phrase 1", "phrase 2"],
        "whitespace": "...",
        "creative_hypothesis": "..."
    }
}

with open('[Brand Name]-persona-data.json', 'w') as f:
    json.dump(persona_data, f, indent=2)
```

Compute `chart_data` numbers here in Python — do not derive them in the HTML. The HTML reads static numbers only.

Save to the outputs folder. Always confirm the file was written before proceeding.

---

**HARD STOP — Run 1 complete.**

Output exactly this message to the CS:

```
✅ Run 1 complete — [Brand Name] persona analysis saved.

JSON file: [Brand Name]-persona-data.json
Macros: [M1 name] ([X%]) · [M2 name] ([X%])
Personas: [P1 name] (M1) · [P2 name] (M2) · [P3 name if exists] (M1)
Priority persona: [P1 name] — [one sentence: why this persona scores highest]

To build the HTML report, Notion page, and PERSONA-STRATEGY.md, trigger Run 2:
"Run 2 — [Brand Name]"
```

Do not proceed further. Do not start Step 6. Wait for the Run 2 trigger.

---

## Step 6 — Build the HTML Output

Read the saved JSON. Build the HTML from it. Do not re-derive persona insights.

See `references/html-template-notes.md` for exact CDN imports, tab structure, chart component specs, Foreplay card component, and Tailwind colour patterns.

**Required structure:**

1. **Strategy Overview tab** (first tab, full-width, no persona colour):
   - **Macro persona overview** (above charts): Card per macro showing name, shared motivation, shared messaging themes, which micros belong to it, and % of reviews. This gives the CS the high-level "who buys and why" before diving into micro detail.
   - Four Recharts charts:
   - Persona distribution (donut chart — uses `chart_data.persona_distribution`, colour-grouped by macro)
   - Funnel stage breakdown (bar chart — uses `chart_data.funnel_stages`)
   - Vailance zone split (bar chart — uses `chart_data.vailance_zones`)
   - Recommended content split (bar chart — uses `chart_data.content_split`)

2. **One tab per persona** (coloured to match persona theme, grouped under macro heading): 5 inner tabs:
   - Overview: macro badge (e.g. "M1: Self-Buyer"), who she is, pain points, desired outcome, failed solutions, purchase triggers
   - VOC Quotes: verbatim quotes grid + language patterns
   - Messaging: primary message, ad angles
   - Funnel & Bias: TE map visual, cognitive bias, vailance zone, self-concept anchor
   - Creative: hook bank (FEAR/DESIRE/BIAS labelled) + creative formats + brief skeleton + **Foreplay reference cards** (if `foreplay_refs` is populated)

3. **Cross-persona insights section** (below all tabs)

4. **Footer**: "Created by Launch With Us · launchwithus.io"

**Do not** include a Platform Priority section.

File naming: `[Brand Name] Audience Research.html` (space, not underscore). Save to outputs folder.

---

## Step 7 — Notion page (deferred — do not run during persona build)

Notion sync is handled separately after the persona build completes. Do not create a Notion page
during this skill. The CS will run the notion-sync skill when ready.

HTML + JSON + PERSONA-STRATEGY.md are the primary deliverables.

---

## Step 7.5 — Generate PERSONA-STRATEGY.md (handover to audience + competitor research)

Save to: `[client-folder]/PERSONA-STRATEGY.md`

```markdown
# [CLIENT NAME] — Persona Strategy Handover
Generated: [YYYY-MM-DD] | Source: [Brand Name] Audience Research.html + persona-data.json

---

## Macro Personas

| Macro | Name | Micros | Shared Motivation | Shared Messaging | % of Reviews |
|---|---|---|---|---|---|
| M1 | [Name] | [P1.1, P1.3, P1.4] | [one sentence] | [2-3 themes] | [X%] |
| M2 | [Name] | [P1.2] | [one sentence] | [2-3 themes] | [X%] |

---

## Micro Personas — Priority Ranked

| Rank | Macro | Persona | Score | ROAS Signal | Spend % | Creative Gap | Primary pain | Primary failed solution |
|---|---|---|---|---|---|---|---|---|
| 1 | M1 | [Name + code] | [score] | [Xa ROAS or "no data"] | [X% of spend] | [e.g. "ZERO dedicated creative"] | "[verbatim]" | "[verbatim]" |
| 2 | M1 | [Name + code] | [score] | [Xa ROAS] | [X%] | [gap] | "[verbatim]" | "[verbatim]" |
| 3 | M2 | [Name + code] | [score] | [Xa ROAS] | [X%] | [gap] | "[verbatim]" | "[verbatim]" |

> **Score source:** If ACCOUNT-AUDIT.md was available, scores include performance weighting (ROAS, spend allocation, creative gaps). If not, scores are review + brand research only — flag which mode was used.

---

## Per Persona — Audience Research Briefing

### [P1.X Archetype Name] (Macro: [M1 Name])
**Who to search for:** [specific description — age, situation, platform behaviour]
**Exact phrases to search on Reddit/TikTok:** [list from VOC + language patterns]
**Questions to validate:** [list from "What to validate in audience research"]
**Before state:** [one sentence — exact situation before purchase]
**After state:** [one sentence — exact transformation described in reviews]

[repeat per persona]

---

## Failed Solutions — Validated (priority for creative)
| Solution they tried | Why it failed | Verbatim |
|---|---|---|
| [product/approach] | [reason] | "[quote]" |

---

## Shared language across all personas (use in hooks)
- "[phrase 1]"
- "[phrase 2]"
- "[phrase 3]"

---

## Instructions for downstream skills

**→ audience-research:** Search for each persona using the exact phrases listed above. Validate the "before state" language — does Reddit confirm this is how they describe their situation? Look specifically for failed solutions evidence — what brands or approaches do they mention trying?

**→ competitor-research:** Each persona has a failed solution. Research which brands are mentioned in those failures. These are the competitors to analyse first.

**→ strategic-brief-builder:** Persona priority order is confirmed above. Hook bank and creative formats are in the JSON and HTML. Three Consistent Truths from BRAND-INTELLIGENCE.md still apply. Use macro-level messaging for broad campaigns that serve multiple micros simultaneously; use micro-level messaging for targeted creative.
```

Log the file path. This file is required before audience or competitor research runs.

---

## Step 8 — DECK GENERATION (separate trigger — do not run on standard analysis)

**Only run when the CS explicitly says:** "generate the deck", "make the presentation", "create the client deck", "I need the slides", or similar.

### 8.1 Find the data

Look for `[Brand Name]-persona-data.json` in the outputs folder. If not found, ask the user to confirm the brand name. Do not re-run the full analysis.

### 8.2 Read the pptx skill and analyse the template

```bash
# First read the pptx skill for the full editing workflow:
# /sessions/kind-eager-galileo/mnt/.skills/skills/pptx/SKILL.md

# Then analyse the LWU template:
python -m markitdown "[workspace]/assets/LWU-template.pptx"
python scripts/thumbnail.py "[workspace]/assets/LWU-template.pptx"
```

Then unpack:
```bash
python scripts/office/unpack.py "[workspace]/assets/LWU-template.pptx" unpacked/
```

### 8.3 Deck structure

Target: 10-14 slides. Map content to the appropriate LWU template layouts identified in the thumbnail review.

| Slide | Content | Notes |
|---|---|---|
| 1 | Cover: Brand name + "Audience Research & Persona Strategy" + date | Dark cover layout |
| 2 | At a glance: total reviews analysed, number of personas, dominant funnel stage, dominant vailance zone | 4-callout layout |
| 3 | Persona overview: all persona names, taglines, % distribution side by side | Multi-column or card grid |
| 4-N | One slide per persona: archetype name, tagline, who she is (short), top pain, top 3 hooks (one of each type), top 2 creative formats | 2-column or picture+text layout |
| N+1 | Cross-persona insights: shared language, whitespace opportunity, creative hypothesis | Full text or 2-column |
| N+2 | Testing priority: which persona/hook type to test first, and why | Numbered list or callout slide |
| Last | LWU close slide | Template close/cover layout |

For 2 personas: combine both on one slide (side-by-side), keep deck under 12 slides.
For 4 personas: use one slide per persona, keep other slides tight.

### 8.4 Edit, QA, and save

Follow the full editing and visual QA workflow from the pptx skill:
unpack → edit slides → clean → pack → convert to images → inspect visually → fix issues → re-verify.

Do not declare success without at least one full visual QA pass.

Save as: `[Brand Name] Audience Research - Deck.pptx` in the outputs folder.

---

## Quality Standards

- Every hook must use at least one exact phrase from the VOC
- No em dashes anywhere — use hyphens or commas
- Vailance zones and self-concept arcs must connect in the brief skeleton
- HTML must open correctly in a browser with no console errors
- Personas must feel like distinct real people, not hollow archetypes
- Every micro persona must be meaningfully distinct from other micros in the same macro (different vailance zone OR different self-concept anchor)
- Macro personas must have genuine shared messaging themes that work across all their micros — not just a label
- JSON must be valid and complete before any output is generated
- Notion must always be attempted, even if HTML fails
- Do not pad. If a persona has 5 strong hooks, write 5.
- Coverage check (Step 5.1) must be completed before declaring the run done

---

## Concept Sense-Check

When reviewing an existing script, brief, or ad against a persona, assess across these six dimensions. Flag every misalignment with a specific fix — not just an observation.

| Dimension | Question |
|---|---|
| Visual alignment | Does the person shown match this persona? Age, aesthetic, setting. |
| Hook-to-awareness match | Does the hook register match her TE stage? (Trigger = empathy first; Exploration = credibility; Evaluation = proof; Purchase = urgency) |
| Tone of voice | Would she recognise this language from her own community and how she actually talks? |
| Bias activation | Does the CTA or scripting tap her primary cognitive bias? |
| Objection handling | Are her key scepticisms addressed somewhere in the ad? |
| Framework fit | Is this a format she would genuinely stop and watch organically - not just a format the brand is comfortable making? |

---

## Account Plateau Diagnosis

When performance has stalled, map symptoms to their psychological root cause before recommending new creative volume.

| Symptom | Likely cause | Fix |
|---|---|---|
| All budget concentrating on one ad | Creative library is psychologically redundant - Meta favouring one and ignoring the rest | Audit vailance zone and self-concept clustering; produce concepts in untested zones |
| Rising CPMs without reach growth | Creative similarity is high | Introduce genuinely different vailance zones and self-concept anchors - not hook rewrites |
| Good thumb-stop and CTR but low conversion | Wrong intensity or self-concept for the funnel stage | Test Low Intensity for cold traffic; Medium-High for warm retargeting |
| Strong Zone 3-4 performance but overall CPAs rising | Fear-fatigue - the same emotional note is being played too often | Introduce Zone 1-2 aspiration-led concepts; test Ideal Self anchor |
| New customer acquisition slowing | Incremental reach has stalled on existing emotional territory | Brief concepts in untested vailance zones and self-concept anchors to unlock new psychological segments |

---

## Reference files

- `references/framework.md` — Full definitions of TE mapping, vailance zones, cognitive bias types, self-concept anchors
- `references/html-template-notes.md` — CDN imports, React/Babel/Recharts setup, tab structure, chart specs, Foreplay card component, Tailwind patterns
