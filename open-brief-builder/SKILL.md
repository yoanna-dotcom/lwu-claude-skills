---
name: open-brief-builder
description: >
  Reads a brief entry from the client's Open Brief System Notion database, loads all brand
  context, validates the angle against the STRATEGIC-BRIEF.md tier system, matches relevant
  execution frameworks from the LWU creative library, writes full creative briefs with
  referenced examples, and pushes the output back to Notion as a child page of the brief entry.
  Trigger: "/open-brief-builder [Notion URL of the brief entry]"
---

# Open Brief Builder

## What this skill does

Takes one Notion brief entry (filled by the CS) → loads all brand intelligence → validates
the angle → matches execution frameworks from the LWU library → writes the full creative
brief with framework references and copy → pushes it back to Notion as a child page.

The CS fills the brief database row. Claude does everything after that.

---

## Trigger

```
/open-brief-builder [Notion URL of the specific brief entry]
```

The CS creates the row in the Open Brief System database first, then sends this trigger.

If no URL is provided, ask: "Please share the Notion URL of the brief entry you'd like me to build."

---

## Global references (read-only — do not modify)

**LWU Static Frameworks Library:**
https://www.notion.so/launchwithus/Static-Ads-Frameworks-AI-Prompt-Document-5eaf64437f9b83808aca81bfe1823206

**LWU UGC Frameworks Library:** Not yet built. When Format = UGC, apply UGC execution
principles from the STRATEGIC-BRIEF.md Format Playbook and note: "UGC framework library
coming — applied Format Playbook principles instead."

---

## Step 0 — Fetch the brief entry

Fetch the Notion page at the provided URL using `notion-fetch`.

Extract and log these fields:
- **Concept** — the brief title / concept name
- **Format** — Static / UGC / HP
- **Angle** — the creative angle (e.g. Gifting, Social Proof, Superiority)
- **Macro Persona** — P1 / P2 / P3 / P4
- **Micro Persona** — P1.1 / P2.3 / etc.
- **Product/Offer** — SKU or offer name
- **Destination** — HP or PDP
- **Variations** — number of creative variants to produce
- **Creator** — Brand or [Creator name]
- **Date** — brief date

If any of Concept, Format, Angle, or Macro Persona are blank, stop and output:
"The following required fields are empty in the brief entry: [list]. Please fill them in Notion and re-trigger."

---

## Step 1 — Load brand context (run in parallel)

Determine the client folder by searching `~/Desktop/` for a folder matching the brand name
from the Notion page ancestry or concept title. Common path pattern: `~/Desktop/[brand-name]/`

Read all of the following simultaneously:

- **MUST-READ-SCRIPTING.md** — `[client-folder]/MUST-READ-SCRIPTING.md`
  → HARD STOP if missing: "MUST-READ-SCRIPTING.md not found. Run strategic-brief-builder first."

- **STRATEGIC-BRIEF.md** — `[client-folder]/STRATEGIC-BRIEF.md`
  → HARD STOP if missing: "STRATEGIC-BRIEF.md not found. Run strategic-brief-builder first."

- **ACCOUNT-AUDIT.md** — Glob `[client-folder]/` for `ACCOUNT-AUDIT.md`
  → If found: read Repeatable Creative Formula + confirmed angle rankings + fatigue signals
  → If absent: log "ACCOUNT-AUDIT.md not found — proceeding without account performance layer"

- **BRAND-INTELLIGENCE.md** — `[client-folder]/BRAND-INTELLIGENCE.md`
  → If found: read TOV, confirmed USPs, language to avoid
  → If absent: log "BRAND-INTELLIGENCE.md not found — using STRATEGIC-BRIEF.md as sole brand reference"

---

## Step 2 — Validate the angle

Find the Angle from Step 0 in the STRATEGIC-BRIEF.md angle tier list. Match by name or
closest semantic match (e.g. "Gifting" matches "Gift: solves the unsolvable").

**Validation outputs:**

| Tier | Output |
|---|---|
| Tier 1 | ✅ [Angle] — Tier 1. Proceed. |
| Tier 2 | ✅ [Angle] — Tier 2. Proceed with caution — contested whitespace noted. |
| Tier 3 | ⚠️ [Angle] — Tier 3. Limited review evidence. Proceeding as instructed — brief quality may be lower without strong VOC grounding. |
| Saturated | ⚠️ [Angle] — Saturated in this category. Competitors run this heavily. Proceeding as instructed — differentiation will need to come from mechanism specificity, not angle alone. |
| Not found | ⚠️ [Angle] not found in STRATEGIC-BRIEF.md. Proceeding without tier context — Claude will apply brand VOC and best judgement. |

**Do not refuse.** Always proceed after the flag. The CS owns the angle decision.

---

## Step 3 — Match execution frameworks

### If Format = Static

Fetch the LWU Static Frameworks Library (URL above) using `notion-fetch`.

Read the Trigger Quick Reference table. Match 2–3 frameworks that best fit the combination of:
- Angle (from Step 0)
- Macro Persona emotional trigger
- Destination (HP = broader appeal, PDP = purchase-ready, specificity-led)
- Creator type (Brand = cleaner design, [Creator] = UGC-native overlay styles)

For each selected framework, note:
- Framework number and name
- The Notion link to that framework's section (use the main library URL with #anchor if available,
  otherwise link to the main library page)
- One sentence on why this framework fits this brief

**Framework matching heuristics by Angle:**

| Angle | Prioritise these framework types |
|---|---|
| Gifting | Proof-of-recipient-reaction, before/after emotional payoff, "who it's for" persona targeting, pull-quote reviews, curiosity gap |
| Social Proof | Verified review cards, annotated testimonials, comment screenshots, social proof walls, UGC + review splits |
| Superiority / Us vs Them | Side-by-side comparison, benefit checklist, us-vs-them colour split, graph/chart comparison |
| Heritage / Nostalgia | Manifesto/letter ad, bold statement, founder story, editorial content card |
| Product Feature | Feature arrow callout, "what's inside" exploder, routine stack, product hero + stat bar |
| Urgency / Offer | Countdown card, offer burst, promo variant, guarantee/risk reversal |

**If Foreplay board links are present in the framework page:** Include them verbatim in the
brief output under "More references."

### If Format = UGC

Apply UGC execution structure from STRATEGIC-BRIEF.md Format Playbook. Note the absence
of UGC framework library. Structure output as:
- Hook type (problem/solution, identity, social proof, day-in-life, unboxing)
- Scene breakdown (scene 1 / scene 2 / scene 3 with timing)
- Creator direction notes

### If Format = HP (video)

Apply video script structure: Hook (0–3s) / Problem (3–8s) / Mechanism (8–15s) / Proof (15–22s) / CTA (22–30s).

---

## Step 4 — Run declaration before writing

Output this block before writing a single word of brief:

```
OPEN BRIEF BUILDER — RUN DECLARATION
──────────────────────────────────────────────────────
Brand: [name]
Concept: [concept title from Notion]
Format: [Static / UGC / HP]
Angle: [angle name] — [Tier X / Saturated / Not found]
Macro Persona: [P1–P4] | Micro Persona: [P1.x]
Product/Offer: [product name]
Destination: [HP / PDP]
Variations: [N]
Creator: [Brand / Creator name]
Frameworks selected: [names]
Brand context loaded: STRATEGIC-BRIEF ✅ | MUST-READ ✅ | ACCOUNT-AUDIT [✅/❌] | BRAND-INTELLIGENCE [✅/❌]
──────────────────────────────────────────────────────
[Any angle validation warnings here]
```

---

## Step 5 — Write the creative brief

Write one complete brief per variation (up to N from the Variations field).

If Variations = 1: write the single strongest concept.
If Variations = 2–4: write each as a distinct concept with different hook direction or
framework — do not repeat the same approach with minor copy changes.
If Variations = 5+: apply the 50/50 rule — half extend the brief's angle with strong
VOC grounding, half explore adjacent territory within the same angle.

---

### Brief structure per variation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCEPT [N] — [Descriptive name]
Format: [Static / UGC / Video] | Creator: [Brand / Creator]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STRATEGY
Persona: [Macro/Micro name + one sentence on who this is]
Tension: [The specific fear or friction this ad resolves]
Mechanism: [The product feature or proof that resolves it]
Why now: [Trigger event or reason this lands right now]

EXECUTION FRAMEWORK
Framework: [Name + number]
Reference: [Notion link to framework page]
Why this framework: [One sentence]
[Foreplay board: link — if available]

HOOK OPTIONS (pick one or test all three)
Hook 1 — [Tension/Fear]: [copy — static: 3–6 words / video: 1 spoken sentence]
Hook 2 — [Identity/Realisation]: [copy]
Hook 3 — [Reward/Outcome]: [copy]
VOC source: "[verbatim phrase from VOC glossary that grounds these hooks]"

COPY / SCRIPT
[For Static:]
Panel 1: [headline / hero copy]
Panel 2: [proof / mechanism]
Panel 3: [CTA + offer if applicable]
Body copy (if used): [supporting copy — max 2 lines]

[For UGC:]
Scene 1 (0–3s): [hook + visual direction]
Scene 2 (3–12s): [problem/agitation + creator direction]
Scene 3 (12–22s): [mechanism + proof moment]
Scene 4 (22–28s): [CTA + verbal close]
Creator notes: [tone, energy, what to avoid]

[For Video:]
Hook (0–3s): [visual + VO]
Problem (3–8s): [VO + scene]
Mechanism (8–15s): [product demo or proof moment]
Proof (15–22s): [social proof or VOC line]
CTA (22–30s): [verbal + text overlay]

CTA: [specific CTA copy]
Destination: [HP / PDP]

PRODUCTION NOTES
Assets needed: [list what's required — product shots, lifestyle, UGC footage, etc.]
Design notes: [colour, layout, overlay style if relevant]
Copy placement: [where each copy element sits on the creative]

CONSTRAINTS CHECK
✅ Passes swap test — [competitor] cannot say this
✅ No banned language from MUST-READ-SCRIPTING.md
✅ Grounded in VOC — [specific phrase used]
[⚠️ flags if any constraint is borderline]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 6 — Quality gates (blocking — fix before output)

Run every concept through these checks before proceeding to Step 7:

- [ ] **Swap test** — Replace brand with main competitor. Hook and body must stop working. If it passes unchanged, rewrite.
- [ ] **MUST-READ-SCRIPTING.md compliance** — No banned language, no unproven claims, no saturated phrases.
- [ ] **VOC grounding** — Minimum 1 line per concept anchored to a real phrase from the VOC Glossary in STRATEGIC-BRIEF.md.
- [ ] **Angle tier compliance** — If angle is Saturated, differentiation must come from mechanism specificity in the copy, not just different words for the same claim.
- [ ] **Hook format rules** — Static hooks: 3–6 words. Video/UGC hooks: 1 spoken sentence. No "Are you...", "Introducing...", "Have you ever..." openers.
- [ ] **Awareness stage match** — Cold/TOF copy must not assume product knowledge. If Destination = PDP, copy can be more specific.

If any check fails: fix the concept inline. Do not output failing concepts.

---

## Step 7 — Push to Notion

Create a child page inside the brief entry using `notion-create-pages`.

**Page title:** `[Concept name] — Brief [YYYY-MM-DD]`
**Parent:** The Notion page URL provided in the trigger

**Page content structure:**
1. Blue callout: file path of local brief if saved, date, angle tier, frameworks used
2. Each concept as a section (H2 heading = concept name)
3. Framework references as inline links
4. Foreplay board links in a yellow callout if present
5. Red callout at bottom: MUST-READ-SCRIPTING.md constraints reminder (pulled verbatim)

---

## Step 8 — Save locally + output summary

Save the full brief output to:
`[client-folder]/briefs/brief-[concept-slug]-[YYYY-MM-DD].md`

Then output to CS:

```
──────────────────────────────────────────────────────
✅ Open Brief complete — [Concept name]
📄 Notion: [child page URL]
📁 Local: [client-folder]/briefs/brief-[slug]-[date].md

[N] concepts written | Framework(s): [names]
Angle: [name] — [Tier X]
[Any warnings surfaced during the run]

When concepts are signed off → send: "Push [Brand] briefs to production — [date]"
──────────────────────────────────────────────────────
```

---

## Quality checklist — BLOCKING before declaring complete

- [ ] All N variations produced (matching the Variations field from Notion)
- [ ] Every concept passes all 6 quality gates from Step 6
- [ ] Framework references included with Notion links
- [ ] Notion child page created — URL logged
- [ ] Local brief file saved — path logged
- [ ] Angle validation flag surfaced (or confirmed clean)
- [ ] MUST-READ constraints reminder in Notion output
