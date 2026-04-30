---
name: carbeth-script-builder
description: >
  Writes performance-driven Meta ad scripts and creative briefs for Carbeth Plants.
  Produces minimum 5 concepts per run, each with a strategy section (objective + hypothesis)
  and 3-4 production-ready variations (statics, edit-only videos, or UGC).
  Creates Notion tickets directly in the Creative Tickets DB + saves a local .md file.
  Trigger whenever Yoanna says anything like: "write scripts", "build concepts", "create briefs",
  "script ideas for Carbeth", "what should we make this week", or "run the script builder".
  Always reads the latest weekly analysis before writing anything.
---

# Carbeth Plants — Script Builder

## Standard trigger prompt (use this exact format for best output)

```
Run Carbeth script builder.
Focus: [optional — specific product, persona, or angle to prioritise this week]
Production constraint: [optional — e.g. "statics only", "no UGC this run"]
Extra context: [optional — anything not in the files, e.g. "last batch was too soft, go harder"]
```

Minimal trigger: **"Run Carbeth script builder."** — the skill reads everything else from files.
Only add context the skill cannot get from reading files.

---

## What this skill does

Generates a full week of Meta ad concepts for Carbeth Plants, grounded in the latest
creative intelligence data. Each concept has a clear strategic rationale and production-ready
variations written to the exact format used in the Creative Tickets DB.

---

## Step 0 — Read the feedback log FIRST (hard constraints)

Read `carbeth-plants/feedback/script-feedback-log.md` before anything else.

This file contains every rejected concept pattern and the reason it was rejected.
These are hard constraints — not suggestions. If a concept you are about to write matches
a pattern in this log, do not write it. State the conflict and choose a different direction.

The 8 core rejection patterns (always active, regardless of log contents):
1. Vague language — if it works for 10 other brands, delete it
2. Non-scroll-stopping hooks — must hit in 1 second, create tension or curiosity
3. Overly long / written hooks — speak, don't write; no clauses before the point
4. Generic beginner energy — not every ad is for beginners; speak up, not down
5. Lack of specificity — real plant, real situation, real outcome; nothing abstract
6. Too explanatory — ads are decisions, not tutorials; if a line doesn't move persuasion forward, cut it
7. Not platform-native — if you wouldn't stop for it in-feed, it fails
8. Weak static execution — statics are 3–6 words max; instant clarity or instant curiosity only

---

## Step 1 — Read all inputs in parallel

Read all of the following simultaneously before writing a single word:

**Local files:**
- Weekly analysis — PRIMARY brief: Use Glob on `carbeth-plants/research/` to list all `weekly-analysis-*.md` files. Read the one with the latest date. This tells you what to focus on: winning themes, top hooks, biggest gaps, next 5 tests.
- `carbeth-plants/MUST-READ-SCRIPTING.md` — NON-NEGOTIABLE. Every concept must pass this before it exists.
- `carbeth-plants/STRATEGIC-BRIEF.md` — THE BRIDGE. Contains the Persona→Tension→Mechanism→Hook→VOC mapping table. Use this table to ground every concept before writing it. Also contains current winners with WHY, available angles in priority order, and active hypotheses.
- Competitor research — Use Glob on `carbeth-plants/research/` to list all `competitor-research-*.md` files. Read the most recent one if it exists. If not, use the whitespace section from STRATEGIC-BRIEF.md.

**Notion — persona context:**
- Persona descriptions are in `carbeth-plants/STRATEGIC-BRIEF.md`. Only search Notion if you need supplementary audience data not covered there.

**Foreplay — scan saved creative inspiration:**
- Call `get_boards()` to list all available Foreplay boards.
- If any boards are relevant to the concepts you're writing (outdoor plants, gardening, UK D2C, the specific angle), call `get_board_ads()` on those. Scan for: format patterns, hook structures, visual approaches, execution ideas.
- If no relevant boards exist, skip this step — do not let a missing board block the run.
- Do NOT copy. Use for execution inspiration and quality benchmarking only.

---

## Step 2 — Determine what to write

From the weekly analysis, extract:
- The "Next 5 Tests" list → these are your starting concepts
- Q7 (biggest gap) → add as concept #6 if not already covered
- Q6 (top 3 to replicate) → reference these as benchmarks when writing hooks

Cross-reference with:
- Current season priority (from CLAUDE.md — March: outdoor shrubs, fruit/veg, herbs; April: climbers, annuals, veg)
- Persona distribution gap (if grow-your-own or gift buyer is underrepresented)
- Funnel stage gap (if MOF is empty, flag it and include at least 1 MOF concept)

Minimum 5 concepts. Maximum 7. Every concept must have a clear answer to: "why this, why now, what do we learn from it?"

---

## Step 2.5 — Specificity gate (complete this for every concept before writing it)

For each concept, state the following out loud before writing a single word of copy.
If you cannot complete a field from real data in the files, stop and state what is missing.
Do not proceed with a generic version.

```
CONCEPT [N] — PRE-WRITE DECLARATION
Persona: [which persona from STRATEGIC-BRIEF.md mapping table — A/B/C/D + one line description]
Their core tension: [exact phrase — pulled from the mapping table or VOC glossary]
Carbeth mechanism that resolves it: [specific — UK-grown/season-organised/19 years/variety]
Hook type: [identity rehabilitation / permission + guide / reward-led / lifestyle integration]
VOC phrase to use verbatim: [exact quote from audience research glossary or the mapping table]
Account insight this concept is based on: [specific ad name + ROAS, OR weekly analysis finding, OR Next 5 Tests item N]
Why this format (static/video/UGC): [1 sentence grounded in account data]
```

If the concept passes this gate, write it. If any field is "I don't know" or vague, you don't have enough grounding — go back to the data before writing.

---

## Step 3 — Choose execution type per concept

For each concept, assign one execution type based on production logic:

| Type | When to use |
|---|---|
| **2 statics + 1 edit-only video** | Mixed test — strongest when you want to compare static vs video on same concept |
| **3 statics** | Message-led concepts where visual simplicity wins; no footage needed |
| **3 edit-only videos** | Existing footage available; listicle, mashup, or VO-driven concepts |
| **1 UGC concept (3 hook variants)** | Net new creator footage needed; talking head, story-driven, first-person |

Prioritise edit-only and static executions over UGC where the concept allows it — lower production cost and faster to test. Motion design is lowest priority; only use for offer/pricing/product rotation concepts.

---

## Step 4 — Write each concept

Use this exact structure for every concept:

```
---
CONCEPT [N]: [NAME IN CAPS]
Execution type: [2 statics + 1 video / 3 statics / 3 edit-only videos / UGC x3 hooks]
Angle: [from Notion DB dropdown options]
Pain point: [specific, not generic]
Product: [specific category]
Funnel stage: [Problem Aware / Solution Aware / Product Aware]
Platform: Meta

STRATEGY
Objective: [Max 2 sentences. What does this concept need to achieve? What anxiety or desire does it address?]
Hypothesis: [Max 2 sentences. Why will this work? Cite account data, persona insight, or seasonal truth.]
Testing logic: [1 sentence. What specific question do these variations answer?]

────────────────────────────────────────────

VARIATION 1 — [Static / Video / UGC] — [brief descriptor]
[For statics:]
  Headline: [exact text]
  Subheading: [exact text]
  Visual notes: [what the designer needs to build — layout, products to show, links if known, reference style]
  Editor include: [non-negotiables]
  Editor avoid: [what not to do]

[For edit-only videos:]
  Hook — [TEXT ON SCREEN / VO]: [exact copy]
  Visual inspiration: [what footage to use, where to find it if known]
  Body — [TEXT ON SCREEN / VO]: [exact copy, structured as on-screen text beats]
  Visual direction: [what footage maps to each beat]
  Editor notes: [key message, pacing, music direction, format rules]

[For UGC — Variation 1, 2, 3 share same body, hooks differ:]
  Hook: [exact spoken line — punchy, one sentence, creates tension or curiosity]
  Visual inspiration for hook: [what the creator should do/show in opening frame]
  ---
  BODY FLOW (shared across all 3 hooks):
  Example script: [THIS IS AN EXAMPLE — CREATOR USES OWN WORDS]
  [Write full body as spoken natural English. First person. No ad language.]
  Directional beats:
  • [beat 1 — what to say/show]
  • [beat 2]
  • [beat 3]
  • [CTA direction]

  Creator requirements:
  Age: / Location: UK / Gender: / Niche:

  Shoot list must include:
  • [required shot 1]
  • [required shot 2]
  • [Plant close-ups — healthy, glossy]
  • [Unboxing shots if delivery trust concept]
  • [Head-to-camera clips]

  Avoid:
  • Messy visuals, damaged packaging
  • Dead/unhealthy plants, dark or blurry shots

VARIATION 2 — [type] — [descriptor]
[same structure, different pain point angle or hook territory]

VARIATION 3 — [type] — [descriptor]
[same structure]

[VARIATION 4 if execution type warrants it]

PRE-APPROVAL CHECK
Run every check. If any fails, fix it before outputting. Do not present work that fails a check.

STRATEGY
[ ] Did this concept complete the Step 2.5 pre-write declaration? (persona, tension, mechanism, VOC, account insight all cited)
[ ] Is the hypothesis specific — does it name a real ad, ROAS, or weekly analysis finding? "Research suggests..." = fail.

HOOK
[ ] Would YOU stop scrolling for this? (If uncertain, rewrite)
[ ] Is there genuine tension, curiosity, or specificity in the first line?
[ ] Is it 3–8 words for static, or 1 punchy sentence for video/UGC? Can it be shorter?
[ ] Does it sound spoken, not written? Read it aloud — any awkward clause structure?

REPLACEABILITY TEST
[ ] Replace "Carbeth" with a competitor brand name. Does the hook still work? If yes → rewrite.
[ ] Could any of the body copy appear word-for-word in a Patch Plants ad? If yes → rewrite.

SPECIFICITY TEST
[ ] Does the concept reference a real plant, real situation, or real outcome — not abstract benefits?
[ ] Is at least one VOC phrase from the glossary used verbatim in the hook or body?

BODY
[ ] Does every sentence move persuasion forward? Cut anything that doesn't.
[ ] Is it easy to say out loud, fast? If it drags, tighten it.
[ ] No banned phrases: "beautiful plants", "better garden", "great quality", "add something new", "start your journey", "elevate", "transform your space", "bring nature home", "curated", "premium experience"
[ ] No double dashes (--). Single dash or comma only.

STATIC HEADLINES (if applicable)
[ ] Is the headline 3–6 words?
[ ] Is it instantly understood — instant clarity OR instant curiosity? No middle ground.
[ ] Is it an outcome or a tension — not a brand statement?

EMOTION
[ ] Is the emotional angle concrete and real — grounded in a specific outcome or feeling?
[ ] Is it earned through specificity, not written through adjectives?
[ ] No over-romanticising. The audience wants easier starting points, not a dream identity.
---
```

### Scripting rules (from MUST-READ-SCRIPTING.md — always apply)

- Open with tension, solution, or curiosity. No warm-up.
- Every concept must link to at least one proven account foundation: outdoor > indoor, reassurance > aspiration, beginner confidence, fear-removal, "what to plant now", multi-product/shortlist, reduce confusion.
- Sound like a person talking, not a copywriter writing. Short to medium sentences. Believable spoken English.
- Do not write: "elevate your outdoor living", "transform your space", "bring nature home", "curated", "premium experience"
- Do not over-romanticise. The audience wants easier starting points, not a dream identity.
- For fruit/veg: reward + taste + pride, NOT tutorial content.
- For roses: fear-removal is central — address the anxiety directly.
- For herbs: cost/value and convenience, not transformation.
- Hooks must vary in type: tension / realisation / reward / curiosity / identity / seasonal timing / solution-first. Never reuse the same hook logic across concepts.
- No double dashes (--). Use single dash or comma.

### Hook variation rules (UGC and video)

3 hooks per UGC concept. Each must attack a different psychological entry point:
- Hook 1: tension / fear / problem ("If you keep killing plants...")
- Hook 2: realisation / identity / timing ("This is the time of year to...")
- Hook 3: reward / curiosity / solution-first ("I didn't expect growing my own to feel like this")

Same body flow for all 3. Body does not change.

---

## Step 5 — Save .md file

Save to: `carbeth-plants/scripts/scripts-[YYYY-MM-DD].md`

Structure:
```
# Carbeth Plants — Script Pack
**Date:** [date]
**Based on:** weekly-analysis-[date].md
**Concepts:** [N]

---
[all concepts in full, using Step 4 format]

---
*Generated by carbeth-script-builder. All concepts pending internal review.*
```

---

## Step 6 — Create Notion tickets

For each concept, create one parent ticket + child deliverable tickets in the Creative Tickets DB.

**Carbeth Plants client ID:** `https://www.notion.so/2c5f64437f9b816faa74d9aa5c133d1b`
**Creative Tickets DB collection:** `collection://27df6443-7f9b-81ed-b579-000b5f0058b3`

### Template IDs — duplicate these, never build from scratch

| Execution type | Parent template | Child template (1 deliverable) |
|---|---|---|
| 2 statics + 1 video | `32af64437f9b804c93e2d8b19ce33191` (LWUCPL030) | Static: `32af64437f9b80928450ef5c45990a84` |
| 3 statics | `2e9f64437f9b81d2bd19fece6dabc275` (LWUCPL016) | Static: `2e9f64437f9b804dbd78df1afd5302af` |
| 3 edit-only videos | `308f64437f9b81119827fdb964aaa8dc` (LWUCPL029) | Video: `308f64437f9b8037959eccd1fb65f53e` |
| UGC x3 hooks | `305f64437f9b81a6abb0e8e83cfc7f78` (LWUCPL022) | UGC: `305f64437f9b812f9dfbd67d8aead0ba` |

### Creation sequence per concept

Do each concept in sequence (not all in parallel — Notion rate limits):

1. **Duplicate parent template** using `notion-duplicate-page`
2. **Update parent page** using `notion-update-page`:
   - Ticket ID: `LWUCPL[next available number]`
   - Ticket Status: `Internal Concept Review`
   - Angle: [from concept]
   - Pain Point: [from concept]
   - Product: [from concept]
   - Funnel Stage: [from concept]
   - Ticket Type: `Design` (for statics/video) or `UGC`
   - Objective: [from strategy section]
   - Hypothesis: [from strategy section]
   - Client: `https://www.notion.so/2c5f64437f9b816faa74d9aa5c133d1b`
   - Update Strategy table body: Angle description, Objective, Hypothesis
3. **Duplicate child template** once per variation using `notion-duplicate-page`
4. **Update each child page** with variation-specific content:
   - Ticket ID: `LWUCPL[N]-[1/2/3]`
   - For statics: update Specification table (Headline, Subheading, Visual Notes)
   - For videos: update Hook table (Copy, Visual Inspiration) + Body table (Copy, Visual Direction)
   - For UGC: update Hook table + Body table + Creator Requirements + Shoot list
5. **Link child to parent**: update child's `Concept` property to point to new parent URL

### Next ticket number

Before creating, use `notion-search` in the Creative Tickets DB to find the highest existing LWUCPL number. Increment by 1 for each new concept.

### If Notion creation fails

Log the failure, continue with the .md file. The content is always the primary deliverable — Notion is the secondary output. Never abort the run because of a Notion error.

---

## Important context

- This skill runs after the weekly creative intelligence analysis. The analysis is the brief. Do not invent directions that contradict it.
- The account wins on: beginner confidence, fear-removal, outdoor > indoor, native/editorial format, problem-solution structure.
- It is currently spring (March-April). Priority: outdoor shrubs, fruit/veg, herbs, Mother's Day gifting.
- Motion design is low priority. Only use for product rotation, offers, or pricing.
- Production hierarchy: static → edit-only video → UGC. Test cheaper formats first.

## Tone calibration — voice register for Carbeth UGC and video

These are not templates. They are voice benchmarks — use them to calibrate register, not to copy structure.

**What these scripts do right:**
- One thought per sentence. Short. No clause before the point.
- First person, past tense for the journey ("I started growing..."), present for the insight ("the difference was bigger than I expected").
- Specific product named naturally — never "our plants" or "their products".
- No ad language. Sounds like someone telling a friend, not writing copy.
- The surprise/discovery moment is earned ("what I didn't expect was...") — not announced.
- Ends with a recommendation that sounds personal, not a CTA.
- Body never explains. It shares. The person is living through something real.

**Calibration examples (grow-your-own register — LWUCPL041):**
> "I didn't start growing my own food to make some big lifestyle change. I just kept buying fruit and veg from the supermarket and feeling disappointed by it."
> "What I didn't expect was how rewarding it felt. Knowing I'd grown them myself."

**Calibration examples (knowledge transfer / reassurance register — LWUCPL022):**
> "She told me the biggest thing is choosing plants that actually handle British weather."
> "Watching her do it every year, you realise it's not complicated. She just starts with the right plants."

**The test:** Read the body out loud. If it sounds like someone performing an ad, rewrite it. If it sounds like someone telling you something they genuinely discovered, it passes.
