---
name: d2c-deep-research
description: >
  Combined brand research + persona strategy skill for D2C brands. Merges d2c-research and
  d2c-persona-strategist into a single pass. Requires ACCOUNT-AUDIT.md (from /audit-interpret)
  before running. Produces: brand research (positioning, TOV, mechanisms, USPs, proof points),
  product research, review mining, full persona strategy with framework layers, hook banks,
  creative formats, and all handover documents in one run. The audit informs persona split
  weighting and creative recommendations. Trigger on: "run deep research", "full research",
  "brand + persona research", "d2c deep research", or whenever both BRAND-INTELLIGENCE.md
  and PERSONA-STRATEGY.md need to be built for a new client.
---

# D2C Deep Research (Brand + Persona Combined)

> `[client-folder]` = the current working directory. All file reads and saves use this path.

This skill combines brand research and persona strategy into a single pass. It processes the
reviews CSV once, builds brand intelligence and persona clusters simultaneously, and uses the
account audit to ground persona split and creative recommendations in real performance data.

**What this skill produces:**
- Stage 1: Brand Research (positioning, TOV, mechanisms, USPs, proof points, summary statement)
- Stage 2: Product Research (product-level detail, mechanism, features, differentiators)
- Stage 3: Review Mining + Persona Clustering (merged - one pass over the CSV)
- USP->Buyer Fear Map
- Language to Avoid
- Full persona strategy with framework layers (TE, bias, vailance, self-concept)
- Trigger events, hook banks, creative formats per persona
- Creative coverage check
- All handover documents: BRAND-INTELLIGENCE.md, PERSONA-STRATEGY.md, persona-data.json

**What this skill does NOT produce:**
- Reddit/TikTok audience research -> use `audience-research`
- Competitor analysis -> use `competitor-research`
- Ad performance audit -> use `audit-interpret` (must run BEFORE this skill)

**When to use this vs the individual skills:**
- Use this skill for new client onboarding (the standard path)
- Use `d2c-research` standalone when you only need brand intelligence without personas
- Use `d2c-persona-strategist` standalone when brand research already exists and you need to rebuild personas from new review data

---

## How to trigger this skill

The CS runs this with a prompt like:

```
/d2c-deep-research for [Brand Name].
Onboarding form: ./onboarding.md
Reviews CSV: [filename].csv
Audit: ACCOUNT-AUDIT.md is in the client folder.
```

**Required inputs (the skill will HARD STOP without these):**

1. **ACCOUNT-AUDIT.md** in the client folder - produced by `/audit-interpret`. Must exist before this skill runs. If the account is brand new with no ad history, the CS must create a minimal audit noting "new account - no performance data" so the skill knows to skip audit-informed weighting.

2. **Customer reviews CSV** - attached or in the client folder. Mandatory for Stage 3 + personas.

**Required inputs (from CS or onboarding form):**

3. **Onboarding Form MD** - the client's onboarding answers (brand name, URL, USPs, competitors, target customer, pain points, tone, markets, discount codes, CPA targets, socials, content links). The CS creates this per client.

4. **Brand name + Website URL** - can be in the onboarding form or in the prompt.

**Optional inputs:**

5. Best seller URLs (if not on homepage)
6. Foreplay board name(s) for creative references
7. Competitor brands (can also come from onboarding form)

---

## Critical research rule

**Brand-provided materials are ONE input, not the source of truth.**

Brands describe themselves aspirationally. Buyers describe reality. Where they conflict, buyer
language wins. Every USP must be tested against review evidence before it goes into creative.

Sources hierarchy (always in this order):
1. Customer reviews (on-site, TrustPilot, Google) - buyer reality
2. Reddit / organic forums - unprompted buyer voice
3. Third-party coverage (press, comparison sites) - independent signal
4. Brand website / deck - brand aspiration (useful for positioning context, not for truth)

---

## TOKEN EFFICIENCY ARCHITECTURE

This skill runs in **two invocations**, same as the standalone persona skill.

### Run 1 - Full analysis pass (default trigger)
Phases 0 through 7. Reads audit, scrapes brand, processes CSV (brand research + persona
clustering in one pass), applies framework, saves all outputs.
**HARD STOP after Phase 7.** Output handover message. Do not build HTML.

### Run 2 - Output pass (separate trigger)
Triggered by: "Run 2", "Run 2 - [brand name]", "build the outputs", "generate the HTML"
Reads saved JSON. Builds HTML report + PERSONA-STRATEGY.md.
Do not re-derive any insights.

---

## PHASE 0 - Read Account Audit (MANDATORY - run before everything else)

```
Read: [client-folder]/ACCOUNT-AUDIT.md
```

**If ACCOUNT-AUDIT.md does not exist: HARD STOP.** Do not proceed. Tell the CS:

> "ACCOUNT-AUDIT.md is missing. This file is produced by the /audit-interpret skill and
> contains performance data, persona coverage analysis, messaging territory gaps, and
> creative health scores that this skill needs to produce audit-informed personas.
> Please run `/audit-interpret [Notion URL]` first, then re-trigger this skill."

Do not offer to proceed without it. The audit grounds persona split and creative
recommendations in real account performance - without it, personas are review-derived
only, which is what the standalone skills already do.

**Extract and hold in context from the audit:**

- **Account Snapshot:** Monthly spend, ROAS/CPA, active ads, Creative Health Score, Creative Diversity Score
- **Cross-Phase Findings:** The patterns that emerged from reading all 10 audit phases together
- **Persona coverage from Phase 6:** Which personas currently have motivation-specific creative, which don't. Identity angles used vs missing.
- **Messaging territory gaps from Phase 5:** Beliefs and motivations never spoken to. Territory Coverage Checklist status.
- **Format analysis from Phase 8:** Which formats are overused, which are untapped. Format-to-job mapping.
- **Funnel distribution from Phase 10:** Where spend clusters (TOF/MOF/BOF). Funnel mismatches.
- **Validated strengths:** What's working and must be protected.
- **Risk signals:** What's fragile and needs addressing.
- **Strategic opportunities:** Ranked by expected impact - these inform persona priority.
- **Repeatable creative formula from Phase 9:** Winning video structure, hook patterns.

**How the audit informs the rest of this skill:**

1. **Persona split weighting:** If the audit shows persona X has zero motivation-specific creative, that persona gets elevated priority regardless of review volume. The audit reveals WHO the account is missing, not just who's buying.

2. **Creative format recommendations:** The audit's format-to-job map and untapped format opportunities feed directly into Step 5 (Creative Formats per persona). Don't recommend formats the account is already oversaturated with unless there's a new angle.

3. **Hook bank prioritisation:** The audit's winning hook patterns tell you what's already proven. New hooks should attack DIFFERENT emotional territories, not variations of what's already winning. Cross-reference with Creative Diversity Score.

4. **Territory gap filling:** The audit's missing messaging territories become mandatory coverage items in the persona hook banks. If the audit says "aspiration territory untested", at least one persona's hook bank must include aspiration hooks.

5. **Funnel stage alignment:** The audit's funnel distribution tells you where spend clusters. Persona TE mapping should explicitly address funnel gaps - if 80% of spend is BOF, persona creative recommendations should prioritise TOF formats.

---

## PHASE 0.5 - Read Onboarding Form + Inputs

**Read the Onboarding Form MD if provided.** Treat every claim as a hypothesis to validate -
not confirmed fact. Extract: brand name, URL, best-sellers, competitors named by client,
customer pain points (brand's view), USPs (brand's view), audience demographics, language
they say to avoid.

The CS provides in their prompt:
- **Onboarding Form MD** (primary input - read first if attached)
- Brand name
- Website URL
- Best seller URL(s)
- Customer reviews CSV (mandatory)
- Competitor brands (pull from Onboarding Form if not specified separately)
- Client folder path
- Optionally: Foreplay board name(s) for creative references

If Onboarding Form is missing: proceed with remaining inputs. Note the gap explicitly.

**Foreplay (ONLY if boards specified):**
```
get_boards() -> match the named board(s) exactly
get_board_ads(board_id, limit=10) -> max 10 ads per board
```
Extract ONLY: `thumbnail_url`, `brand`, `format`, `headline`. Hard limit: 10 ads per board.

---

## PHASE 1 - Scrape all sources (Sonnet subagent)

**Do NOT run web scraping in the main conversation.** Launch a single Sonnet subagent using the
Agent tool (`model: "sonnet"`) to handle all WebFetch and WebSearch calls.

**Subagent prompt - include all of the following:**

> You are researching a D2C brand for a creative strategy team. Scrape the following sources
> and return ONLY structured extracted data - no raw HTML, no full page dumps.
>
> **Brand: [brand name]**
> **Website: [URL]**
>
> **Scrape these pages (use WebFetch):**
> - Homepage - extract: hero copy, positioning statement, primary CTA
> - /about or /our-story - extract: founder story, mission, origin, reason-to-believe claims
> - /collections or /shop - extract: full product range, pricing, featured collections
> - /blog or /press - extract: any third-party coverage linked from the site
> - Top 3 bestseller product pages - extract: product descriptions, features, embedded reviews (verbatim)
>
> **Scrape review sources:**
> - TrustPilot: `https://www.trustpilot.com/review/[brand-domain]` - extract: star rating, review count, 15+ verbatim reviews
> - On-site product reviews (from bestseller pages above) - extract: all verbatim reviews found
>
> **Run these web searches (use WebSearch):**
> - `"[brand name] review"`
> - `"[brand name] vs [competitor]"` (for each competitor if known)
>
> **Return format - use this exact structure:**
>
> ```
> BRAND SCRAPE RESULTS
>
> ## Homepage
> Hero copy: ...
> Positioning: ...
> Primary CTA: ...
>
> ## About / Story
> Founder story: ...
> Mission: ...
> Claims: ...
>
> ## Product Range
> [list with prices]
>
> ## Product Pages (top 3)
> [per product: name, description, features, embedded reviews verbatim]
>
> ## TrustPilot
> Rating: X/5 (N reviews)
> Verbatim reviews:
> 1. "..."
> 2. "..."
> [all found]
>
> ## Web Search Results
> [key findings, verbatim quotes found]
>
> ## Sources blocked or empty
> [list any that failed]
> ```

When the subagent returns, proceed using the structured data it provided.
Do not re-scrape anything.

**The reviews CSV is read directly in the main conversation** (not in the subagent).

---

## SPECIFICITY GATE - Run before proceeding to Phase 3

Count real verbatim quotes collected across all review sources:

**If fewer than 10 real verbatim quotes from real sources:**
-> STOP. Do not run Phase 3. Output:

```
RESEARCH INCOMPLETE - INSUFFICIENT REAL DATA

Brand: [Brand Name]
Sources successfully accessed: [list]
Sources blocked or empty: [list]
Real verbatim quotes found: [count]
Minimum required: 10

Cannot produce review mining, personas, or handover documents.
Stage 1 (brand positioning) and Stage 2 (product research) are available from website data.

To complete: provide reviews CSV, working TrustPilot URL, or review source with real quotes.
```

**If 10+ real verbatim quotes:** proceed to Phase 3.

---

## FABRICATION IS PROHIBITED

The following are **never** acceptable in any output:
- "Expected pattern based on category norms"
- "Extrapolated from comparable brands"
- "Inferred from typical buyer behaviour"
- Any quote not sourced from a real, accessible review, Reddit post, or website

**If data is not found:** write `NOT FOUND`. Never fill gaps with invented content.

---

## PHASE 2 - Stage 1: Brand Research

### Brand Overview
- Mission statement (exact quote if available, paraphrase if not)
- Vision / long-term positioning ambition
- Core product categories and what the brand is known for
- Founding year and key milestones (if available)
- Customer resonance - what moment or story made buyers loyal

### Tone of Voice
- 4-6 TOV descriptors (e.g. "direct, warm, knowledgeable, unpretentious")
- Trust-building approach (what language builds credibility)
- Language style with examples: sentence length, formality level, vocabulary
- Sounds like: [short example of the right tone]
- Does NOT sound like: [short example of the wrong tone]

### Brand Positioning
- Market position: premium / mass-market / specialist / challenger
- Core UVP (1-2 sentences)
- Primary messages - the 3-5 claims they repeat most across channels
- Awareness stage primarily addressed (cold / warm / both)

### Brand Formality - Channel-Level Calibration

| Channel | Tone | Formality | Notes |
|---|---|---|---|
| Meta ads (cold TOF) | | | |
| Meta ads (retargeting) | | | |
| Email | | | |
| Organic social | | | |
| Product pages | | | |

### Brand Story
- Founding purpose
- The insight that created the brand
- Key milestones that built reputation
- Why buyers feel connected (grounded in review language)

### USPs - Tested Against Buyer Evidence

| USP | What it claims | Buyer evidence from reviews | Verdict |
|---|---|---|---|
| [USP] | [exact brand claim] | [verbatim from reviews] | Proven / Partial / Unproven |

**Verdict rules:**
- **Proven** - multiple reviews reference this unprompted
- **Partial** - some review evidence, but not dominant
- **Unproven** - brand claims it but no buyer evidence found

### Unique Mechanisms

| USP | Mechanism (how it works specifically) | Why a buyer should believe it |
|---|---|---|
| [USP] | "Works by [specific process] which means [specific outcome]" | [proof point] |

### Key Proof Points
- Star ratings and review counts (platform + exact numbers)
- Certifications or accreditations
- Awards or verified press mentions
- Statistics (note if verified or brand-claimed)

### Summary Statement

One paragraph, 4-6 sentences, plain English, review-grounded.

---

## PHASE 2.5 - Stage 2: Product Research

For each of the top 3-5 products:

| Field | Detail |
|---|---|
| Category | |
| Price | |
| What it is | (buyer language) |
| What it does | (functions, results, problems it solves) |
| Who it's for | (audience, needs, lifestyle signals from reviews) |
| How it works | (mechanism: "works by [process] which means [outcome]") |
| Key features / ingredients | |
| Functional benefits | |
| Emotional benefits | (from review language) |
| Limitations / considerations | (from reviews) |
| What makes it different | (specific, not vague) |
| Proof and credibility | |
| Price and value positioning | |
| Sensory / experiential story | (verbatim from reviews) |

---

## PHASE 3 - Review Mining + Persona Clustering (MERGED - single CSV pass)

This is the core merge point. Process the CSV ONCE and produce BOTH review mining outputs
AND persona clusters simultaneously.

**Read ALL reviews using Python** - do not sample. For large CSVs, process in chunks via Bash.

### 3A - Review Mining (produces the same outputs as d2c-research Stage 3)

Synthesise across ALL review sources (on-site, TrustPilot, CSV).

**Pain Points - Ranked by Mention Frequency**

| Rank | Pain Point | Signal | Sub-keywords | Verbatim example |
|---|---|---|---|---|
| 1 | | High | | "[exact quote]" |

Minimum 8 pain points.

**Failed Solutions - Ranked**

| Rank | Failed solution | Why it failed (buyer language) | Verbatim example |
|---|---|---|---|
| 1 | | | "[exact quote]" |

**Benefits - Ranked by Mention Frequency**

| Rank | Benefit | Signal | Sub-keywords | Verbatim example |
|---|---|---|---|---|
| 1 | | High | | "[exact quote]" |

**Review Mining Summary**
- **Primary pattern:** one sentence
- **Biggest gap:** where brand claims and buyer experience diverge
- **Single most important insight:** the one finding that should drive creative strategy

### 3B - Persona Clustering (produces persona definitions)

During the same CSV pass, identify dominant themes across:
- Emotional triggers (why they bought)
- Failed solutions (what they tried before)
- Desired outcomes (what they wanted to feel)
- Proof signals (what built trust)
- Language patterns (exact repeating phrases)

Group into **2-4 distinct persona clusters** by primary purchase reason. Aim for 20-40% per
cluster. Fold any cluster under 15% into the closest match.

**AUDIT-INFORMED PERSONA WEIGHTING:**
After initial clustering from reviews, cross-reference with ACCOUNT-AUDIT.md:
- If the audit's Phase 6 shows a persona with NO motivation-specific creative -> elevate that persona's priority score by +5, regardless of review volume
- If the audit's Phase 5 shows a messaging territory gap that maps to a specific persona -> note this as a "territory gap persona" and flag it for priority creative
- If the audit's funnel distribution is heavily skewed -> ensure at least one persona's creative recommendations address the underserved funnel stage

For each persona define:
- **code**: P1.1, P1.2, etc.
- **colour theme**: rose / purple / teal / amber / slate
- **archetype name**: e.g. "The Gift Solver"
- **tagline**: one-line emotional drive
- **who they are**: 2-3 vivid sentences
- **review_count** + **percentage**: approximate cluster size
- **priority score**: sum of (review cluster %) + (pain point mention count) + (audit persona gap bonus)
- **audit context**: what the audit says about this persona's current creative coverage

Extract for each persona:
- Top 3 pain points - verbatim from reviews. No paraphrasing.
- Desired outcome - in their own words
- **Failed solutions** (mandatory): minimum 2 per persona with verbatim language
- Purchase triggers
- Before -> After state: one sentence each, grounded in review evidence
- 5-8 verbatim VOC quotes
- Language patterns (5-8 phrases)
- What to validate in audience research: 2-3 questions for Reddit/TikTok

**Emotional depth layer (required for every persona):**

List 3-5 specific emotional frustrations. For each:
- The frustration in their words (verbatim where possible)
- The core human desire it connects to: confidence / belonging / freedom / self-worth / attractiveness / security / approval / competence / empowerment
- 1-2 story lines that agitate this emotion - written in the persona's voice

### 3C - VOC Glossary (unified - not duplicated)

Build ONE glossary that serves both brand research and persona outputs:

| Phrase | Context | Emotion | Persona allocation |
|---|---|---|---|
| "[exact phrase]" | | | P1.1 / P1.2 / shared |

Minimum 15 phrases. Prioritise phrases that name a specific fear, relief, transformation,
or social situation.

### 3D - Emotional Language Surface (lightweight)

5-7 emotionally loaded phrases the brand hasn't used yet, surfaced across ALL reviews.
These feed into the VOC Enrichment Glossary and hook writing.

### 3E - USP->Buyer Fear Map

| USP | Buyer fear it resolves | How to say it in an ad | Review evidence |
|---|---|---|---|
| [USP] | "[specific fear in buyer language]" | "[one line]" | "[verbatim quote]" |

If no buyer fear can be identified, mark: No creative application found.

### 3F - Language to Avoid

**This section is mandatory. Copied into MUST-READ-SCRIPTING.md.**

- Generic brand phrases (too weak to differentiate)
- Category tropes (invisible to buyers)
- Language buyers find unconvincing (from review analysis)
- The "do not write like" rule (one sentence)

---

## PHASE 4 - Apply the D2C Creative Strategy Framework

For each persona. Read `references/framework.md` for full definitions.

**TE Map**: Trigger / Exploration / Evaluation / Purchase.
Write awareness level + 1-sentence creative implication.
**Cross-reference with audit:** Note where this persona's TE stage aligns with or contradicts
the audit's funnel distribution. If the audit shows 80% BOF spend and this persona is Trigger
stage, flag the gap explicitly.

**Cognitive Bias**: Primary + secondary from: Loss Aversion / Authority Bias / Identity
Reinforcement / Social Proof / Switching Cost / Bandwagon.
Write 1-sentence creative implication.

**Vailance Zone**: Open zone + close zone. Write 1 sentence on zone movement.

**Self-Concept Anchor**: Actual Self / Ideal Self / Ought Self. Write narrative note.

**Language Intensity**: Low / Medium / High. Write 1 sentence on why this intensity matches.

---

## PHASE 4.5 - Trigger Events (Schwartz + Ogilvy)

For each persona: two layers, both required.

**Layer 1 - Psychological triggers (Schwartz-style):**
Minimum 3 per persona. For each:
- The trigger (internal shift, pain flare, breaking point)
- Why it creates urgency
- Emotional state that signals it
- Ad angle

**Layer 2 - Contextual triggers (Ogilvy-style):**
Minimum 3 per persona. For each:
- The event or context (specific and real)
- Why it creates receptivity
- Where they are when most receptive (platform, format, time)
- Ad angle

---

## PHASE 5 - Build the Hook Bank

For each persona: **8-10 hooks** mapped to emotional territories.

| Label | Type | Emotional territory |
|---|---|---|
| **FEAR** | Loss / risk / worst case | shame / regret / inadequacy / missing out |
| **DESIRE** | Dream state / aspiration | confidence / belonging / freedom / approval |
| **IDENTITY** | Who they want to be | self-worth / competence / empowerment |
| **TRIGGER** | The moment that flips the switch | from Phase 4.5 psychological triggers |
| **PROOF** | Cognitive shortcut | authority / social proof / before-after evidence |

Each hook: one sentence, 15-25 words, written as an opening line. No brand name.
Use exact phrases from the VOC. Tag the emotional territory.

**Audit-informed hook prioritisation:**
- Cross-reference hooks against the audit's winning hook patterns (Phase 9 repeatable formula)
- Ensure new hooks attack DIFFERENT emotional territories from what's already winning
- If the audit's Creative Diversity Score is low, explicitly prioritise hooks in underrepresented territories
- If the audit flags a missing messaging territory, at least 2 hooks per persona must address it

**Coverage check:** At least 4 different emotional territories across the bank.

---

## PHASE 5.5 - Creative Formats

For each persona: 3-4 ad formats. For each:
- Format name
- Brief description
- Why it works for this persona (link to bias, zone, or funnel stage)

**Audit-informed format recommendations:**
- Cross-reference with audit Phase 8 format analysis
- Do NOT recommend formats the account is already oversaturated with (from format-to-job map) unless there's a genuinely new angle
- Prioritise formats the audit identified as having untapped potential
- If the audit shows a format performing well for one persona, note whether it could extend to others

Write a **brief skeleton** for the strongest format per persona:
Hook -> Problem -> Failed solutions -> Solution -> CTA
With self-concept arc and vailance zone transition written in.

---

## PHASE 6 - Creative Coverage Check

Map each persona across three dimensions:

| Persona | Vailance Zone (open) | Self-Concept Anchor | Language Intensity |
|---|---|---|---|
| [P1.1] | Zone [X] | [Actual/Ideal/Ought] | [Low/Med/High] |

**Check for clustering:** If 70%+ share the same vailance zone or self-concept anchor,
the creative library will be psychologically redundant.

**Minimum coverage:** At least one persona in a positive zone (1-2) and one in negative (3-4).

**Audit cross-check:** Compare this coverage table against the audit's Creative Diversity Score.
If the audit already flags low diversity, the new persona creative MUST introduce coverage in
zones and anchors the current library lacks. Note specific gaps and how the new personas fill them.

---

## PHASE 7 - Save All Outputs

### 7A - Save brand research

Save to: `[client-folder]/research/brand-research-[YYYY-MM-DD].md`

```
# [CLIENT NAME] - Brand + Product Research
Date: [YYYY-MM-DD]
Generated by: d2c-deep-research skill

---

## Stage 1: Brand Research
[full output from Phase 2]

## Stage 2: Product Research
[full output from Phase 2.5]

## Stage 3: Review Mining
[full output from Phase 3A - pain points, failed solutions, benefits, summary]

## USP->Buyer Fear Map
[from Phase 3E]

## Language to Avoid
[from Phase 3F]

---
ACTION REQUIRED: Copy "Language to Avoid" into [client-folder]/MUST-READ-SCRIPTING.md
before any scripting session begins.
```

### 7B - Save BRAND-INTELLIGENCE.md

**Gate check:**
- Phase 3 must have run (10+ real verbatim quotes)
- At least 1 USP must have a Proven verdict
- If >50% USPs are Unproven: add RED WARNING at top

Save to: `[client-folder]/BRAND-INTELLIGENCE.md`

```markdown
# [CLIENT NAME] - Brand Intelligence Handover
Generated: [YYYY-MM-DD] | Source: brand-research-[date].md

---

## Account Audit Context
- Creative Health Score: [X]/25
- Creative Diversity Score: [X]%
- Primary audit risk: [one sentence from ACCOUNT-AUDIT.md]
- Biggest opportunity: [one sentence from ACCOUNT-AUDIT.md]

---

## Confirmed USPs - use in creative (Proven verdict only)
- [USP] - mechanism: [how it works] - evidence: "[verbatim quote]"

## Partial USPs - use with caution
- [USP] - what's unconfirmed: [gap]

## Do not use - Unproven
- [USP] - no buyer evidence found

---

## Top 5 Pain Points - Verbatim
1. "[exact quote]" - [mention count]
2-5. [same format]

## Top 3 Failed Solutions - Verbatim
1. "[exact quote]" - tried: [what they used before]
2-3. [same format]

---

## Three Consistent Truths (cross-source)
1. [Truth] - evidence: [cite sources]
2-3. [same format]

---

## Competitors (from Onboarding Form)
[list]

---

## Language to Avoid
[from Phase 3F]

---

## USP -> Hook Territory (top 5)
| USP | Fear it resolves | Hook direction |
|---|---|---|
| [USP] | "[buyer fear]" | "[hook territory]" |

---

## Instructions for downstream skills

**-> audience-research:** Search for [persona 1] using: [VOC phrases]. Search for [persona 2] using: [list]. Key subreddits: [infer from research].

**-> competitor-research:** Research these 3 competitors: [list]. Key question per competitor: do they own [confirmed USP 1]? Look for failure patterns around: [top 2 pain points].

**-> strategic-brief-builder:** USP->Fear Map ready. Three Consistent Truths above. Persona priority from audit: [ranked list with audit rationale]. Priority angles: [top 3].
```

### 7C - Save persona data as JSON

```python
import json

persona_data = {
    "brand": "[Brand Name]",
    "date": "[YYYY-MM-DD]",
    "audit_context": {
        "creative_health_score": "[X]/25",
        "creative_diversity_score": "[X]%",
        "primary_risk": "[from audit]",
        "biggest_opportunity": "[from audit]",
        "persona_gaps": "[from audit Phase 6]",
        "territory_gaps": "[from audit Phase 5]",
        "funnel_skew": "[from audit Phase 10]"
    },
    "foreplay_refs": [],
    "chart_data": {
        "persona_distribution": [
            {"name": "P1.1 Name", "value": 42, "color": "#f43f5e"}
        ],
        "funnel_stages": [
            {"stage": "Trigger", "count": 0},
            {"stage": "Exploration", "count": 2},
            {"stage": "Evaluation", "count": 1},
            {"stage": "Purchase", "count": 0}
        ],
        "vailance_zones": [
            {"zone": "Zone 2 - Curious", "count": 1},
            {"zone": "Zone 3 - Frustrated", "count": 2}
        ],
        "content_split": [
            {"format": "UGC Testimonial", "recommended": 3},
            {"format": "Before/After", "recommended": 2}
        ]
    },
    "personas": [
        {
            "code": "P1.1",
            "colour_theme": "rose",
            "archetype_name": "...",
            "tagline": "...",
            "who_they_are": "...",
            "review_count": 0,
            "percentage": 0,
            "priority_score": 0,
            "audit_context": "...",
            "pain_points": [],
            "desired_outcome": "...",
            "failed_solutions": [],
            "purchase_triggers": [],
            "before_after": {"before": "...", "after": "..."},
            "voc_quotes": [],
            "language_patterns": [],
            "validate_in_audience_research": [],
            "emotional_depth": [],
            "te_map": {},
            "cognitive_bias": {},
            "vailance_zone": {},
            "self_concept": {},
            "language_intensity": {},
            "trigger_events": {},
            "hooks": [],
            "creative_formats": [],
            "brief_skeleton": {}
        }
    ],
    "cross_persona": {
        "hook_testing_priority": "...",
        "shared_language": [],
        "whitespace": "...",
        "creative_hypothesis": "...",
        "coverage_check": {}
    },
    "emotional_language_surface": []
}

with open('[Brand Name]-persona-data.json', 'w') as f:
    json.dump(persona_data, f, indent=2)
```

Save to the outputs folder. Confirm the file was written.

---

**HARD STOP - Run 1 complete.**

Output exactly this message:

```
Run 1 complete - [Brand Name] deep research saved.

Brand research: research/brand-research-[date].md
Brand intelligence: BRAND-INTELLIGENCE.md
Persona JSON: outputs/[Brand Name]-persona-data.json

Personas: [P1 name] | [P2 name] | [P3 name if exists]
Priority persona: [P1 name] - [why, including audit rationale]

Audit integration:
- Creative Health: [X]/25 | Diversity: [X]%
- Persona gaps addressed: [which audit gaps the new personas fill]
- Territory gaps addressed: [which territory gaps the hooks cover]

To build HTML report and PERSONA-STRATEGY.md, trigger Run 2:
"Run 2 - [Brand Name]"
```

Do not proceed further. Wait for Run 2 trigger.

---

## Run 2 - Output Pass

**Triggered by:** "Run 2", "Run 2 - [brand name]", "build the outputs", "generate the HTML"

**Step R2.0 - Find and read JSON:**
Search the outputs folder for `[Brand Name]-persona-data.json`
If not found: stop and tell CS to complete Run 1 first.

**Then run Steps R2.1 -> R2.2 -> R2.3 in sequence.**

### R2.1 - Build the HTML Output

Read the saved JSON. Build HTML from it. Do not re-derive insights.

**Required structure:**

1. **Strategy Overview tab** (first tab, full-width): Four charts:
   - Persona distribution (donut)
   - Funnel stage breakdown (bar)
   - Vailance zone split (bar)
   - Recommended content split (bar)
   Plus: Audit context summary card (Creative Health, Diversity, primary risk, biggest opportunity)

2. **One tab per persona** (coloured to match theme): 5 inner tabs:
   - Overview: who they are, pain points, desired outcome, failed solutions, purchase triggers, audit context
   - VOC Quotes: verbatim quotes grid + language patterns
   - Messaging: primary message, ad angles
   - Funnel & Bias: TE map, cognitive bias, vailance zone, self-concept anchor
   - Creative: hook bank (FEAR/DESIRE/BIAS labelled) + creative formats + brief skeleton + Foreplay cards (if populated)

3. **Cross-persona insights section**

4. **Footer**: "Created by Launch With Us - launchwithus.io"

File naming: `[Brand Name] Audience Research.html`. Save to outputs folder.

### R2.2 - Generate PERSONA-STRATEGY.md

Save to: `[client-folder]/PERSONA-STRATEGY.md`

```markdown
# [CLIENT NAME] - Persona Strategy Handover
Generated: [YYYY-MM-DD] | Source: [Brand Name]-persona-data.json

---

## Audit Context
- Creative Health: [X]/25 | Diversity: [X]%
- Persona gaps from audit: [which personas lack motivation-specific creative]
- Territory gaps from audit: [which messaging territories are untested]
- Funnel skew: [where spend clusters]

---

## Personas - Priority Ranked

| Rank | Persona | Score | Primary pain | Primary failed solution | Audit gap filled |
|---|---|---|---|---|---|
| 1 | [Name + code] | [score] | "[verbatim]" | "[verbatim]" | [what audit gap this persona addresses] |

---

## Per Persona - Audience Research Briefing

### [P1.X Archetype Name]
**Who to search for:** [specific description]
**Exact phrases to search on Reddit/TikTok:** [list from VOC + language patterns]
**Questions to validate:** [from "What to validate in audience research"]
**Before state:** [one sentence]
**After state:** [one sentence]
**Audit note:** [what the audit says about this persona's current coverage]

[repeat per persona]

---

## Failed Solutions - Validated (priority for creative)
| Solution they tried | Why it failed | Verbatim |
|---|---|---|
| [product/approach] | [reason] | "[quote]" |

---

## Shared language across all personas (use in hooks)
- "[phrase 1]"
- "[phrase 2]"

---

## Instructions for downstream skills

**-> audience-research:** Search for each persona using exact phrases above. Validate "before state" language. Look for failed solutions evidence.

**-> competitor-research:** Each persona has a failed solution. Research which brands are mentioned. These are the competitors to analyse first.

**-> strategic-brief-builder:** Persona priority order confirmed above. Hook bank and creative formats in JSON. Three Consistent Truths from BRAND-INTELLIGENCE.md apply. Audit context: [one sentence on what the audit says the brief should prioritise].
```

### R2.3 - Confirm completion

Output:

```
Run 2 complete - [Brand Name] outputs generated.

HTML report: outputs/[Brand Name] Audience Research.html
Persona strategy: PERSONA-STRATEGY.md

All handover documents ready:
- BRAND-INTELLIGENCE.md (for audience-research + competitor-research)
- PERSONA-STRATEGY.md (for audience-research + strategic-brief-builder)
- persona-data.json (for HTML + deck generation)

Next in pipeline: audience-research or competitor-research
```

---

## Deck Generation (separate trigger)

Only run when CS explicitly says: "generate the deck", "make the presentation", etc.

### Find the data
Look for `[Brand Name]-persona-data.json` in outputs folder.

### Deck structure
Target: 10-14 slides.

| Slide | Content |
|---|---|
| 1 | Cover: Brand name + "Brand Research & Persona Strategy" + date |
| 2 | Account audit snapshot: Creative Health, Diversity, primary risk, opportunity |
| 3 | Brand summary: positioning, USPs (proven only), summary statement |
| 4 | Persona overview: all names, taglines, % distribution |
| 5-N | One slide per persona: archetype, tagline, who, top pain, top 3 hooks, top 2 formats, audit gap |
| N+1 | Cross-persona insights: shared language, whitespace, creative hypothesis |
| N+2 | Testing priority: which persona/hook to test first, and why (grounded in audit) |
| Last | LWU close slide |

---

## Quality Checklist - BLOCKING

**Research:**
- [ ] ACCOUNT-AUDIT.md read and referenced throughout
- [ ] Minimum 2 review sources successfully scraped
- [ ] Brand website fully read (homepage + about + product pages)

**Stage 1 (Brand):**
- [ ] Every USP has a verdict with evidence
- [ ] Every mechanism written as "works by [process] which means [outcome]"
- [ ] Summary Statement written
- [ ] Brand formality table completed

**Stage 2 (Product):**
- [ ] Top 3+ products covered with full table
- [ ] Sensory / experiential story from real review language

**Stage 3 (Review Mining + Personas):**
- [ ] Pain points RANKED (minimum 8)
- [ ] Failed solutions RANKED
- [ ] Benefits RANKED
- [ ] Unified VOC Glossary has minimum 15 phrases
- [ ] Review Mining Summary completed
- [ ] 2-4 personas defined with full depth layers
- [ ] Every persona has minimum 2 failed solutions with verbatim
- [ ] Emotional depth layer completed for every persona
- [ ] Audit-informed persona weighting applied and documented

**Framework (per persona):**
- [ ] TE Map with audit funnel cross-reference
- [ ] Cognitive bias (primary + secondary)
- [ ] Vailance zone (open + close + movement)
- [ ] Self-concept anchor with narrative note
- [ ] Language intensity with rationale
- [ ] Trigger events (3 psychological + 3 contextual minimum)
- [ ] Hook bank (8-10 hooks, 4+ emotional territories, audit-informed prioritisation)
- [ ] Creative formats (3-4, audit-informed)
- [ ] Brief skeleton for strongest format

**Coverage:**
- [ ] Creative coverage check completed
- [ ] Coverage cross-checked against audit Creative Diversity Score
- [ ] At least one positive zone and one negative zone persona

**USP->Buyer Fear Map:**
- [ ] Every USP appears in the map
- [ ] USPs with no creative application flagged

**Language to Avoid:**
- [ ] Section exists and is non-empty
- [ ] "Do not write like" rule written

**Outputs:**
- [ ] brand-research-[date].md saved
- [ ] BRAND-INTELLIGENCE.md saved (with audit context)
- [ ] persona-data.json saved and valid
- [ ] All file paths logged

---

## Concept Sense-Check

When reviewing an existing script, brief, or ad against a persona:

| Dimension | Question |
|---|---|
| Visual alignment | Does the person shown match this persona? |
| Hook-to-awareness match | Does the hook register match their TE stage? |
| Tone of voice | Would they recognise this language? |
| Bias activation | Does the CTA tap their primary cognitive bias? |
| Objection handling | Are their key scepticisms addressed? |
| Framework fit | Is this a format they'd stop and watch organically? |
| Audit alignment | Does this concept address an audit-identified gap? |

---

## Account Plateau Diagnosis

| Symptom | Likely cause | Fix |
|---|---|---|
| All budget on one ad | Creative library psychologically redundant | Audit vailance zone clustering; produce concepts in untested zones |
| Rising CPMs, no reach growth | Creative similarity high | Introduce different vailance zones and self-concept anchors |
| Good CTR, low conversion | Wrong intensity for funnel stage | Test Low for cold; Medium-High for warm |
| Strong Zone 3-4 but CPAs rising | Fear-fatigue | Introduce Zone 1-2 aspiration concepts |
| New customer acquisition slowing | Reached existing emotional territory ceiling | Brief concepts in untested zones and anchors |

---

## Reference files

- `references/framework.md` - Full definitions of TE mapping, vailance zones, cognitive bias types, self-concept anchors
