# Growth Strategy Creative Audit — End-to-End Workflow

This file is the complete instruction set for running a **Growth Strategy Creative Audit**.
When the user selects this analysis type, Claude should read this file and follow it step-by-step.

This audit is more sophisticated than the individual analysis modes. It combines multiple
analysis passes into a single comprehensive workflow and outputs a structured report
directly into the user's Notion Creative Audit Worksheet.

---

## Overview

The Growth Strategy Creative Audit runs the following pipeline:

1. **Portfolio Health Check** — Extract total active creatives, top performers, frequency/ROAS/CPM splits
2. **Performance-Creative Correlation** — Run correlation analysis on all ads
3. **Valence Gap Analysis** — Map the psychological diversity matrix
4. **Persona Gap Analysis** — Map persona coverage and spend allocation
5. **Creative Framework Audit** — Emotional ID, Story Framework, Awareness Level classification
6. **Opportunity Synthesis** — Combine all findings into categorised opportunities
7. **Report Output to Notion** — Insert the full report into the user's Creative Audit Worksheet

---

## Step-by-Step Execution

### Phase 0: Onboarding (Before Running Anything)

Gather the following from the user using AskUserQuestion:

#### 0.1 — Ad Account ID
Ask: "Which ad account should I audit? I just need the account ID (format: act_XXXXXXXXXXXX)."

#### 0.2 — Creative Audit Worksheet URL
Ask: "Please share the Notion link to the Creative Audit Worksheet where you'd like me to insert the report."

**This is MANDATORY.** The report must be inserted into the worksheet's callout block where it says `<CLAUDE TO INSERT REPORT HERE>`. If the user doesn't provide this, remind them that the Growth Strategy Audit outputs directly into their worksheet.

#### 0.3 — Defining "Top Performer"
Ask the Growth Strategist (the user): "How should we define a 'top performer' for this account? This will shape the entire audit."

Present options via AskUserQuestion:
- **Top 20% by ROAS** (Recommended) — Ads in the top quintile of return on ad spend
- **Top 20% by spend with positive ROAS** — Highest spend ads that are actually profitable
- **ROAS above account target** — Ads exceeding the client's ROAS target (ask for target)
- **Custom definition** — Let the user define their own threshold

Store this definition — it's used throughout the pipeline.

#### 0.4 — Number of Ads to Analyse
Ask: "How many ads should I pull for this audit? For a Growth Strategy Audit I'd recommend 50-80 — that gives enough volume for meaningful pattern analysis across all dimensions."

Present options: 50 (Recommended), 60, 80, Custom

#### 0.5 — Research Context (Optional)
Ask: "Do you have a Growth Strategy Dashboard or research document I can use for additional context? This enriches the analysis with your existing personas and strategy."

#### 0.6 — Confirm and Estimate Time
Summarise the configuration and give a time estimate before running. Example:

> "Here's what I'm about to do:
> - Pull top 60 ads by spend (last 30 days) from act_XXXXXXXXXXXX
> - Top performer defined as: Top 20% by ROAS
> - Run 4 analysis passes: Correlation, Valence, Persona, and Creative Framework audit
> - Synthesise opportunities and insert the report into your Creative Audit Worksheet
> - Estimated time: ~40-50 minutes (mostly Gemini analysis time)
>
> Shall I proceed?"

---

### Phase 1: Data Collection & Portfolio Health Check

#### 1.1 — Pull All Ads
Run the pipeline script with `--analysis-type growth-strategy` and `--date-preset last_30d`.

The script will:
1. Fetch all ads sorted by spend for the last 30 days
2. Compute batch averages (CPC, CPM, CTR, ROAS, Frequency)
3. Classify each ad as "Top Performer" or "Non-Top Performer" based on the user's definition
4. Compute split metrics:
   - Average Frequency: Top Performers vs Non-Top Performers
   - Average ROAS: Top Performers vs Non-Top Performers
   - Average CPM: Top Performers vs Non-Top Performers

#### 1.2 — Portfolio Health Metrics
The script will extract and compute:

| Metric | How |
|--------|-----|
| Total Active Creatives | Count of unique ads with spend > $0 in last 30 days |
| Total Top Performers | Count of ads meeting the top performer definition |
| Top Performer % | Top Performers / Total × 100 |
| Avg Frequency (Top Performers) | Mean frequency of top performer ads |
| Avg Frequency (Non-Top Performers) | Mean frequency of non-top performer ads |
| Frequency Delta | Difference — indicates creative fatigue signal |
| Avg ROAS (Top Performers) | Mean ROAS of top performers |
| Avg ROAS (Non-Top Performers) | Mean ROAS of non-top performers |
| Avg CPM (Top Performers) | Mean CPM of top performers |
| Avg CPM (Non-Top Performers) | Mean CPM of non-top performers |

**Creative Fatigue Signal**: If Frequency (Non-Top) > Frequency (Top) + 1.0, flag creative fatigue.

---

### Phase 2: Multi-Pass Gemini Analysis

The script runs FOUR analysis passes on each ad. Each pass uses a different prompt to extract
a specific dimension. This is more efficient than running 4 separate pipeline executions because
the media only needs to be downloaded and uploaded to Gemini once.

#### Pass 1: Performance-Creative Correlation
Uses the `correlation` prompt. Extracts:
- Format classification (UGC / Branded / Hybrid / Static)
- Hook analysis and thumbstop potential
- Engagement drivers
- RAG-scored metrics
- Performance verdict
- Ad lifecycle classification

#### Pass 2: Valence Classification
Uses the `valence` prompt. Extracts:
- Valence Zone (1-4)
- Self-Concept Anchor (Actual / Ideal / Ought)
- Language Intensity (Low / Mid / High)
- Matrix Position
- Trust Equity (Build / Spend / Neutral)

#### Pass 3: Persona Classification
Uses the `persona` prompt. Extracts:
- Macro Persona
- Micro Persona (Desire / Fear / Belief)
- Angle (8-angle taxonomy)
- Before State / New State

#### Pass 4: Creative Framework Audit (Selective)
Uses the `audit` prompt but extracts ONLY the most informative parts:
- Emotional ID (primary + secondary)
- Story Framework classification
- Awareness Level
- Angle classification
- Hook analysis (first 3 seconds)
- Key messaging / value proposition

**Important**: This is NOT a full end-to-end audit. We only extract the framework
classifications and messaging analysis — not the full 14-point audit. This keeps
the analysis focused and avoids redundancy with the other passes.

---

### Phase 3: Synthesis

After all individual ad analyses are complete, run THREE synthesis passes:

#### 3.1 — Valence Synthesis
Uses `build_valence_synthesis_prompt()` to produce:
- Psychological Matrix Heatmap (4 zones × 3 self-concepts)
- Diversity Score (X/12 cells covered)
- Zone distributions
- Trust Equity balance
- Unmapped opportunity zones

#### 3.2 — Persona Synthesis
Uses `build_persona_synthesis_prompt()` to produce:
- Persona spend allocation table
- Awareness level distribution
- Story framework distribution
- Angle coverage matrix
- Creative gap analysis
- Cross-persona patterns

#### 3.3 — Opportunity Synthesis (NEW — unique to Growth Strategy Audit)
This is the key strategic output. After gathering all individual analyses and both
synthesis reports, run a final Gemini pass that:

1. **Combines all findings** from correlation, valence, persona, and framework analyses
2. **Categorises opportunities** by what they relate to:
   - Valence Gap — Unmapped psychological zones
   - Persona Gap — Under-served or missing personas
   - Creative Diversity — Format/style/production gaps
   - Framework Gap — Untested story frameworks or awareness levels
   - Messaging Gap — Missing angles, value propositions, or hook styles
   - Fatigue Signal — High frequency with declining performance
   - Performance Correlation — Creative elements linked to strong/weak metrics
3. **Ranks opportunities** using ICE scoring (Impact × Confidence × Ease)
4. **Frames each opportunity for Reddit deep-dive** — describes what to research on Reddit
   to better understand the messaging style and framework for each opportunity

The opportunity list is the CORE DELIVERABLE. It sets the user up for the next step
in the Growth Strategy workflow: filtering opportunities and using Reddit research
to dig deeper into the best ones.

---

### Phase 4: Report Output to Notion

#### 4.1 — Create the Report Page
Create a NEW Notion page as a child of the Creative Audit Worksheet.
Title: "AI Creative Audit Report — [Date]"

The report page should contain the following sections in this order:

```
# AI Creative Audit Report

## Executive Summary
[2-3 paragraph overview of key findings]

## Portfolio Health Check
[Table with all Phase 1 metrics]
[Creative fatigue signals]
[Top performer analysis]

## Performance-Creative Correlation
[Key correlations found]
[Format/hook/engagement patterns]
[RAG-scored performance summary]

## Psychological Diversity (Valence Analysis)
[Matrix heatmap]
[Diversity score]
[Zone distributions]
[Trust Equity balance]

## Persona & Spend Analysis
[Persona spend allocation table]
[Awareness level distribution]
[Creative gap analysis]

## Creative Framework Analysis
[Emotional ID distribution]
[Story Framework distribution]
[Awareness Level coverage]
[Angle taxonomy coverage]

## Strategic Opportunities
[CATEGORISED opportunity list — this is the main deliverable]
[Each opportunity with:]
  - Category (Valence / Persona / Diversity / Framework / Messaging / Fatigue / Correlation)
  - Description
  - Evidence (which data points support this)
  - ICE Score (Impact / Confidence / Ease / Total)
  - Reddit Research Prompt (what to search for to dig deeper)

## Next Steps
[Instruction to user: Filter the opportunities above, then use Reddit audience research
 to explore the messaging styles and frameworks for your selected opportunities]
```

#### 4.2 — Insert into Worksheet
After creating the report page, update the Creative Audit Worksheet.
Find the callout block containing `<CLAUDE TO INSERT REPORT HERE>` and replace it
with a link/embed to the report page you just created.

Use the Notion update-page tool with `replace_content_range`:
- selection_with_ellipsis: Target the callout block containing the placeholder
- new_str: Replace with the report page embed/link

---

## Script Integration

### New CLI Flag
The `analyse_creatives.py` script supports a new analysis type: `growth-strategy`

```bash
python3 analyse_creatives.py \
  --limit 60 \
  --date-preset last_30d \
  --analysis-type growth-strategy \
  --top-performer-method roas_top_20 \
  --metrics-enriched \
  --output ./creative_analysis
```

### New Arguments
- `--top-performer-method`: How to define top performers
  - `roas_top_20` (default) — Top 20% by ROAS
  - `spend_positive_roas` — Top 20% by spend with ROAS > 1.0
  - `roas_above_target` — Requires `--roas-target`
  - `custom` — Requires `--custom-top-performer-filter`
- `--roas-target`: Float. Used with `roas_above_target` method.

### Script Behaviour for growth-strategy Mode
When `--analysis-type growth-strategy` is set, the script:

1. Fetches ads and computes batch averages (same as other modes)
2. Classifies Top Performers based on `--top-performer-method`
3. Computes split metrics (frequency, ROAS, CPM for top vs non-top)
4. Runs **multi-pass analysis** on each ad:
   - Pass 1: Correlation prompt → stored in `result["correlation_analysis"]`
   - Pass 2: Valence prompt → stored in `result["valence_analysis"]`
   - Pass 3: Persona prompt → stored in `result["persona_analysis"]`
   - Pass 4: Framework audit prompt → stored in `result["framework_analysis"]`
5. Runs synthesis passes:
   - Valence synthesis → `valence_synthesis`
   - Persona synthesis → `persona_synthesis`
   - Opportunity synthesis → `opportunity_synthesis` (NEW)
6. Generates the full report markdown + JSON

### Time Estimate
Growth Strategy Audit takes ~4x longer per ad than a single-pass analysis because
it runs 4 Gemini calls per ad. Estimate:
- Image ads: ~80s each (4 × 20s)
- Video ads: ~60s each (media uploaded once, 4 × ~15s Gemini calls)
- 60 ads mixed: ~60-70 minutes total
- Plus 3 synthesis passes: ~5-10 minutes

**Always warn the user** about the time commitment upfront.

---

## Prompt Templates

### Opportunity Synthesis Prompt

This is the NEW prompt used after all individual analyses and synthesis passes are complete.
It's the strategic capstone that produces the categorised opportunity list.

See `prompts.md` section "Growth Strategy Opportunity Synthesis" for the full prompt template.

### Framework Audit Prompt (Selective)

This is a slimmed-down version of the full end-to-end audit prompt. It only extracts:
- Emotional ID (primary + secondary)
- Story Framework + how it's used
- Awareness Level + evidence
- Angle classification
- Hook analysis (first 3 seconds only)
- Key message / value proposition
- Stand-out messaging

See `prompts.md` section "Framework Audit (Selective)" for the full prompt template.
