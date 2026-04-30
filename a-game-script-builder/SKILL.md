---
name: a-game-script-builder
description: >
  Writes submission-ready Meta ad scripts and creative briefs for A-Game sportswear.
  Produces 4 concepts per run, each with strategy rationale (objective + hypothesis),
  pre-write declaration, and production-ready variations (UGC / Static / Hyrox UGC / Native DTC).
  Saves a local .md file and creates Notion tickets in the Creative Tickets DB.
  Trigger whenever Yoanna says anything like: "write scripts for A-Game", "build concepts",
  "create briefs", "script ideas for A-Game", "run the A-Game script builder", or names a
  specific product and asks for copy/scripts.
  ALWAYS reads the feedback log first. ALWAYS confirms visual context before writing.
---

# A-Game — Script Builder

## Standard trigger prompt

```
Run A-Game script builder.
Product focus: [specific SKU from product-specs-march-2026.md — or leave blank for priority order]
Format: [UGC / Static / Hyrox UGC / Native DTC — or leave blank for mixed]
Visual context: [MANDATORY if known — who is in the creative, what are they doing, what setting]
Extra context: [anything not in files — e.g. "Joshua wants something softer this batch", "Hyrox London is next week"]
```

Minimal trigger: **"Run A-Game script builder."** — the skill reads everything else from files.
Only add context the skill cannot get from reading files.

---

## What this skill produces

Submission-ready Meta ad scripts for A-Game, grounded in confirmed product specs, approved
brand voice, and client feedback history. Each concept has a clear strategy rationale and
production-ready copy written for Joshua to review and forward to Andy/Amy.

Maximum 4 concepts per run. Client rule — do not deliver more.

---

## Step 0 — Read the feedback log FIRST (hard constraints)

Read `a-game/feedback/script-feedback-log.md` before anything else.

This file contains every rejected line, every rejected pattern, and verbatim client quotes.
These are hard stops — not guidelines. If a concept matches a rejection pattern, do not write it.

The 7 permanent rejection patterns (always active, always enforced):

1. **Vague sensation claims** — "moves with you", "locked in", "feels second skin", "zero restriction" without mechanism. Client: "What does that mean?" → Always name the construction first.
2. **Infomercial/salesy language** — "the last [X] you'll need", "you'll never look back", "sold out twice. back again." → Replace with specific utility.
3. **Redundant obvious claims** — "full arm freedom" on sleeveless hoodie, "sports bras for real training" → Only claim what's non-obvious and engineered.
4. **Overclaimed support (bras)** — "high-impact support" when PDP says light. Already rejected once. → Confirm support level before writing every women's bra script.
5. **Generic category copy (swap test fail)** — if Gymshark, Nike or ASRV could say it → rewrite.
6. **Copy/visual mismatch** — copy must describe what's actually visible. Indoor Hyrox creative + cold weather copy was flagged as execution failure.
7. **Low-quality visual execution** — wrong product shown, distorted AI images, mismatched outfit, same reviews across every video. Flag if visual context is unknown.

---

## Step 1 — Read all inputs in parallel

Read all of the following before writing a single word:

- `a-game/feedback/script-feedback-log.md` ← already read in Step 0
- `a-game/MUST-READ-SCRIPTING.md` — NON-NEGOTIABLE. Every concept passes this or it doesn't exist.
- `a-game/STRATEGIC-BRIEF.md` — PRIMARY BRIEF. Persona→Tension→Mechanism→Hook map. USP→Buyer Fear Map. Enriched VOC glossary. Creator profiles. Active hypotheses. Priority SKU queue.
- `a-game/product-specs-march-2026.md` — PDP TRUTH. Every claim must map to a ✓ in this file. If a feature is marked ✗ — it cannot be in the script.

---

## Step 2 — Determine what to write

If the trigger prompt specifies a product → use it.
If not → use the Priority SKU Queue from STRATEGIC-BRIEF.md Section 9 (priority order):
1. Men's 2-in-1 Training Shorts (Steel Grey) — strongest mechanism story
2. Men's Seamless Training T-Shirt (Black) — strongest technical SKU
3. Men's Performance Training T-Shirt (Steel Grey/Beige) — baseline hero
4. Women's Reflective Running Shorts (Black) — running-specific
5. Women's Light Support Sports Bra (Pale Blue) — ⚠️ LIGHT SUPPORT ONLY

Format distribution (if not specified): 2 UGC concepts + 1 Static + 1 Hyrox or Native DTC.

---

## Step 2.5 — Pre-Write Declaration Gate

**Complete this for EVERY concept before writing a single word of copy.**
If any field cannot be completed from real data in the files — STOP and state what is missing.
Do not write a generic version. Missing data means a missing gate field = a blocked concept.

```
CONCEPT [N] — PRE-WRITE DECLARATION
─────────────────────────────────────
Product: [EXACT SKU name from product-specs-march-2026.md]
Format: [UGC / Static / Hyrox UGC / Native DTC]

VISUAL CONTEXT (MANDATORY):
  Who is in the creative: [Creator name from STRATEGIC-BRIEF.md Section 9d, OR "unknown — flagged"]
  What they are doing: [specific activity — sled push / barbell squat / run / warm-up / etc.]
  Setting: [gym floor / outdoor track / Hyrox event / studio]
  Product visible: [confirm product is clearly visible in described visual]
  ⚠️ If any field above is "unknown" → STOP. Do not write this concept. Note: "Visual context
  unconfirmed for Concept [N] — needs briefing from Joshua before scripting."

Persona: [from STRATEGIC-BRIEF.md Section 2 — name the persona type + one-line description]
Core tension: [exact phrase from tension column or VOC glossary — not paraphrased]
Product mechanism resolving it: [specific ✓ feature from product-specs — e.g. "flatlock seam
  construction + 4-way stretch" — not "quality fabric"]
USP→Fear row used: [cite the USP row from STRATEGIC-BRIEF.md Section 9b]
Hook territory: [gear failure / anti-athleisure callout / invisible gear / mechanism proof /
  discipline identity]
VOC phrase to use verbatim: [exact quote from Section 9c — state which one]
PDP claim check: [list every performance claim in this concept → confirm ✓ in product-specs]
Why this format: [1 sentence — what does this format test or prove?]
Ten Thousand reference (if applicable): [cite specific ad structure if using as tone model]
─────────────────────────────────────
```

If the concept passes all fields → write it.
If any field is vague, invented, or unchecked → do not write it.

---

## Step 3 — Choose execution type per concept

| Type | When to use |
|---|---|
| **UGC x3 hooks** | Creator footage — talking head, training in context, mechanism explanation |
| **2 statics + 1 video** | Mixed test — static vs video on same mechanism claim |
| **3 statics** | Message-first — when headline specificity is the creative question |
| **Hyrox UGC** | Creator at or training for Hyrox — named first line, station context |
| **Native DTC** | Emotional entry point — anti-athleisure conviction angle |

Prioritise UGC and statics. Do not use motion design unless it's the explicit request.

---

## Step 4 — Write each concept

Use this exact structure:

```
───────────────────────────────────────────────────────────
CONCEPT [N]: [NAME IN CAPS — mechanism + use case]
Execution type: [UGC x3 hooks / 2 statics + 1 video / 3 statics / Hyrox UGC / Native DTC]
Product: [exact SKU]
Angle: [from Tier 1/2/3 in STRATEGIC-BRIEF.md]
Persona tension: [one line — from pre-write declaration]
Funnel stage: [Problem Aware / Solution Aware / Product Aware]
Platform: Meta

STRATEGY
Objective: [1–2 sentences. What conversion moment does this concept address? What fear or desire?]
Hypothesis: [1–2 sentences. Why will this work? Cite VOC evidence, product spec, or client priority.]
Testing logic: [1 sentence. What specific question do these variations answer?]

────────────────────────────────────────────
```

### UGC Concept structure

```
VARIATION 1 — UGC Hook 1 — [GEAR FAILURE / PAIN]
Hook (spoken, 1 sentence): [verbatim — punchy, names a specific failure moment from VOC glossary]
Opening visual: [what the creator does in frame 0–3 seconds]
---
BODY FLOW (shared across all 3 hooks):
⚠️ THIS IS AN EXAMPLE — CREATOR USES THEIR OWN WORDS. Give them the structure, not the script.

Example script:
[Write full body as natural spoken English. First person. Past/present tense. No ad language.
 One thought per sentence. Short. Mechanism named naturally — not as a bullet point.
 Name the brand ("This is A-Game") clearly and early — within first 10 seconds.
 Mechanism → Function → Outcome embedded in the speech, not listed.
 End: "Bring your A-Game."]

Directional beats:
• [Beat 1 — problem context or training moment]
• [Beat 2 — "This is A-Game." + product named]
• [Beat 3 — mechanism woven in naturally]
• [Beat 4 — function/outcome — what that means in training]
• [Beat 5 — CTA: "Bring your A-Game."]

Creator requirements:
  Discipline: [lifting / running / Hyrox / conditioning]
  Platform: [Instagram / TikTok]
  Suggested creator from pool: [name + handle from STRATEGIC-BRIEF.md Section 9d — or "any"]

Shoot list must include:
  • [product clearly visible + well-lit — not distorted]
  • [specific training movement that matches the tension in the hook]
  • [head-to-camera clip for spoken line delivery]
  • [close-up of product feature being described — seam / ventilation / liner]
  Avoid:
  • AI-generated or distorted product images
  • Any outfit combination that doesn't match (check colour coherence)
  • Same Trustpilot reviews used in other videos

VARIATION 2 — UGC Hook 2 — [ANTI-ATHLEISURE CALLOUT]
Hook (spoken, 1 sentence): [names the category failure — "Most [sportswear/training tops]..."]
Opening visual: [what the creator does in frame 0–3 seconds]

VARIATION 3 — UGC Hook 3 — [INVISIBLE GEAR / OUTCOME]
Hook (spoken, 1 sentence): [the "when it works" moment — gear disappears, training is the focus]
Opening visual: [what the creator does in frame 0–3 seconds]

PRE-APPROVAL CHECK — run before outputting
[ ] Does the body explain the mechanism (construction → function → outcome)?
[ ] Is the product introduced early (within 10 seconds)?
[ ] Does "This is A-Game." appear and sound natural?
[ ] Are all 3 hooks attacking different psychological entry points?
[ ] Swap test: could Gymshark say this script? If yes → rewrite.
[ ] Is the tone calm, controlled, athlete-first — not hyped, not salesy?
[ ] If women's: no aggressive tone, no empowerment slogans, no "lockdown/bounce" language?
[ ] Does "Bring your A-Game." close the script?
[ ] Is "sportswear" used instead of "activewear" anywhere in the copy?
[ ] Are all PDP claims confirmed ✓ in product-specs-march-2026.md?
```

---

### Static Concept structure

```
VARIATION 1 — Static — [MECHANISM HEADLINE]
Headline: [3–6 words — mechanism or use-case statement — NOT a brand statement or vague adjective]
Subheading: [1–2 outcome subs — compressed. What the mechanism means in training.]
Visual notes: [what must be shown — product, training context, key feature close-up. Colour match
  check: confirm outfit coherence. Note: "Men's" label only needed once per creative.]
CTA: Bring your A-Game.

VARIATION 2 — Static — [different mechanism or use case territory]
[same structure]

VARIATION 3 — Static — [third angle — proof or outcome]
[same structure]

PRE-APPROVAL CHECK — static
[ ] Is the headline 3–6 words?
[ ] Instant clarity OR instant curiosity — no middle ground?
[ ] Does it name a mechanism or use case — not a sensation or brand statement?
[ ] Does the visual match what the copy describes?
[ ] Swap test pass?
[ ] No standalone "breathable", "comfortable", "supportive" without mechanism explanation?
```

---

### Hyrox UGC structure

**HYROX CREATOR CONTEXT (from meeting notes 19 March 2026):**
- Top 15 Hyrox athletes signed on 3-month contracts — 6 deliverables/month (stills + video mix)
- These are raw, phone-shot UGC — not professional video. Organic feel preferred.
- All athletes confirmed for paid partnership ads (whitelisting). Chris sets up via handles.
- Upcoming events: London late March · Manchester marathon mid-April · Cardiff end of April
- A-Game providing shot references — focus on product detail during movement

```
HYROX UGC CONCEPT [N]: [NAME]
⚠️ HYROX CREATOR REQUIREMENT: Confirm creator has Hyrox race or training experience before briefing.

Hook (spoken, 1 sentence): [HYROX named in first line — specific station or training context]
Opening visual: [creator at training / race / station — product visible and matching the hook]
---
BODY FLOW:
Example script:
[High context, immediate. HYROX named first line.
 Product named within first 10 seconds.
 No motivational fluff — product in real race/training context.
 Stations named: runs, sled push, ski erg, rower, wall balls, burpee broad jumps, sandbag lunges, farmers carry.
 Mechanism → why it holds up across stations.
 "Bring your A-Game." close.]

Station-specific language to reference (verbatim VOC):
• "Inner thighs during lunges, underarms during rowing, waistband during wall balls."
• "Cushion for the runs, control for sled work."
• "Cotton chafes and will make you miserable by station three."

Creator requirements:
  Hyrox athlete or active competitor — confirm with Joshua before briefing
  Suggested: check STRATEGIC-BRIEF.md Section 9d — confirm Hyrox background

Shoot list must include:
  • Training/race footage with product clearly visible
  • At least one station reference in context
  • Head-to-camera delivery
  Avoid: motivational b-roll without product; generic gym footage without Hyrox context
```

---

### Native DTC structure

```
NATIVE DTC CONCEPT [N]: [NAME]
(More emotional entry — grounded in anti-athleisure conviction)

Hook (text or spoken, 1 sentence): [pattern interrupt — calls out the category lie]
Body: [emotional entry → product truth → mechanism → outcome]
  Opens with the tension: "You don't train for the photo. So stop buying gear made for it."
  Names the product + brand.
  Mechanism embedded naturally.
  Outcome: "Remove friction. Focus on the rep."
  Close: "Bring your A-Game."

Visual: [specific — product in training context, not studio. Real movement. Real sweat.]
```

---

## Step 5 — Save .md file

Save to: `a-game/scripts/scripts-[YYYY-MM-DD].md`

Structure:
```
# A-Game — Script Pack
Date: [date]
Concepts: [N]
Priority SKUs scripted: [list]
Visual context confirmed: [yes / partial — list any flagged concepts]

---
[all concepts in full]
---
⚠️ Pending: [list any concepts blocked by missing visual context — needs Joshua to confirm before writing]
*Pending internal review by Joshua + Chris before production.*
```

---

## Step 5b — Create Joshua-Ready Summary (MANDATORY — always output this after the full scripts)

Joshua explicitly requested a simple, scannable format he can forward to Andy/Amy without them
having to navigate Notion. Directors get overwhelmed by large batches — they need quick yes/no
on headlines + copy only.

Always produce this as a separate section AFTER the full scripts:

```
───────────────────────────────────────────────────────────
A-GAME — SCRIPT REVIEW SUMMARY
[Date] | [N] concepts for review
Reply by: [next Tuesday]
───────────────────────────────────────────────────────────

CONCEPT 1 — [NAME]
Product: [SKU]
Format: [UGC / Static / Hyrox]
Reference: [Ten Thousand ad title + "running X+ days" if known — or Pinterest/ASRV reference]
Why this works: [1 sentence — the rational argument Joshua can say out loud to Andy/Amy]

Headline / Hook: [exact line]
Body (compressed): [2–3 sentences — the core product argument only]
CTA: Bring your A-Game.

→ Approve / Reject / Amend: _______________

───────────────────────────────────────────────────────────

CONCEPT 2 — [NAME]
[same structure]

───────────────────────────────────────────────────────────
[repeat for all concepts]
```

**Rules for the Joshua-Ready Summary:**
- Strip all strategy language. Just the product argument.
- One reference per concept — name the Ten Thousand ad (or ASRV/Satisfy) explicitly so Joshua can pull it up when talking to directors. Format: "Inspired by: [brand] — '[ad name]' — running [X]+ days."
- The "Why this works" sentence is what Joshua says to the directors. Write it like he's presenting it. Not like a brief. Like: "This one leads with the kit failure at station four — specific enough that Hyrox athletes will stop scrolling."
- Maximum one A4 page total. If it runs longer, compress harder.

---

## Step 6 — Create Notion tickets (when Notion structure is confirmed)

⚠️ **Notion ticket structure for A-Game is not yet confirmed.** Before creating tickets:
1. Search Notion for "A-Game" creative tickets workspace
2. If A-Game uses the same Creative Tickets DB as Carbeth → use same template IDs
3. If A-Game has separate workspace → find it, confirm template IDs with Joshua
4. Log Notion ticket URL in script file

Until confirmed: save scripts as local .md file only. Do not create Notion tickets blind.

**Carbeth Creative Tickets DB (reference only — use if A-Game shares same DB):**
- Carbeth client ID: `https://www.notion.so/2c5f64437f9b816faa74d9aa5c133d1b`
- Collection: `collection://27df6443-7f9b-81ed-b579-000b5f0058b3`

---

## Tone Calibration — Voice Register Benchmarks

These are not templates. They are voice calibration examples — use them to check register
before declaring a script complete.

### Benchmark 1 — Men's UGC (approved Gold Standard — use to calibrate speaking register)

**What this script does right:**
- "I've tried a lot of training gear" — opens with experience, not a pitch
- "most of it doesn't hold up once you actually train in it properly" — names the category failure without naming a competitor
- "This is A-Game." — brand named clearly, early, simply
- "lightweight, four-way stretch, split hem" — mechanism named naturally in conversation, not listed
- "so nothing restricts you when you're moving between lifts and sprints" — function follows immediately
- "They don't ride up, don't bunch. Just stay out of the way." — outcome in the athlete's language
- "It's built for training — not just wearing to the gym." — the anti-athleisure line without being preachy
- "Bring your A-Game." — CTA is the brand line, not a command

**The test:** Read it aloud. Does it sound like a real athlete telling a friend? If it sounds performed → rewrite.

> Full script: "I've tried a lot of training gear, but most of it doesn't hold up once you actually train in it properly. This is A-Game. The shorts — lightweight, four-way stretch, split hem — so nothing restricts you when you're moving between lifts and sprints. They don't ride up, don't bunch. Just stay out of the way. The tee is the same — breathable, dries fast, and doesn't cling once you start sweating. So it still looks clean, even deep into a session. That's the difference. It's built for training — not just wearing to the gym. Bring your A-Game."

---

### Benchmark 2 — Women's UGC (approved Gold Standard — women's tone calibration)

**What this script does right:**
- "Most training sets feel good for five minutes. Then you start adjusting." — opens with the micro-moment of failure, not a product claim
- Quiet. Not aggressive. Not empowerment-led. Speaks to someone who already trains seriously.
- "support where you need it, without digging in" — benefit named through what it doesn't do, not just what it does
- "So once you start, you don't think about what you're wearing. You just train." — the job to be done, stated cleanly
- Tone: controlled, precise. Not "tough girl". Not "you've got this".

**The test:** Would a serious female athlete feel spoken to, not marketed at? If it has any empowerment language, urgency, or aggressive framing → rewrite.

> Full script: "Most training sets feel good for five minutes. Then you start adjusting. This is A-Game. The leggings are built to stay in place — high-rise, supportive waistband, no slipping mid-session. The bra is lightweight but structured — support where you need it, without digging in. The fabric handles heat properly — breathable, quick-drying, doesn't hold onto sweat. So once you start, you don't think about what you're wearing. You just train. That's the difference. Bring your A-Game."

---

### Benchmark 3 — Static headline register

**What good looks like:**
- "Built for lifting. Running. Conditioning." — use case named, not a brand statement
- "Flatlock seam construction. Sweat-zone mapping. 4-way stretch." — mechanism list as headline — works for product-educated audience
- "Ventilated panels regulate heat under load." — function statement as headline — mechanism implied

**What fails:**
- "Premium sportswear for serious athletes." — could be any brand
- "Train harder." — empty direction
- "Engineered performance." — vague without mechanism

**The test:** Replace A-Game with Gymshark. Does it still work? If yes → rewrite.

---

## Process rules (non-negotiable)

1. Scripts are reviewed by Joshua and Chris before production — always
2. Joshua and Chris must receive: script + copy + graphic headline (all three, together)
3. Deliver in format Joshua can quickly forward to directors: strategy rationale visible + scannable
4. Maximum 4 concepts per run
5. PDP claim check must be completed and documented in the pre-write declaration
6. Scripts go into `a-game/scripts/scripts-[date].md` — always save before doing anything else
7. Do NOT launch production before script approval — this has been an explicit failure point
