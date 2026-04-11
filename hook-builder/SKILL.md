---
name: hook-builder
description: >
  Standalone D2C hook generator. Produces 5-6 hooks for any brand or brief.
  Reads STRATEGIC-BRIEF.md for grounding, can also surface original angles not yet tested.
  Runs the swap test automatically on every hook before outputting — only passing hooks shown.
  Saves output to client folder + outputs in chat.
  Trigger: "Run hook builder" or "Build hooks for [brand]".
  Claude will explicitly ask for format (static/video/UGC) and persona if not specified.
---

# D2C Hook Builder

## Trigger prompt

```
Run hook builder.

Brand: [CLIENT NAME]
Format: [Static / Video-UGC / Both — leave blank and Claude will ask]
Persona: [which persona — from STRATEGIC-BRIEF.md — or leave blank and Claude will ask]
Angle / theme: [specific angle to explore — or "use priority angles from STRATEGIC-BRIEF.md"]
Extra context: [campaign brief, seasonal moment, production constraint, anything not in files]
```

**Minimum required:** Brand only. Claude asks for Format and Persona if not specified.

---

## Step 0 — Ask for missing required fields before doing anything else

If **Format** is not specified in the trigger:
→ STOP. Ask: "What format are these hooks for? Static (3–6 words) / Video-UGC (1 spoken sentence) / Both?"
→ Wait for answer. Do not proceed until confirmed.

If **Persona** is not specified:
→ Ask: "Which persona? I'll default to the priority persona from STRATEGIC-BRIEF.md unless you specify a different one."
→ If the response is "use priority persona" or similar → proceed.

Do NOT guess on format. Static hooks and video/UGC hooks are structurally different and cannot be assumed from context.

---

## Step 1 — Read inputs

Read in parallel:

- `[client-folder]/STRATEGIC-BRIEF.md` — persona tensions, VOC glossary, priority angles (Tier 1/2/3), confirmed whitespace, hard constraints
- `[client-folder]/MUST-READ-SCRIPTING.md` — banned language and hard brand rules

If STRATEGIC-BRIEF.md is missing:
→ Proceed with creative freedom only.
→ Output this warning before the hooks: "⚠️ No STRATEGIC-BRIEF.md found in [client-folder]/. Hooks generated from trigger context only — not grounded in confirmed VOC or account data. Build STRATEGIC-BRIEF.md for grounded output."

If MUST-READ-SCRIPTING.md is missing:
→ Note it. Proceed. Apply universal hook quality rules only.

---

## Step 2 — Generate hooks

Produce 5–6 hooks total. Vary the theme/psychological entry point across the full set — never repeat the same type in one run.

**Themes to vary across the set (use a different one for each hook):**
- **Tension / fear of failure** — names a specific failure moment the audience recognises
- **Realisation / identity** — the moment of "wait, this is me" recognition
- **Reward / outcome** — the "when it works" payoff, told from the other side
- **Curiosity / pattern interrupt** — creates a knowledge gap or unexpected angle
- **Seasonal / timing** — time-bound relevance tied to a moment or event
- **Social proof / peer signal** — what everyone else already knows

**Grounding rule:**
At least 3 hooks must be anchored to confirmed VOC, angle tiers, or tensions from STRATEGIC-BRIEF.md.
1–2 hooks can explore original angles not yet in the brief — label these clearly as "Original angle."

**Format-specific rules:**

*Static hooks:*
- 3–6 words maximum
- Instant clarity OR instant curiosity — no middle ground
- Must be an outcome, tension, or use-case — NOT a brand statement or vague adjective
- Test-ready as headline text

*Video/UGC hooks:*
- 1 spoken sentence — no clause before the point
- Must sound said, not written — read it aloud before finalising
- Opens with tension, curiosity, or a specific named problem
- Do not start with "Are you...", "Have you ever...", or "Introducing..."

---

## Step 3 — Swap test (auto-run, internal — never skipped)

Before including any hook in the output, run the swap test internally:
→ Replace the brand name with the main direct competitor.
→ Does the hook still work unchanged? If yes → rewrite until it fails the swap test.
→ Only hooks that fail the competitor swap test (i.e. are brand-specific enough) appear in the output.

If a hook was rewritten due to swap test failure:
→ Note: "[Rewritten — original version was too generic]"

If a hook could not be made specific enough after two rewrites:
→ Drop it. Do not include it. Note the dropped theme if relevant.

---

## Step 4 — Output

```
─────────────────────────────────────────────────────────
[BRAND] — Hook Set
Format: [Static / Video-UGC / Both]
Persona: [name from STRATEGIC-BRIEF.md — or "as briefed"]
Grounding: [X hooks from STRATEGIC-BRIEF.md VOC/angles] + [Y original angles]
─────────────────────────────────────────────────────────

HOOK 01 — [THEME TYPE: e.g. TENSION / FEAR]
Source: [Grounded in VOC — "exact phrase" from glossary — OR Original angle]

[If Static requested:]
Static (3–6 words): "[headline]"

[If Video-UGC requested:]
Video/UGC (spoken, 1 sentence): "[hook]"

[If Both requested: show both]

─────────────────────────────────────────────────────────

HOOK 02 — [THEME TYPE]
Source: [Grounded / Original]
Static: "..."
Video/UGC: "..."

[repeat for all 5–6 hooks]

─────────────────────────────────────────────────────────
SWAP TEST: All [N] hooks passed.
[Or if rewritten: Hook 03 rewritten — original was too generic]
─────────────────────────────────────────────────────────
```

---

## Step 5 — Save to file

Save to: `[client-folder]/hooks/hooks-[YYYY-MM-DD].md`

Create the `/hooks/` directory if it doesn't exist.

```
# [Brand] — Hook Set
Date: [date]
Format: [Static / Video-UGC / Both]
Persona: [name]
Run: [N] hooks — [X grounded from VOC/brief] + [Y original angles]

---
[full hook output in Step 4 format]
---
Swap test: All hooks passed before output.
```

After saving, output the file path so the CS can find it:
"Saved: `[client-folder]/hooks/hooks-[date].md`"

---

## Quality rules (always apply)

- Never output a hook that passed the swap test on the first try without questioning whether it's specific enough
- Never use: "Are you looking for...", "Introducing...", "Have you ever...", "The [adjective] [product category] you need"
- Never open with the brand name — earn it
- Static hooks that are just the product name + adjective always fail ("Premium Plants. Beautiful Results.") — not a hook, a tagline
- If the trigger angle is already saturated (from STRATEGIC-BRIEF.md), flag it before writing hooks for it: "⚠️ [Angle] is listed as Saturated in STRATEGIC-BRIEF.md — competitors own this territory. Consider a Tier 1 or Tier 2 angle instead. Proceeding as requested."
