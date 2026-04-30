---
name: d2c-research
description: >
  Brand and product research skill for D2C brands. Produces Stage 1 (Brand Research),
  Stage 2 (Product Research), Stage 3 (Review Mining from CSV + TrustPilot + on-site reviews),
  and Stage 4 (Reddit Research — mines Reddit for real audience language, pain points, failed
  solutions, and unprompted conversations). Reddit research runs BEFORE personas so persona
  creation is grounded in real platform language from day one. Does not build personas, run
  competitor analysis, or pull ad data (those are separate skills). Trigger on: "run brand
  research", "research this brand", "build the brand profile", "Stage 1 research", "brand and
  product research", "reddit research", or whenever BRAND-INTELLIGENCE.md needs to be built
  for a new client.
---

# D2C Brand + Product Research

> `[client-folder]` = the current working directory. All file reads and saves use this path.

This skill produces the brand intelligence foundation that all scripting, copywriting, and strategy
work reads from. It is the first thing built for any new client and the document that stops generic
output at the source.

**What this skill produces:**
- Stage 1: Brand Research (positioning, TOV, mechanisms, USPs, proof points, summary statement)
- Stage 2: Product Research (product-level detail, mechanism, features, differentiators)
- Stage 3: Review Mining (ranked pain points, failed solutions, VOC glossary, persona signals)
- Stage 4: Reddit Research (real audience language from Reddit — pain points, failed solutions, dream states, competitor sentiment, exact phrases for hooks)
- USP→Buyer Fear Map (every USP tested against real review evidence)
- Language to Avoid (mandatory — copied into MUST-READ-SCRIPTING.md before any script is written)

**Why Reddit is here, not later:**
Reddit research runs inside this skill — BEFORE persona creation — so that BRAND-INTELLIGENCE.md
arrives with real platform language baked in. This means `/d2c-persona-strategist` builds personas
from review data AND Reddit data together, not just reviews alone. The `/audience-research` skill
still exists as a post-persona validation layer (searches Reddit/TikTok with persona context for
deeper, targeted validation).

**What this skill does NOT produce:**
- Audience personas → use `d2c-persona-strategist`
- Competitor analysis → use `competitor-research` skill
- Ad performance analysis → use weekly creative analysis skill

---

## Critical research rule

**Brand-provided materials are ONE input, not the source of truth.**

Brands describe themselves aspirationally. Buyers describe reality. Where they conflict, buyer
language wins. Every USP must be tested against review evidence before it goes into creative.

Sources hierarchy (always in this order):
1. Customer reviews (on-site, TrustPilot, Google) — buyer reality
2. Reddit / organic forums — unprompted buyer voice
3. Third-party coverage (press, comparison sites) — independent signal
4. Brand website / deck — brand aspiration (useful for positioning context, not for truth)

---

## Step 0 — Read inputs from trigger prompt

**First: read the Onboarding Form MD if provided.** Treat every claim as a hypothesis to validate — not confirmed fact. Extract: brand name, URL, best-sellers, competitors named by client, customer pain points (brand's view), USPs (brand's view), audience demographics, language they say to avoid.

The CS provides in their prompt:
- **Onboarding Form MD** (primary input — read first if attached)
- Brand name
- Website URL
- Best seller URL(s)
- Customer reviews CSV (attached directly — mandatory for Stage 3)
- Competitor brands (pull from Onboarding Form if not specified separately)
- Client folder path

If Onboarding Form is missing: proceed with remaining inputs. Note the gap explicitly in the output.

---

## Step 1 — Scrape all sources (Sonnet subagent)

**Do NOT run web scraping in the main conversation.** Launch a single Sonnet subagent using the
Agent tool (`model: "sonnet"`) to handle all WebFetch and WebSearch calls. This keeps raw web
content out of the Opus context and uses Sonnet's separate rate limits.

**Subagent prompt — include all of the following:**

> You are researching a D2C brand for a creative strategy team. Scrape the following sources
> and return ONLY structured extracted data — no raw HTML, no full page dumps.
>
> **Brand: [brand name]**
> **Website: [URL]**
>
> **Scrape these pages (use WebFetch):**
> - Homepage — extract: hero copy, positioning statement, primary CTA
> - /about or /our-story — extract: founder story, mission, origin, reason-to-believe claims
> - /collections or /shop — extract: full product range, pricing, featured collections
> - /blog or /press — extract: any third-party coverage linked from the site
> - Top 3 bestseller product pages — extract: product descriptions, features, embedded reviews (verbatim)
>
> **Scrape review sources:**
> - TrustPilot: `https://www.trustpilot.com/review/[brand-domain]` — extract: star rating, review count, 15+ verbatim reviews
> - On-site product reviews (from bestseller pages above) — extract: all verbatim reviews found
>
> **Run these web searches (use WebSearch):**
> - `"[brand name] review"`
> - `"[brand name] vs [competitor]"` (for each competitor if known)
>
> **Reddit searches (use WebSearch — run ALL in parallel):**
> - `site:reddit.com "[brand name]"` — find any existing brand mentions
> - `site:reddit.com "[brand name] review"` — buyer opinions
> - `site:reddit.com "[product category] recommendation"` — what people recommend and why
> - `site:reddit.com "[product category] worth it"` — purchase hesitation and validation
> - `site:reddit.com "[product category] disappointed"` — pain points with category
> - `site:reddit.com "[product category] switched from"` — failed solutions and migration stories
> - `site:reddit.com "[competitor 1]"` — competitor sentiment (repeat for each competitor)
> - `site:reddit.com "[competitor 1] vs"` — comparison threads
> - `site:reddit.com "[top pain point from on-site reviews]"` — validate review pain points on Reddit
> - `site:reddit.com "[second pain point from on-site reviews]"` — validate second pain point
>
> For each Reddit result found, open the thread URL with WebFetch to get full comments.
> Prioritise threads with 10+ comments. Collect up to 20 threads maximum.
>
> **Reddit format per thread:**
> - Thread title
> - Subreddit
> - Upvotes + comment count
> - Top 5 verbatim quotes from comments (preserve exact phrasing)
> - Thread type: recommendation request / rant / comparison / success story / question
> - Sentiment: positive / negative / mixed
>
> **Return format — use this exact structure:**
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
> ## Reddit Research
> ### Brand mentions
> [threads mentioning brand directly — sentiment, key quotes]
>
> ### Category conversations
> [threads about product category — what people recommend, complain about, ask for]
>
> ### Pain point validation
> [threads confirming or contradicting review pain points]
>
> ### Failed solutions
> [what people tried before, why it didn't work — verbatim]
>
> ### Competitor sentiment
> [per competitor — what Reddit thinks of them, strengths/weaknesses mentioned]
>
> ### Subreddits with most results
> [ranked list of subreddits where this audience lives]
>
> ## Sources blocked or empty
> [list any that failed — including any Reddit searches that returned nothing]
> ```

When the subagent returns, proceed to the Specificity Gate using the structured data it provided.
Do not re-scrape anything. If the subagent reports a source as blocked, note it and continue.

**If the CS attached a reviews CSV:** Read the CSV directly in the main conversation (not in the
subagent) — CSV processing does not require web calls.

---

## ⛔ SPECIFICITY GATE — Run this check before writing Stage 3 or BRAND-INTELLIGENCE.md

Count real verbatim quotes collected across all review sources:

**If you have fewer than 10 real verbatim quotes from real sources:**
→ STOP. Do not run Stage 3. Do not generate BRAND-INTELLIGENCE.md.
→ Output this message:

```
RESEARCH INCOMPLETE — INSUFFICIENT REAL DATA

Brand: [Brand Name]
Sources successfully accessed: [list what was found]
Sources blocked or empty: [list what failed]
Real verbatim quotes found: [count]
Minimum required: 10

This run cannot produce Stage 3, VOC Glossary, or BRAND-INTELLIGENCE.md.
Stage 1 (brand positioning) and Stage 2 (product research) are available from website data.

To complete the research, the CS must provide one of:
- Customer reviews CSV (attached directly to the prompt)
- Working TrustPilot URL for this brand
- A Reddit thread or review source with real buyer quotes

Do not proceed. Do not infer, estimate, or extrapolate from category norms.
```

**If you have 10+ real verbatim quotes:** proceed to Stage 3.

---

## ❌ FABRICATION IS PROHIBITED — Applies to every section of this skill

The following are **never** acceptable in any output:
- "Expected pattern based on category norms"
- "Extrapolated from comparable brands"
- "Inferred from typical buyer behaviour"
- "Requires verification" as a placeholder for a fabricated quote
- Any quote not sourced from a real, accessible review, Reddit post, or website

**If data is not found:** write `NOT FOUND` in that field. Never fill gaps with invented content.
A document full of `NOT FOUND` is useful. A document full of fabricated patterns is dangerous.

⚠️ symbols do not make fabricated data safe to use. They just make it look like due diligence.

---

## Step 2 — Stage 1: Brand Research

### Brand Overview
- Mission statement (exact quote if available, paraphrase if not)
- Vision / long-term positioning ambition
- Core product categories and what the brand is known for
- Founding year and key milestones (if available)
- Customer resonance — what moment or story made buyers loyal

### Tone of Voice
- 4–6 TOV descriptors (e.g. "direct, warm, knowledgeable, unpretentious")
- Trust-building approach (what language builds credibility — certifications? founder story?
  clinical proof? community?)
- Language style with examples: sentence length, formality level, vocabulary
- Sounds like: [short example of the right tone]
- Does NOT sound like: [short example of the wrong tone]

### Brand Positioning
- Market position: premium / mass-market / specialist / challenger
- Core UVP (1–2 sentences — what they claim to do better than anyone)
- Primary messages — the 3–5 claims they repeat most across channels
- Awareness stage primarily addressed in their marketing (cold / warm / both)

### Brand Formality — Channel-Level Calibration

| Channel | Tone | Formality | Notes |
|---|---|---|---|
| Meta ads (cold TOF) | | | |
| Meta ads (retargeting) | | | |
| Email | | | |
| Organic social | | | |
| Product pages | | | |

Fill from scraped channel data. Note any channel that's inactive or missing.

### Brand Story
- Founding purpose — the problem the founder saw that nobody else was solving
- The insight that created the brand
- Key milestones that built reputation with customers
- Why buyers feel connected to the story (if they do — grounded in review language)

### USPs — Tested Against Buyer Evidence

List 4–8 USPs in order of creative strength (most differentiated first):

| USP | What it claims | Buyer evidence from reviews | Verdict |
|---|---|---|---|
| [USP] | [exact brand claim] | [quote or pattern — verbatim from reviews] | Proven / Partial / Unproven |

**Verdict rules:**
- **Proven** — multiple reviews reference this unprompted
- **Partial** — some review evidence, but not dominant
- **Unproven** — brand claims it but no buyer evidence found

Unproven USPs are deprioritised for scripting. Do not build ads around them without flagging the
risk. They may still be true — they just haven't earned creative confidence yet.

### Unique Mechanisms

For each USP — what is the specific process that makes it true? The mechanism is the HOW behind
the WHAT. Generic answers ("high quality") are not acceptable.

| USP | Mechanism (how it works specifically) | Why a buyer should believe it |
|---|---|---|
| [USP] | "Works by [specific process] which means [specific outcome]" | [proof point or logical reason] |

Mechanisms are the most important output of this entire skill. They are what the bridge prompt
will map to personas. Without a documented mechanism, a USP is just a tagline.

### Key Proof Points
- Star ratings and review counts (platform + exact numbers)
- Certifications or accreditations (exact names — not paraphrased)
- Awards or verified press mentions
- Clinical studies or independent testing (with source)
- Statistics the brand uses in marketing (note if source is verified or brand-claimed)

### Summary Statement

One paragraph — 4–6 sentences — that any CS can paste into any brief, email, or document to
orient someone on this brand instantly. Written in plain English. No jargon. No aspirational
fluff — only what review data confirms buyers experience.

---

## Step 3 — Stage 2: Product Research

For each of the top 3–5 products (or the products specified in the trigger prompt):

---

**[PRODUCT NAME]**

| Field | Detail |
|---|---|
| Category | |
| Price | |
| What it is | (description in buyer language, not brand language) |
| What it does | (functions, results, problems it solves) |
| Who it's for | (audience, needs, lifestyle signals from reviews) |
| How it works | (mechanism — write as: "works by [process] which means [outcome]") |
| Key features / ingredients | |
| Functional benefits | |
| Emotional benefits | (from review language — how buyers describe feeling) |
| Limitations / considerations | (what it doesn't do, who it's NOT for — from reviews) |
| What makes it different | (vs. competitors and generic alternatives — specific, not vague) |
| Proof and credibility | (ratings, certifications, studies for this specific product) |
| Price and value positioning | (how it justifies its price — premium/value/specialist) |
| Sensory / experiential story | (what using it actually feels like — verbatim from reviews) |

Repeat this table for each product. If more than 5 products, cover top 3 in full and list the
rest in a summary table only.

---

## Step 4 — Stage 3: Review Mining

Synthesise across ALL review sources (on-site reviews, TrustPilot, customer CSV if provided).
Do not list per-source. Pattern frequency matters more than any individual source.

> **Note:** This stage covers reviews from on-site, TrustPilot, and CSV sources. Reddit
> research is handled in Stage 4 below — it runs on the same data pass but is separated
> because Reddit produces different types of insight (unprompted conversations vs. prompted
> reviews). After personas are built, the `/audience-research` skill can optionally run a
> deeper, persona-targeted Reddit pass for validation.

### Pain Points — Ranked by Mention Frequency

| Rank | Pain Point | Signal | Sub-keywords | Verbatim example |
|---|---|---|---|---|
| 1 | | High | | "[exact quote]" |
| 2 | | | | |

Minimum 8 pain points. More if strong patterns exist. Signal = High (many mentions) / Medium /
Low (few but significant mentions).

### Failed Solutions — Ranked

What did buyers try before this brand, and why did it fail?

| Rank | Failed solution | Why it failed (buyer language) | Verbatim example |
|---|---|---|---|
| 1 | | | "[exact quote]" |

### Benefits — Ranked by Mention Frequency

| Rank | Benefit | Signal | Sub-keywords | Verbatim example |
|---|---|---|---|---|
| 1 | | High | | "[exact quote]" |

### Persona Signals

Patterns in reviews that suggest distinct buyer types. Not full personas — just signals for
the persona build that follows.

| Signal | Evidence from reviews | Implication for creative |
|---|---|---|
| [e.g. "55+ language patterns"] | [e.g. "references to retirement garden, grandchildren"] | [e.g. "older beginner segment — large and underserved in current creative"] |

### VOC Glossary — Verbatim Buyer Language

Exact phrases worth carrying into scripts, hooks, and headlines. Not paraphrased — raw buyer
words only. These feed directly into the script builder and persona strategist.

| Phrase | Context (when/where they say it) | Emotion behind it |
|---|---|---|
| "[exact phrase]" | | |

Minimum 15 phrases. Prioritise: phrases that name a specific fear, relief, transformation, or
social situation. These are the phrases that stop scroll because they make the viewer feel seen.

### Review Mining Summary

- **Primary pattern:** What buyers care about most (one sentence)
- **Biggest gap:** Where brand claims and buyer experience diverge
- **The single most important insight:** The one finding that should drive creative strategy

---

## Step 5 — Stage 4: Reddit Research

This stage uses the Reddit data collected by the subagent in Step 1. Do not re-search — synthesise
what was already returned.

**Why this exists as a separate stage:** Reviews (Stage 3) are prompted responses — someone bought
the product and was asked to rate it. Reddit is unprompted — people talking about their problems,
comparing options, venting frustrations, and asking for help without any brand prompting them. This
produces fundamentally different (and often more honest) language.

### Reddit Brand Mentions

| Thread | Subreddit | Sentiment | Key Quote | Context |
|---|---|---|---|---|
| [title] | r/[sub] | positive/negative/mixed | "[verbatim]" | recommendation / complaint / comparison |

If no brand mentions found: write `NO BRAND MENTIONS FOUND ON REDDIT` — this is useful data
(means the brand has low organic awareness).

### Reddit Pain Points — Category Level

Pain points people discuss about the CATEGORY (not the brand specifically). These are often
different from review pain points because they include people who haven't bought yet.

| Rank | Pain Point | Subreddit(s) | Verbatim Quote | Frequency |
|---|---|---|---|---|
| 1 | | | "[exact quote]" | High/Med/Low |

### Reddit Failed Solutions

What people tried before and why it didn't work. This is the highest-value Reddit output for
creative — "I tried X and it didn't work because Y" is a ready-made hook structure.

| What They Tried | Why It Failed (their words) | Verbatim Quote | Subreddit |
|---|---|---|---|
| | | "[exact quote]" | r/[sub] |

### Reddit Competitor Sentiment

| Competitor | Positive Mentions | Negative Mentions | Key Weakness (their words) |
|---|---|---|---|
| [name] | [count/summary] | [count/summary] | "[verbatim]" |

### Reddit Dream State

What does the audience WANT but can't find? These are unprompted desires — gold for ad creative.

| Desire | Verbatim Quote | Subreddit | Frequency |
|---|---|---|---|
| | "[exact quote]" | r/[sub] | High/Med/Low |

### Subreddit Map

Where does this audience actually live on Reddit? Ranked by relevance.

| Subreddit | Subscriber Count (if visible) | Relevance | What They Discuss |
|---|---|---|---|
| r/[sub] | | High/Med/Low | [one-line summary] |

### Reddit vs Review Comparison

| Topic | What reviews say | What Reddit says | Gap |
|---|---|---|---|
| [pain point] | "[review quote]" | "[Reddit quote]" | [same / different / Reddit-only / Review-only] |

This comparison is critical — where Reddit and reviews AGREE, you have high-confidence creative
angles. Where they DISAGREE, you have research questions for persona validation.

### Reddit Research Summary

- **Strongest Reddit-only insight:** [finding not in reviews — most valuable for creative]
- **Reddit confirms from reviews:** [top 3 pain points/benefits confirmed on both sources]
- **Reddit contradicts from reviews:** [any conflicts — flag for investigation]
- **Audience awareness level on Reddit:** [unaware / problem-aware / solution-aware / product-aware]

---

## Step 6 — USP→Buyer Fear Map

This is the document that connects brand knowledge to creative strategy.

For each USP, identify the specific buyer fear or hesitation it resolves — and how to say it
in an ad. Now includes Reddit evidence alongside review evidence:

| USP | Buyer fear it resolves | How to say it in an ad | Review evidence | Reddit evidence |
|---|---|---|---|---|
| [USP] | "[specific fear in buyer language]" | "[one line — how this USP becomes a hook]" | "[verbatim quote]" | "[Reddit quote or NOT FOUND]" |

**Rule:** If no buyer fear can be identified from review OR Reddit data, the USP cannot be used
as a creative angle yet. Mark it: ⚠️ No creative application found — needs more buyer evidence.
USPs confirmed by BOTH reviews and Reddit get highest creative confidence.

This table is what the bridge prompt reads to build STRATEGIC-BRIEF.md.

---

## Step 7 — Language to Avoid

**This section is mandatory. It is copied directly into MUST-READ-SCRIPTING.md before any
script is written for this client.**

### Generic brand phrases (in their own copy but too weak to differentiate):
- [list — exact phrases from scraped brand copy that are interchangeable with any competitor]

### Category tropes (used by every competitor — invisible to buyers):
- [list — phrases and angles that are saturated across the category]

### Language buyers find unconvincing (from review analysis):
- [list — based on complaints, dismissive language, or negative sentiment patterns]

### The "do not write like" rule:
One sentence capturing the most important negative constraint for this brand.
Example: "Do not write like a lifestyle magazine — this audience wants confidence and
practicality, not aesthetic aspiration."

---

## Step 8 — Save outputs

### Local .md file

Save to: `[client-folder]/research/brand-research-[YYYY-MM-DD].md`

```
# [CLIENT NAME] — Brand + Product Research
Date: [YYYY-MM-DD]
Generated by: d2c-research skill

---

## Stage 1: Brand Research
[full output]

## Stage 2: Product Research
[full output]

## Stage 3: Review Mining
[full output]

## Stage 4: Reddit Research
[full output]

## USP→Buyer Fear Map
[full table]

## Language to Avoid
[full section]

---
ACTION REQUIRED: Copy "Language to Avoid" into [client-folder]/MUST-READ-SCRIPTING.md
before any scripting session begins.

*Review this document before running the bridge prompt to create STRATEGIC-BRIEF.md.*
```

### Notion page (deferred — do not run during research)

Notion sync is handled separately after the research run completes. Do not create a Notion page
during this skill. The CS will run the notion-sync skill when ready.

**What goes where:**
- `research/brand-research-[date].md` → pushed to Notion as FULL report (all 4 stages, all tables, all verbatim quotes). This is the team's research reference.
- `BRAND-INTELLIGENCE.md` → stays LOCAL only. This is the compressed inter-skill handover that downstream skills (`d2c-persona-strategist`, `competitor-research`, `strategic-brief-builder`) read. It does NOT go to Notion.

---

## Step 9 — Generate BRAND-INTELLIGENCE.md (handover to next phase)

**Gate check before generating:**
- Stage 3 must have run successfully (10+ real verbatim quotes)
- At least 1 USP must have a Proven verdict
- If >50% of USPs are Unproven: generate the file but add a RED WARNING at the top — do not silently pass weak data downstream

If Stage 3 did not run: skip this step entirely. Output: "BRAND-INTELLIGENCE.md not generated — insufficient review data. Complete Stage 3 first."

Every downstream skill reads this file as Step 0. It must be compressed, specific, and grounded in confirmed data only — no brand aspiration.

Save to: `[client-folder]/BRAND-INTELLIGENCE.md`

```markdown
# [CLIENT NAME] — Brand Intelligence Handover
Generated: [YYYY-MM-DD] | Source: brand-research-[date].md

---

## Confirmed USPs — use in creative (Proven verdict only)
- [USP] — mechanism: [how it works] — evidence: "[verbatim quote]"

## Partial USPs — use with caution
- [USP] — what's unconfirmed: [gap]

## ❌ Do not use — Unproven
- [USP] — no buyer evidence found

---

## Top 5 Pain Points — Verbatim
1. "[exact quote]" — [mention count]
2. "[exact quote]" — [mention count]
3. "[exact quote]" — [mention count]
4. "[exact quote]" — [mention count]
5. "[exact quote]" — [mention count]

## Top 3 Failed Solutions — Verbatim
1. "[exact quote]" — tried: [what they used before]
2. "[exact quote]" — tried: [what they used before]
3. "[exact quote]" — tried: [what they used before]

---

## Persona Signals — Priority Ranked
| Persona | Score | Key VOC phrase |
|---|---|---|
| [Name] | [score] | "[phrase]" |

---

## Reddit Intelligence
- **Subreddit map:** [ranked list of subreddits where this audience lives]
- **Reddit-only pain points:** [pain points found on Reddit but NOT in reviews]
- **Reddit-only failed solutions:** [what they tried — verbatim]
- **Reddit dream states:** [what the audience wants but can't find — verbatim]
- **Competitor weaknesses (Reddit):** [per competitor — key weakness in audience's words]
- **Audience awareness level on Reddit:** [unaware / problem-aware / solution-aware / product-aware]

---

## Three Consistent Truths (cross-source — reviews + Reddit)
1. [Truth] — evidence: [cite review AND Reddit sources]
2. [Truth] — evidence: [cite review AND Reddit sources]
3. [Truth] — evidence: [cite review AND Reddit sources]

---

## Competitors (confirmed — from Onboarding Form)
[list — to be used by competitor-research skill]

---

## Language to Avoid
- [rule 1]
- [rule 2]
- [rule 3]
- Do not write like: [one sentence negative constraint]

---

## USP → Hook Territory (top 5)
| USP | Fear it resolves | Hook direction |
|---|---|---|
| [USP] | "[buyer fear — verbatim]" | "[hook starting territory]" |

---

## Instructions for downstream skills

**→ d2c-persona-strategist:** Priority persona order: [ranked list]. Ground personas in these VOC phrases: [top 5]. Deepen the failed solutions layer — this is the most underused creative territory.

**→ audience-research (optional — post-persona validation):** Reddit research already ran in Stage 4. Use `/audience-research` ONLY if you want deeper, persona-targeted validation after `/d2c-persona-strategist` has run. Key subreddits already identified: [list from Stage 4]. Search for [persona 1 signal] using these exact phrases: [top VOC phrases per persona].

**→ competitor-research:** Research these 3 competitors: [list — max 3]. Key question per competitor: do they own [confirmed USP 1]? Look for failure patterns around: [top 2 pain points].

**→ strategic-brief-builder:** USP→Fear Map ready. Three Consistent Truths above. Priority angles from review mining: [top 3].
```

Log the file path. If this file cannot be saved, the run is incomplete — do not declare success.

---

## Quality checklist — BLOCKING, not verification

This runs before declaring the run complete. Any unchecked item = run is incomplete. Do not
declare success with unchecked items. State which items failed and what the CS must provide to
complete them.

**Research:**
- [ ] Minimum 2 review sources successfully scraped (note any failures)
- [ ] Brand website fully read (homepage + about + product pages)

**Stage 1:**
- [ ] Every USP has a verdict (Proven / Partial / Unproven) with evidence cited
- [ ] Every mechanism written as "works by [process] which means [outcome]"
- [ ] Summary Statement written — plain English, no jargon, review-grounded
- [ ] Brand formality table completed for all active channels

**Stage 2:**
- [ ] Top 3+ products covered with full table (including mechanism field)
- [ ] Sensory / experiential story populated from real review language

**Stage 3:**
- [ ] Pain points RANKED by frequency (minimum 8)
- [ ] Failed solutions RANKED
- [ ] Benefits RANKED by frequency
- [ ] VOC Glossary has minimum 15 verbatim phrases
- [ ] Review Mining Summary — 3 fields completed

**Stage 4 (Reddit):**
- [ ] Reddit searches executed (minimum 5 search queries ran)
- [ ] Reddit pain points documented with verbatim quotes
- [ ] Reddit failed solutions documented
- [ ] Reddit vs Review comparison table completed
- [ ] Subreddit map populated
- [ ] Reddit Research Summary — 4 fields completed
- [ ] If no Reddit results found: documented as "NO REDDIT DATA" (not silently skipped)

**USP→Buyer Fear Map:**
- [ ] Every USP from Stage 1 appears in the map
- [ ] Any USP with no creative application is flagged ⚠️

**Language to Avoid:**
- [ ] Section exists and is non-empty
- [ ] "Do not write like" rule written (one sentence)

**Outputs:**
- [ ] Local .md file saved — path confirmed
- [ ] Notion page created — URL logged
