---
name: strategic-brief-builder
description: >
  Builds STRATEGIC-BRIEF.md and MUST-READ-SCRIPTING.md for any D2C brand by synthesising all
  upstream handover documents into a single creative intelligence layer. Reads BRAND-INTELLIGENCE.md,
  PERSONA-STRATEGY.md, AUDIENCE-VOC.md, and COMPETITOR-BRIEF.md in parallel. Outputs tiered
  angles, persona-to-hook maps, VOC glossary, format playbook, and hard constraints. Trigger on:
  "build the strategic brief", "run the brief builder", "create the brief", "we need a strategic
  brief", or whenever BRAND-INTELLIGENCE.md exists but STRATEGIC-BRIEF.md does not.
---

# Strategic Brief Builder

This skill is the synthesis layer between research and scripting. It does not run any new research
— it reads what the upstream skills confirmed, resolves conflicts, tiers the evidence, and outputs
the single document every script builder, hook builder, and CS reads before writing line one.

**What this skill produces:**
- `STRATEGIC-BRIEF.md` — full creative intelligence brief for this brand
- `MUST-READ-SCRIPTING.md` — stripped hard constraints + approval checklist for scripting sessions

**What this skill does NOT do:**
- Run new research (that is d2c-research, audience-research, competitor-research)
- Build personas (that is d2c-persona-strategist)
- Write scripts or hooks (that is the script builder skills)
- Invent or extrapolate — if a handover doc doesn't contain it, it doesn't appear in the brief

---

## Step 0 — Read all handover documents in parallel (mandatory first step)

Read simultaneously:
- `[client-folder]/BRAND-INTELLIGENCE.md`
- `[client-folder]/PERSONA-STRATEGY.md`
- `[client-folder]/AUDIENCE-VOC.md`
- `[client-folder]/COMPETITOR-BRIEF.md`
- `[client-folder]/ACCOUNT-AUDIT.md`

**If BRAND-INTELLIGENCE.md is missing:** STOP. Output:
```
BRIEF CANNOT BE BUILT — BRAND-INTELLIGENCE.md not found.

This document contains the confirmed USPs, pain points, and language rules that the entire
brief is built from. Run d2c-research first and ensure BRAND-INTELLIGENCE.md was generated
before running the strategic brief builder.
```

**If any other doc is missing:** Continue. Note explicitly in the brief which doc is absent
and what that means for brief confidence:
- PERSONA-STRATEGY.md missing → Persona → Tension → Hook map cannot be built. Angles are
  listed without persona targeting. Run d2c-persona-strategist before scripting.
- AUDIENCE-VOC.md missing → No Reddit validation available. All Tier 1 angles are downgraded
  to Tier 2. Run audience-research before scripting.
- COMPETITOR-BRIEF.md missing → Whitespace map unavailable. All angles treated as Contested
  until competitor research confirms whitespace. Run competitor-research before scripting.
- ACCOUNT-AUDIT.md missing → No account performance context. Brief will lack validated
  strengths, repeatable formula, and format-to-job mapping from real ad data. Angles are
  tiered without performance validation. Run the Creative Audit (Notion) then
  /audit-interpret before scripting.

---

## Step 0.5 — Extract and hold in context

From **BRAND-INTELLIGENCE.md:**
- Confirmed USPs (Proven verdict only) — these are the creative pillars
- Top 5 pain points verbatim — exact language only, no paraphrasing
- Top 3 failed solutions verbatim — the most underused hook territory
- Three Consistent Truths — cross-source findings
- USP → Hook Territory map — already partially built; sharpen it in Step 1
- Language to Avoid — all rules, copied verbatim into MUST-READ-SCRIPTING.md

From **PERSONA-STRATEGY.md:**
- Personas priority-ranked with scores
- Per persona: pain points, desired outcomes, awareness stage (TE stage), mechanism → messaging
  direction mapping
- Trigger events per persona (psychological + contextual)
- What to validate questions (flags unconfirmed findings)

From **AUDIENCE-VOC.md:**
- Repetitive Reddit themes — desired outcomes, emotional pain points, failed solutions that
  appear consistently across multiple posts (not single mentions)
- New phrases not in PERSONA-STRATEGY.md — Reddit language the persona strategist didn't have

From **COMPETITOR-BRIEF.md:**
- USP whitespace map — Clear / Contested / Saturated per USP
- Differentiation strategies ranked
- Saturated angles — what competitors already own
- Competitor failure quotes — verbatim complaints about competitors
- Cross-competitor emotional pattern — the single most important competitive insight
- What competitors do well that the brand can borrow or adapt (format, angle, proof structure)

From **ACCOUNT-AUDIT.md:**
- Cross-phase findings — patterns from the CS's audit that span multiple analysis dimensions
- Validated strengths — what's already working in the account and why (protect these)
- Risk signals — concentration risk, fatigue risk, funnel gaps (with severity)
- Strategic opportunities — ranked, each tied to a specific audit finding
- Repeatable creative formula — winning video structure + hook patterns + format-to-job map
- Score discrepancies — where the CS's scores diverged from data (flagged for resolution)
- Creative Health Score (/25) and Creative Diversity Score (%) — account benchmarks

---

## Step 1 — Resolve conflicts and tier the evidence

Run this pass before writing anything.

**Conflict check:** Compare what BRAND-INTELLIGENCE.md confirmed against what AUDIENCE-VOC.md
found on Reddit. Flag any disagreement:
- USP listed as Proven in reviews but not confirmed on Reddit → downgrade to Tier 2
- Pain point strong in reviews but absent from Reddit → note as "review-only signal"
- Reddit surfaces a pain point not in reviews → surface as "new finding" in the brief

Do not silently resolve conflicts. Surface them in Section 9 (Conflict Log) of the brief.
The CS decides which source to trust for creative — not the skill.

**Angle tiering — apply to every available angle:**

| Tier | Criteria | Default scripting rule |
|---|---|---|
| **Tier 1** | Review evidence + Reddit confirmation + Clear whitespace | Script by default |
| **Tier 2** | Review evidence + Contested whitespace OR review evidence without Reddit confirmation | Script with caution — note what's unconfirmed |
| **Tier 3** | Review evidence only, no Reddit validation, no whitespace data | Flag before scripting — confirm with CS |
| **Saturated** | 2+ competitors run this angle — client has no demonstrably stronger proof | Do not use unless brief explicitly unlocks it |

---

## Step 2 — Build STRATEGIC-BRIEF.md

---

### Section 1: The One Thing

One sentence. The emotional arc of this brand's buyer.

Format: `"[Persona type] who [specific before state in their words] — until [what changes after buying]."`

Rules:
- No brand name. No product name.
- Must use verbatim language from VOC where possible.
- Must pass the swap test: could a competitor say this unchanged? If yes, rewrite it.
- Every script from this brand starts by reading this sentence.

---

### Section 2: Persona → Tension → Mechanism → Hook Map

For each persona in priority order (P1 first):

| Element | Content |
|---|---|
| **Persona** | [name, archetype, priority score] |
| **Core tension** | [the specific frustration they carry — verbatim from reviews or Reddit] |
| **Awareness stage** | [Trigger / Exploration / Evaluation / Purchase] |
| **USP that resolves it** | [specific confirmed Proven USP from BRAND-INTELLIGENCE.md] |
| **Mechanism** | "Works by [specific process] which means [specific outcome for this persona]" |
| **Audience messaging direction** | [how the mechanism translates into a message for this specific person — not generic, persona-specific] |
| **Trigger event** | [the moment — psychological or contextual — that makes this persona receptive] |
| **Hook direction** | [opening territory — not a finished hook. One sentence on what the hook must do.] |

This map is the primary input for the script builder. Every concept brief should map back to
one row of this table.

---

### Section 3: Available Angles — Tiered

List every available angle with its tier, evidence, and whitespace status.

**Tier 1 — Script by default:**
- **[Angle name]**
  Evidence: "[review verbatim]" + "[Reddit verbatim]"
  Whitespace: Clear
  Hook direction: [one line — what the opening should do]
  SKU match: [product(s) this angle works for]

**Tier 2 — Script with caution:**
- **[Angle name]**
  Evidence: [what's confirmed] | Gap: [what's missing]
  Whitespace: Contested — [which competitor runs this]
  Note: [what the CS should confirm before briefing]

**Tier 3 — Flag before scripting:**
- **[Angle name]**
  Evidence: Reviews only — not Reddit-validated
  Action required: CS to confirm this angle is worth testing before script is written

**Saturated — Do not use:**
- **[Angle name]** — owned by: [competitor(s)] — their angle: [what they run]
  Exception: Only use if client has demonstrably stronger proof (note what that would require)

---

### Section 4: Hard Constraints

**Copied verbatim into MUST-READ-SCRIPTING.md. These are non-negotiable.**

**Language banned** (from Language to Avoid in BRAND-INTELLIGENCE.md):
- [exact phrase] — reason: [why]

**Claims not to make:**
- [Unproven USPs from BRAND-INTELLIGENCE.md]
- [Any brand-stated restrictions from onboarding form]

**Formats that don't work for this brand:**
- [If evidence exists from competitor or performance data — otherwise note as unknown]

**Do not write like:**
[One sentence — the most important negative creative constraint for this brand]

---

### Section 5: Priority SKU Queue

Which products to script first.

| Rank | Product | Reason | Persona match | Angle tier | AOV note |
|---|---|---|---|---|---|
| 1 | [product] | [why first] | [P1.X name] | Tier [X] | [AOV data if in onboarding form] |
| 2 | [product] | | | | |

Ranking logic (in order): Tier 1 angle availability → persona match confidence → AOV data
from onboarding form → whitespace clarity.

If AOV data is not available: rank by persona match + angle tier only. Note the gap.

---

### Section 6: VOC Glossary

20–30 phrases from across all handover documents. Real sources only.

| Phrase | Source | Tier | Best use |
|---|---|---|---|
| "[exact phrase]" | Reviews / Reddit / Both | 1 / 2 / 3 | Hook / Body / CTA |

**Rules:**
- No invented language. Every phrase must trace to a real review, Reddit post, or
  verbatim quote in a handover doc.
- Tier matches the angle tier of the context it came from.
- "Best use" guidance: Hook = scroll-stop opening. Body = agitation or proof. CTA = desire/action.

---

### Section 7: Format Playbook

Per persona — which ad formats to brief and why.

| Persona | Format | Why it works | TE stage | Vailance zone | Production notes |
|---|---|---|---|---|---|
| [P1.X] | [format] | [linked to bias, zone, or stage] | [stage] | [zone] | [shoot style, creator type] |

**What competitors do well — borrowable:**
From COMPETITOR-BRIEF.md — formats or angles the brand can adapt (not copy):
- [Format/approach] — competitor using it: [brand] — why it works: [reason] — how to adapt: [direction]

Note: borrowing means taking the *structure or proof approach*, not the messaging. Adapt to
confirmed client USPs and VOC only.

---

### Section 8: Competitive Edge Summary

**Cross-competitor emotional pattern:**
[The consistent complaint appearing across multiple competitor reviews — this is the brief's
most important creative insight. Name it explicitly. It becomes the emotional territory no
competitor is solving well.]

**Top differentiation strategies:**
1. [Strategy] — exploits: "[competitor weakness verbatim]" — leverages: [client confirmed USP]
2. [Strategy] — exploits: "[verbatim]" — leverages: [USP]
3. [Strategy] — exploits: "[verbatim]" — leverages: [USP]

**Competitor failure quotes — hook territory:**
These are verbatim complaints about competitors. They name the problem without naming the brand.

| Quote | What it unlocks |
|---|---|
| "[exact complaint]" | [how this becomes a hook opening] |

Minimum 3 quotes. More if available.

---

### Section 9: Conflict Log

Disagreements between handover documents. Do not silently resolve — surface for CS decision.

| Conflict | Source A says | Source B says | Recommended action |
|---|---|---|---|
| [USP / angle / finding] | [BRAND-INTELLIGENCE.md verdict] | [AUDIENCE-VOC.md finding] | [which source to trust + why] |

If no conflicts found: state "No conflicts found between handover documents."

---

## Step 3 — Save STRATEGIC-BRIEF.md

Save to: `[client-folder]/STRATEGIC-BRIEF.md`

File header:
```markdown
# [CLIENT NAME] — Strategic Creative Brief
Generated: [YYYY-MM-DD]
Sources: BRAND-INTELLIGENCE.md · PERSONA-STRATEGY.md · AUDIENCE-VOC.md · COMPETITOR-BRIEF.md
Missing inputs: [list any absent docs and their impact on brief confidence]
```

Log the file path. If this file cannot be saved, the run is incomplete.

---

## Step 4 — Generate MUST-READ-SCRIPTING.md

Stripped version. Short enough to paste at the start of any scripting session.
Contains only what a script builder needs before writing line one.

Save to: `[client-folder]/MUST-READ-SCRIPTING.md`

```markdown
# [CLIENT NAME] — Must-Read Before Scripting
Generated: [YYYY-MM-DD] | Source: STRATEGIC-BRIEF.md

---

## The One Thing
[exact sentence from Section 1]

---

## Hard Constraints — Non-Negotiable

**Language banned:**
- [list]

**Claims not to make:**
- [list]

**Do not write like:**
[one sentence]

---

## Saturated Angles — Do Not Use
- [angle] — owned by [competitor]

---

## Approval Checklist — Run before submitting any script

- [ ] Hook uses a Tier 1 or Tier 2 angle only (no Tier 3 without CS approval)
- [ ] No banned language from Hard Constraints above
- [ ] Hook matches the awareness stage of the target persona (Trigger = empathy; Exploration = credibility; Evaluation = proof; Purchase = urgency)
- [ ] At least one VOC phrase from the glossary used verbatim somewhere in the script
- [ ] The product mechanism appears in the script — even implied, never just a claim
- [ ] Swap test passed: read the hook aloud and ask "could [main competitor] say this unchanged?" If yes, rewrite.
- [ ] No claims made from Unproven USPs
```

Log the file path. If this file cannot be saved, the run is incomplete.

---

## Step 5 — Notion page (deferred — do not run during brief build)

Notion sync is handled separately after the brief build completes. Do not create a Notion page
during this skill. The CS will run the notion-sync skill when ready.

STRATEGIC-BRIEF.md and MUST-READ-SCRIPTING.md are the primary deliverables.

---

## Quality checklist — BLOCKING

Before declaring the run complete:

- [ ] The One Thing passes the swap test — specific to this brand, not usable by a competitor
- [ ] Every Tier 1 angle has BOTH review verbatim AND Reddit verbatim in the brief
- [ ] No angle labelled Tier 1 has Contested or Saturated whitespace
- [ ] Persona → Tension → Mechanism → Hook map covers every priority persona
- [ ] VOC Glossary has minimum 20 phrases, all traced to a real source
- [ ] Hard Constraints section is non-empty and copied into MUST-READ-SCRIPTING.md
- [ ] Conflict Log is present (even if empty — must be explicitly stated)
- [ ] STRATEGIC-BRIEF.md saved — path logged
- [ ] MUST-READ-SCRIPTING.md saved — path logged
- [ ] Any missing handover docs noted with their impact on brief confidence
- [ ] Notion page created — URL logged (or failure noted)
