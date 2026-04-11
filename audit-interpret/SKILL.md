---
name: audit-interpret
description: >
  Reads a completed Creative Audit from Notion (10-phase CS audit with performance data,
  winner tagging, messaging territories, persona maps, format analysis, funnel mapping, and
  Creative Health + Diversity scores). Interprets across all phases to produce ACCOUNT-AUDIT.md
  with cross-phase findings, validated strengths, risk signals, strategic opportunities, and a
  repeatable creative formula. Also writes the interpretation back to the same Notion page.
  Trigger on: "/audit-interpret [Notion URL]", "interpret the audit", "read the audit",
  "produce the account audit", or when a CS says the audit is ready for Claude.
---

# Audit Interpret

This skill is the interpretation layer between the CS's manual creative audit and the rest of
the pipeline. It does not audit anything — the CS already did that. It reads their structured
data, diagnostics, and scores, then synthesises across all 10 phases to surface patterns the
CS can act on.

**What this skill produces:**
- `ACCOUNT-AUDIT.md` in the client folder — the interpreted audit, used by strategic-brief-builder and script-builder
- A new "Claude Interpretation" section appended to the same Notion audit page

**What this skill does NOT do:**
- Pull data from Meta Ads Manager or any ad platform (the CS already did this)
- Re-score Creative Health or Creative Diversity (the CS scored it — Claude flags disagreements)
- Invent findings not supported by the audit data
- Paraphrase the CS's diagnostic answers — quote them, then interpret

---

## Step 0 — Fetch the Notion audit page

The CS provides the Notion page URL as the argument to this skill.

Fetch the page using `notion-fetch` with the provided URL.

**The CS triggering this skill is the declaration that the audit is ready.** No status badge
check needed. However, run these quality gates before proceeding:

1. **Phase completeness check:** Scan for empty tables and blank diagnostic answers.
   If more than 2 diagnostic questions are blank — STOP. Output:
   ```
   AUDIT INCOMPLETE — [X] diagnostic questions are blank.

   Claude's interpretation quality depends directly on your written diagnostics.
   These are not optional fields — they contain the analytical judgment that
   separates a useful ACCOUNT-AUDIT.md from a generic summary.

   Missing diagnostics:
   - Phase [X]: [diagnostic question]
   - Phase [X]: [diagnostic question]

   Complete these before marking as READY FOR CLAUDE.
   ```

3. **Creative Health Score check:** If the scoring table has empty cells — STOP with
   the same pattern, naming which factors are unscored.

If all checks pass, proceed.

---

## Step 1 — Extract and hold in context

Read the full page content. Extract and hold the following — these are your raw materials:

**From Account Overview:**
- Client name, monthly spend, avg ROAS/CPA, number of active ads, audit period

**From Phase 0 (Brand Brief):**
- The CS's brand brief paragraph — this is their mental model of the business. Hold it.

**From Phase 1 (Commercial Center of Gravity):**
- Product concentration table — which products hold what % of spend
- Top landing pages with ROAS, CPA, AOV
- Diagnostic answer: broad brand strength vs one product carrying the account

**From Phase 2 (Spend Concentration):**
- Total active ads vs ads above meaningful spend threshold
- Top 3 / top 5 / top 10 spend concentration percentages
- Whether any single ad holds >20% of spend
- New ads launched in last 30 days, new winners graduating per month
- Diagnostic answer: volume problem vs quality problem

**From Phase 3 (Winner Audit) — the winning messaging themes table:**
- Theme names, core arguments, which ads belong, combined spend, avg ROAS
- Do NOT try to re-extract individual ad data from the database. The CS has already
  synthesised the per-ad tagging into the Winning Messaging Themes table and into
  Phases 4-10. Use those summaries.
- Diagnostic answer: which themes are carrying the account and why

**From Phase 4 (Real Variation vs Surface Variation):**
- Messaging Territory Map — territory names, core arguments, spend, % of total, ROAS, genuinely distinct Y/N
- Diagnostic answer: how many genuinely different reasons to buy

**From Phase 5 (Dominant Territory + What's Missing):**
- Dominant territory statement
- Territory Coverage Checklist — status and potential for each territory type
- Diagnostic answer: beliefs and motivations never spoken to

**From Phase 6 (Persona Analysis):**
- Persona Motivation Map — persona names, pain/desire, key objection, belief shift, has motivation-specific creative Y/N/Partial, spend, identity angle
- Diagnostic answer: changing message by persona vs just styling

**From Phase 7 (Landing Page Analysis):**
- LP deep dive table — URLs, spend, ROAS, CPA, AOV, ad-to-page coherence, issue layer
- Diagnostic answer: where experience breaks down

**From Phase 8 (Format Analysis):**
- Format Function Map — format, # ads, spend, % of total, avg ROAS, current function, untapped function
- Diagnostic answer: matching format to job vs defaulting

**From Phase 9 (Video Structure Breakdown):**
- Winning video structures table
- Weak video structures table
- Repeatable Video Formula (CS's written formula)
- Diagnostic answer: structural difference between winners and losers

**From Phase 10 (Funnel Stage Analysis):**
- Funnel Stage Map — stage, # ads, spend, %, avg ROAS
- Funnel Mismatch Checks — all 5 findings
- Diagnostic answer: building demand vs harvesting it

**From Creative Health Scoring:**
- All 5 factor scores with evidence
- Total Creative Health Score (/25)

**From Creative Diversity Score:**
- All 7 dimension counts and percentages
- Overall Creative Diversity Score

**From QC Checklist:**
- Read the checklist status — if any items are unticked, note which ones. These represent
  gaps the CS acknowledged but may not have addressed. Surface them in the interpretation.

---

## Step 2 — Cross-phase analysis (the interpretation)

This is where Claude adds value beyond what the CS already wrote. Do NOT restate each phase.
Instead, find the patterns that only emerge when you read all 10 phases together.

**Run these analytical passes:**

### Pass 1: Concentration × Diversity risk matrix
Cross-reference:
- Spend concentration (Phase 2) × messaging territory count (Phase 4) × funnel distribution (Phase 10)
- If spend is concentrated AND territories are few AND funnel skews BOF → compound fragility. Name it.
- If spend is concentrated BUT territories are diverse → the account has ideas but can't graduate winners. Different problem.
- If spend is spread BUT territories are few → volume masks lack of real variation. Surface-level diversity.

### Pass 2: Persona × Territory alignment
Cross-reference:
- Personas identified (Phase 6) × messaging territories (Phase 4) × identity angles used
- Which personas have spend but NO motivation-specific messaging territory?
- Which territories are persona-agnostic (speaking to everyone = speaking to no one)?
- Which identity angles (Actual/Ideal/Ought Self) are missing entirely?

### Pass 3: Format × Function × Funnel coherence
Cross-reference:
- Format distribution (Phase 8) × funnel stage distribution (Phase 10) × video structure (Phase 9)
- Are formats matched to funnel stages? (e.g., UGC for awareness, demonstration for consideration, offer statics for BOF)
- Or is every format doing the same job regardless of funnel position?
- Does the repeatable video formula align with what's actually winning in the data?

### Pass 4: Landing page × Creative coherence
Cross-reference:
- Top LPs (Phase 7) × winning messaging themes (Phase 3) × product concentration (Phase 1)
- Are the highest-spend LPs receiving traffic from coherent creative? Or is spend flowing to pages that don't match the ad's promise?
- Where is AOV strongest? Does creative strategy account for this?

### Pass 5: Score validation
Compare the CS's Creative Health scores against what the data actually shows:
- If CS scored Persona Coverage 4/5 but Phase 6 shows only 2 personas with motivation-specific creative → flag the discrepancy
- If CS scored Messaging Diversity 3/5 but Phase 4 shows only 1 genuinely distinct territory → flag
- Do NOT override the CS's scores. Flag disagreements with evidence. The CS decides.

---

## Step 3 — Build ACCOUNT-AUDIT.md

Write the file with this exact structure:

```markdown
# [CLIENT NAME] — Account Audit Interpretation
Generated: [YYYY-MM-DD]
Auditor: [CS name from Account Overview]
Source: Creative Audit Notion page — [URL]
Audit period: [from Account Overview]

---

## Account Snapshot

| Metric | Value |
|---|---|
| Monthly ad spend | [value] |
| Avg ROAS / CPA | [value] |
| Active ads | [value] |
| Ads above meaningful spend | [value] |
| Creative Health Score | [X]/25 |
| Creative Diversity Score | [X]% |
| Dominant territory | [one sentence from Phase 5] |
| Hero product (by spend) | [from Phase 1] |

---

## Cross-Phase Findings

[From Step 2 — the patterns that emerge when reading all phases together.
Write 3-6 findings. Each finding must:
- Name the pattern
- Cite which phases it draws from
- State what it means for creative strategy
- Be specific to THIS account — not generic advice]

### Finding 1: [Pattern name]
**Phases:** [X, Y, Z]
**What the data shows:** [specific numbers and diagnostics]
**What this means:** [strategic implication]

### Finding 2: [Pattern name]
...

---

## Validated Strengths

[What is genuinely working and WHY. Not a list of top ads — a list of
strategic assets this account has that the next phase of creative should
protect and build on.]

- **[Strength]:** [evidence from audit] — **Protect by:** [specific action]

---

## Risk Signals

[Ordered by severity. Each must be tied to specific audit data.]

### [Risk name] — Severity: HIGH / MEDIUM / LOW
**Evidence:** [from which phases, what numbers]
**If unaddressed:** [what happens to the account]
**Mitigation:** [specific creative action]

---

## Score Discrepancies

[From Pass 5. If CS scores and data diverge, flag here with evidence.
If no discrepancies: "No discrepancies found between CS scores and audit data."]

| Factor | CS Score | Data Suggests | Evidence | Resolution |
|---|---|---|---|---|
| [factor] | [X]/5 | [Y]/5 | [why] | CS to confirm |

---

## Strategic Opportunities

[Ranked by expected impact. Each tied to a specific finding or gap.
These are NOT generic "test more formats" suggestions. Each one must be:
- Rooted in a specific audit finding
- Narrow enough to brief from
- Realistic given current account resources]

### Opportunity 1: [Name]
**Based on:** [which finding/gap]
**The gap:** [what's missing, with numbers]
**The move:** [specific creative action]
**Expected impact:** [what this unlocks — persona, territory, funnel stage]
**Priority:** HIGH / MEDIUM / LOW

### Opportunity 2: [Name]
...

[Minimum 5 opportunities. Maximum 10. If fewer than 5 genuine opportunities
exist, the audit data is likely incomplete — flag this.]

---

## Repeatable Creative Formula

[Derived from Phase 9 video structure + Phase 3 winning themes + Phase 8
format analysis. This section feeds directly into the script builder.]

### Winning video structure for this account:
[CS's repeatable formula from Phase 9 — quoted, not paraphrased]

### Winning hooks pattern:
[What the top-performing hooks have in common — hook type, speed to product,
opening technique. Derived from Phase 3 winner tagging.]

### Format-to-job map:
| Job | Best format | Evidence |
|---|---|---|
| [awareness / consideration / conversion / specific task] | [format] | [ROAS or diagnostic evidence] |

---

## CS Review Required

[Specific items where Claude's interpretation needs human confirmation
before these findings feed into the Strategic Brief.]

- [ ] Cross-phase findings — do these match your experience with this account?
- [ ] Score discrepancies — confirm or override
- [ ] Strategic opportunities — add, remove, or reprioritise
- [ ] Repeatable formula — does this match what you've seen perform?
```

Save to: `[client-folder]/ACCOUNT-AUDIT.md`

Log the file path. If this file cannot be saved, the run is incomplete.

---

## Step 4 — Write interpretation back to Notion

Using `notion-update-page`, append a new section to the SAME Notion audit page (the URL
provided in Step 0). The section should be added AFTER the existing "Audit Status" section.

**Content to append:**

A heading: "Claude Interpretation — [Date]"

Then include the following from ACCOUNT-AUDIT.md:
- Account Snapshot table
- Cross-Phase Findings (all findings)
- Validated Strengths
- Risk Signals
- Strategic Opportunities (all, with rankings)
- Score Discrepancies (if any)
- CS Review Required checklist

Do NOT include the Repeatable Creative Formula section in Notion — that's for the local
ACCOUNT-AUDIT.md only (it's a script-builder input, not a CS review item).

Add a final callout:

> **CS Action Required:** Review the findings and opportunities above. Check or uncheck
> items in the CS Review Required section. Add your own strategic opportunities below
> this section. When reviewed, the local ACCOUNT-AUDIT.md in the client folder will be
> the confirmed version used by the Strategic Brief Builder and Script Builder.
> **Next step:** Once confirmed, run `/strategic-brief-builder` when all 5 handover docs are ready.

---

## Step 5 — Confirm completion

Output to the user:

```
ACCOUNT-AUDIT.md saved to [client-folder]/ACCOUNT-AUDIT.md
Interpretation appended to Notion page: [URL]

Summary:
- Cross-phase findings: [count]
- Validated strengths: [count]
- Risk signals: [count] ([count] HIGH / [count] MEDIUM / [count] LOW)
- Strategic opportunities: [count]
- Score discrepancies: [count]

CS review required before this feeds into the Strategic Brief.
Items flagged for your review are in the "CS Review Required" section
both locally and on the Notion page.
```

---

## Quality checklist — BLOCKING

Before declaring the run complete:

- [ ] Completeness checks passed (diagnostics, scores, tables not blank)
- [ ] All diagnostic answers were read and referenced (not ignored)
- [ ] Cross-phase findings cite specific phases and specific numbers — no vague claims
- [ ] Every strategic opportunity ties to a specific audit finding — no generic advice
- [ ] No findings were invented beyond what the audit data supports
- [ ] CS diagnostic answers are quoted where referenced, not paraphrased
- [ ] Score discrepancies are flagged with evidence, not silently resolved
- [ ] ACCOUNT-AUDIT.md saved to client folder — path logged
- [ ] Notion page updated with interpretation section — confirmed
- [ ] Repeatable formula section uses CS's own formula from Phase 9, quoted verbatim
- [ ] "CS Review Required" section is present in both local file and Notion
- [ ] Minimum 5 strategic opportunities, each narrow enough to brief from
