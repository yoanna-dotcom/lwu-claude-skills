---
name: init-client
description: >
  Validator and setup tool for the open briefing system. Anyone with Claude Code can run this —
  PSM, CS, or Yoanna. Reads whatever research files exist for a client, reports what's present
  vs missing, auto-generates what it can (BRAND-INTELLIGENCE.md, PERSONA-STRATEGY.md,
  performance-log.md), flags what needs the pipeline (STRATEGIC-BRIEF.md, MUST-READ-SCRIPTING.md),
  and outputs a ready-to-paste Cowork PROJECT-INSTRUCTIONS.md.
  Run any time to check a client's state — not just on first setup.
  Trigger: "/init-client [client-name]"
---

# Init Client — Open Briefing System Validator + Setup

## Trigger

```
/init-client [client-name]
```

Example: `/init-client carbeth-plants`

The `[client-name]` must match the folder name at `~/Desktop/[client-name]/`.

Run this any time — first setup or re-check. If files already exist, it confirms them and outputs the Cowork setup. If anything is missing, it generates what it can and flags what needs the pipeline.

---

## Step 0 — Discover what exists (silent)

Search `~/Desktop/[client-name]/` for any of these (flexible naming — read whatever is found):

**Root level:**
- `BRAND-INTELLIGENCE.md` or `brand-intelligence*.md`
- `PERSONA-STRATEGY.md` or `persona-strategy*.md`
- `STRATEGIC-BRIEF.md` or `strategic-brief*.md`
- `MUST-READ-SCRIPTING.md` or `must-read*.md`
- `AUDIENCE-VOC.md` or `voc*.md`
- `COMPETITOR-BRIEF.md` or `competitor*.md`

**Research subfolder (`research/`):**
- Any `.md` files — read all of them. Common names: `audience-research-v*.md`, `competitor-research-v*.md`, `brand-research-*.md`

**Scripts subfolder (`scripts/`):**
- Any existing brief or script `.md` files — useful for tone reference

Log what's found vs missing. Do not stop if files are missing — synthesise from what exists.

**Notion fallback:** If fewer than 2 files found locally, run `notion-search` for "[client-name] Growth Strategy OS". Fetch Persona Bank, Brand Intelligence, Strategic Brief pages if found.

**Hard stop — only if:** No local files AND no Notion pages found.
→ Output: "I can't find any research for [client]. Run the research pipeline first (`/d2c-research [client-name]`) before initialising."

---

## Step 1 — Report what was found

Use this exact output format. Distinguish clearly between what can be auto-generated vs what requires the pipeline.

```
Checking [Client Name]...

INTELLIGENCE FILES
[✅ exists / ⚠️ missing — will auto-generate] Brand Intelligence
[✅ exists / ⚠️ missing — will auto-generate] Persona Strategy
[✅ exists / ❌ missing — needs /strategic-brief-builder] Strategic Brief
[✅ exists / ❌ missing — needs /strategic-brief-builder] Must-Read Scripting Rules
[✅ exists / ⚠️ missing — will auto-generate] Performance Log
[✅ exists / — not required] Competitor Research

[If any ❌ items: "STRATEGIC-BRIEF.md and/or MUST-READ-SCRIPTING.md are missing.
These can't be auto-generated — they need the full strategy pipeline.
Run /strategic-brief-builder [client-name] first, then re-run /init-client.
Cowork PROJECT-INSTRUCTIONS.md will not be generated until these exist."]

[If only ⚠️ items or all ✅: "Generating missing files now..."]
```

---

## Step 2 — Generate standardised files (only those missing)

For each missing standardised file, generate it from whatever research exists. Save to `~/Desktop/[client-name]/`.

---

### BRAND-INTELLIGENCE.md (if missing)

Synthesise from: audience research, competitor research, any brand research found.

Structure:
```
# [Client Name] — Brand Intelligence

## What this brand does (plain English)
[1 paragraph — product, who it's for, what problem it solves]

## Core differentiators
[3–5 bullet points — the specific mechanisms, not generic claims]

## VOC glossary — verbatim buyer language
[10–15 exact phrases from reviews, research, or customer language found in the research files]

## Primary purchase occasions
[When and why people buy — gift, self-treat, seasonal, repeat etc.]

## Biggest buyer fears / objections before purchase
[3–5 specific anxieties — not generic, pulled from research]

## Failed solutions buyers have tried
[What they tried before this brand — competitors, DIY, nothing]

## Brand restrictions / things to never say
[From MUST-READ-SCRIPTING.md or any brand brief found]
```

---

### PERSONA-STRATEGY.md (if missing)

Synthesise from: audience research, any persona references in the research files.

Structure:
```
# [Client Name] — Persona Strategy

## Persona 1 — [Name]
Demographics: [age, gender, life stage]
Motivation: [why they buy — identity, fear, occasion]
Core tension: [the specific frustration they have before buying]
VOC phrase: [verbatim quote from research]
Buying trigger: [what tips them from browsing to buying]

## Persona 2 — [Name]
[Same structure]

## Persona 3 — [Name]
[Same structure]

[Up to 4 personas — stop at 4. Quality over quantity.]
```

---

### feedback/performance-log.md (if missing)

Copy the standard performance log template. Save to `~/Desktop/[client-name]/feedback/performance-log.md`.

Use this exact content:
```
# [Client Name] — Performance Log

This file tracks what creative has run, how it performed, and what Claude should factor in before building the next brief. Update after each cycle once results are in (2–4 weeks post-launch).

---

## Log

| Date | Concept | Format | Angle | Persona | Result | Verdict | Notes |
|------|---------|--------|-------|---------|--------|---------|-------|
| | | | | | | | |

---

## Verdict guide
| Verdict | When to use |
|---------|------------|
| Run Again | Strong result — repeat the angle, format, or persona |
| Iterate | Some signal but not enough — note what to change |
| Kill | Underperformed — don't revisit without a strong reason |

---

## Patterns Claude watches for
- 2+ Kill verdicts on the same angle → flagged as territory to avoid
- Consistent strong results on a format → prioritised in next brief
- Personas with no recent coverage → flagged as a gap
- Client feedback notes → fed into tone and visual direction
```

---

## Step 3 — Generate Cowork PROJECT-INSTRUCTIONS.md

Read the now-complete set of knowledge files and generate a client-specific PROJECT-INSTRUCTIONS.md ready to paste into claude.ai.

Save to: `~/Desktop/[client-name]/cowork-setup/PROJECT-INSTRUCTIONS.md`

Use `~/Desktop/Claude/open-briefing-system/claude-project-setup/PROJECT-INSTRUCTIONS-TEMPLATE.md` as the base.

Substitute:
- `[CLIENT_NAME]` → client's full name (e.g. "Carbeth Plants")
- `[CLIENT_SHORT]` → short name (e.g. "Carbeth")
- `[PERSONA_1_LABEL]` through `[PERSONA_4_LABEL]` → top 4 persona names from PERSONA-STRATEGY.md
- `[PERSONA_1_DESC]` through `[PERSONA_4_DESC]` → one-line description for each persona
- `[ANGLE_1_LABEL]` through `[ANGLE_4_LABEL]` → top 4 Tier 1/2 angles from STRATEGIC-BRIEF.md
- `[ANGLE_1_DESC]` through `[ANGLE_4_DESC]` → one-line rationale for each angle
- `[PRODUCT_1_LABEL]` through `[PRODUCT_4_LABEL]` → priority SKUs/collections from STRATEGIC-BRIEF.md
- `[PRODUCT_1_DESC]` through `[PRODUCT_4_DESC]` → one-line description per product

---

## Step 4 — Output result

### If any ❌ items (STRATEGIC-BRIEF.md or MUST-READ-SCRIPTING.md missing):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⛔ [Client Name] — setup incomplete.

[List what exists ✅ and what's missing ❌]

The following files can't be auto-generated and must come from the strategy pipeline:
❌ STRATEGIC-BRIEF.md
❌ MUST-READ-SCRIPTING.md

Run this first:
  /strategic-brief-builder [client-name]

Then re-run /init-client [client-name] to complete setup.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### If all files exist or only ⚠️ items (auto-generated):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ [Client Name] — ready for the open briefing system.

Files confirmed / generated:
[List each: ✅ already existed / ✅ auto-generated / ✅ auto-generated from partial data*]

📁 Cowork-ready instructions saved to:
~/Desktop/[client-name]/cowork-setup/PROJECT-INSTRUCTIONS.md

---

NEXT STEPS — 5 minutes in claude.ai:

1. Go to claude.ai → Projects → New Project
   Name it: PSM Brief Builder — [Client Name]

2. Paste Project Instructions:
   Open ~/Desktop/[client-name]/cowork-setup/PROJECT-INSTRUCTIONS.md
   Select all → Copy → Paste into Project Instructions → Save

3. Upload knowledge files:

   From ~/Desktop/[client-name]/:
   ✅ BRAND-INTELLIGENCE.md
   ✅ PERSONA-STRATEGY.md
   ✅ STRATEGIC-BRIEF.md
   ✅ MUST-READ-SCRIPTING.md

   From ~/.claude/skills/psm-brief-builder/:
   ✅ LWU-CREATIVE-CONTEXT.md
   ✅ LWU-SCRIPTING-BEST-PRACTICES.md

4. Test it:
   Open a new conversation in the project.
   Claude should introduce itself and start asking questions immediately.

---

[*If any files were auto-generated from partial data:]
⚠️ Quality note: [Which file] was synthesised from [what source only].
[Plain-English sentence on what this means for brief quality and when it will sharpen.]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
