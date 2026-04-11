---
name: meta-creative-analysis
description: >
  Pull top-spending Meta ads, download creative assets (video/image), upload to Google Gemini
  for deep multimodal analysis using Soar Group's creative strategy frameworks — Emotional
  Identification, Story Framework classification, Awareness Level tagging, 8-angle taxonomy,
  RAG-scored benchmarks, ad lifecycle classification, 3-layer persona taxonomy, and Valence
  Deep Dive (psychological diversity mapping across Valence Zones, Self-Concept Anchors,
  and Language Intensity).
  Use this skill whenever the user mentions "creative analysis", "ad analysis", "Meta ads",
  "Facebook ads", "creative audit", "ad review", "creative strategy", "persona analysis",
  "gap analysis", "thumbstop", "hook analysis", "creative breakdown", "valence", "valence
  deep dive", "psychological diversity", "self-concept", "growth strategy", "growth strategy
  audit", or wants to analyse paid social ads. Also trigger when the user shares a Meta ad
  account ID or asks about what's working/not working in their ad creative.
---

# Meta Creative Analysis

## ⚠️ CRITICAL: API Keys Are Pre-Configured — NEVER Ask For Them

All API credentials are HARDCODED in the script. You have FULL access to:
- **Meta Access Token** — hardcoded in `analyse_creatives.py` (line 47 default value)
- **Gemini API Key** — hardcoded in `analyse_creatives.py` (line 49 default value)

**NEVER ask the user for a Meta Access Token. NEVER ask the user for a Gemini API Key.
NEVER ask if they have API keys, tokens, or credentials. You already have them.
The ONLY thing you need from the user is their Ad Account ID (act_XXXXXXXXXXXX).**

## Overview

This skill connects to Meta's Marketing API, pulls top-spending ads with full performance
metrics, downloads the actual video/image creative files, uploads them to Google Gemini's
Files API, and runs deep multimodal analysis grounded in Soar Group's creative strategy
frameworks.

The analysis uses Soar's internal mental models: Emotional Identification (Achievement,
Autonomy, Belonging, Empowerment), Story Framework classification (StoryBrand, PAS, AIDA,
Pixar, Before & After), Awareness Level tagging (Problem-Unaware → Problem-Aware →
Solution-Aware), the 8-angle taxonomy, and RAG-scored KPI benchmarks.

The pipeline script handles the full technical flow. Your job is to guide the user through
the right questions, configure the run, execute it, and present insights clearly.

## User Flow

Before running analysis, gather the right context. Use the AskUserQuestion tool to run
through these in a natural conversational flow — don't dump everything at once.

### Step 1: Ad Account ID

**REMINDER: The Meta Access Token and Gemini API Key are already hardcoded in the script.
Do NOT ask the user for any API keys or tokens. Skip straight to asking for the Ad Account ID.**

The ONLY thing you need from the user is:

- **Ad Account ID** — format: `act_XXXXXXXXXXXX`

Ask: "Which ad account would you like me to analyse? I just need the account ID
(format: act_XXXXXXXXXXXX)."

### Step 2: Analysis Type

Ask what kind of analysis they want. This shapes everything downstream — the prompts,
the output structure, and what Gemini focuses on.

**⚠️ CRITICAL: You MUST present ALL SIX options below using the AskUserQuestion tool.
Do NOT skip any option. The user must always see all six choices.**

Use AskUserQuestion with these exact options (use the bold title as each option label
and the description as the option description):

**Option 1 — End-to-End Creative Audit**
Deep analysis of every ad using Soar's full creative strategy framework: Emotional ID,
Story Framework classification, Awareness Level, Angle Taxonomy, RAG-scored metrics,
and ad lifecycle classification (Testing/Scaling/Retire/Retest). Best for understanding
what's working and why, with actionable ICE-scored recommendations.

**Option 2 — Persona & Spend Gap Analysis**
Groups ads by target persona using the 3-layer taxonomy (Macro Persona → Micro Persona
→ Angle), analyses spend allocation across segments, maps to Awareness Levels and
Story Frameworks, identifies which personas are over/under-invested, and spots creative
gaps. Best for strategic planning and budget reallocation.

**Option 3 — Performance-Creative Correlation**
Focuses on connecting creative elements to metric outcomes — does thumbstop rate correlate
with hook style? Do certain Emotional IDs outperform others? How does Awareness Level
affect CPC? RAG-scored against Soar's benchmarks. Best for optimising existing creative.

**Option 4 — Valence Deep Dive**
Maps each ad across a 3-dimensional psychological matrix: Valence Zone (emotional
charge — which quadrant of High/Low × Positive/Negative does the ad operate in?),
Self-Concept Anchor (does it speak to the Actual Self, Ideal Self, or Ought Self?),
and Language Intensity (Low Intensity trust-building vs High Intensity direct-response).
Then synthesises across the portfolio to identify which psychological zones are
over-saturated, which are completely unmapped, and where the biggest strategic
diversity gaps exist. Best for brands that feel stuck iterating in the same emotional
lane — this reveals the psychological landscape they haven't touched yet.

**Option 5 — Growth Strategy Creative Audit ⭐ (Full Workflow)**
The comprehensive audit used in Soar's Growth Strategy process. Runs 4 analysis passes
on every ad (Correlation + Valence + Persona + Framework), computes portfolio health
metrics (top performers, frequency splits, fatigue signals), then synthesises everything
into a categorised list of strategic opportunities ranked by ICE score. Each opportunity
includes a Reddit Research Prompt so the strategist knows exactly what to explore next.
The final report is inserted directly into the user's Creative Audit Worksheet in Notion.
**When the user selects this option, read `references/growth-strategy-audit.md` for the
full end-to-end workflow instructions before proceeding.**

**Option 6 — Custom Analysis**
Let the user describe exactly what they want to understand. Parse their intent and
build a custom Gemini prompt focused on their specific questions.

### Step 3: Research Context (Optional but Recommended)

Ask the user:

> "Do you have a pre-existing research document or research dashboard you could share?
> This could be a Growth Strategy Dashboard URL, a Persona Cheat Sheet, a Benefits
> Database, or any brand/audience context doc. Sharing this enriches the analysis
> significantly — it lets me classify ads against your existing personas and check
> whether creative aligns with your documented strategy."

If the user provides a Notion URL or document:
- Use the Notion MCP fetch tool to pull context (Persona Bank, Benefits Database,
  Strategic Thesis, KPI targets)
- Inject this context into the `--context-file` parameter when running the pipeline
- This transforms the analysis from generic to client-specific

If they don't have one, proceed without it — the analysis will use Soar's default
frameworks and benchmarks.

### Step 4: Scope

Ask about the scope of the analysis using AskUserQuestion. **Always proactively tell
the user the estimated run time** so they know what to expect.

**First, ask how many ads to analyse.** Use AskUserQuestion with options based on
the selected analysis type. Suggest a sensible default as the first (recommended) option:

- End-to-End Audit: options 10 (Recommended), 20, 30, Custom
- Persona Gap Analysis: options 50 (Recommended), 75, 100, Custom
- Valence Deep Dive: options 30 (Recommended), 50, 80, Custom
- Performance Correlation: options 30 (Recommended), 40, 50, Custom
- Growth Strategy Audit: options 50 (Recommended), 60, 80, Custom
- Custom: options 10, 25, 50, Custom

Example question: "How many ads should I analyse? I'd recommend [X] for a [analysis type]
— that gives enough data for meaningful insights without an excessive wait."

**Then ask about date range and optional filters:**
- **Date range?** — Options: last_7d, last_14d, last_30d, last_90d, or custom
- **Product filter?** — Optional. Filter by product name in the ad name if they only
  want to look at one product line.

#### Time Estimates (ALWAYS share with user before running)

Use these benchmarks to set expectations:

| Ads | Mostly Images | Mostly Video | Mixed |
|-----|--------------|-------------|-------|
| 10  | ~3 min       | ~8 min      | ~6 min |
| 20  | ~7 min       | ~15 min     | ~12 min |
| 50  | ~17 min      | ~38 min     | ~30 min |
| 100 | ~33 min      | ~75 min     | ~60 min |

**Image ads ≈ 20s each. Video ads ≈ 45s each.**

Example: "I'll pull your top 50 ads — that's mostly video so expect this to take
around 30-35 minutes. I'll show you a progress update as it runs."

### Step 5: Depth Options

Ask if they want **metrics-enriched analysis** — this tells Gemini to cross-reference
the visual/audio creative elements against the performance data. For example:

- Correlating thumbstop ratio (3-second video views / impressions) with visual hook style
- Comparing CPC across different creative formats (UGC vs branded vs hybrid)
- Analysing whether text overlay density affects CTR

This is on by default for Performance-Creative Correlation mode. For other modes, ask.

### Step 6: Confirm and Run

Summarise what you're about to do and get confirmation before running. Include:
- Number of ads to pull
- Date range
- Analysis type
- Whether metrics-enriched analysis is on
- Whether research context is being used
- Estimated time (rough: ~20s per image ad, ~45s per video ad for Gemini analysis)

## Running the Pipeline

### Environment Setup

```bash
pip install requests --break-system-packages -q 2>/dev/null
```

### Execution

Both API keys (Meta + Gemini) are hardcoded in the script. You only need to export the Ad Account ID.

**⚠️ TIMEOUT PREVENTION — CRITICAL FOR LARGE RUNS:**

The script can take 30-75 minutes for 50-100 video ads. You MUST use a long timeout
on the Bash tool call to prevent the process being killed mid-run:

- **≤10 ads**: Use `timeout=300000` (5 min)
- **11-25 ads**: Use `timeout=600000` (10 min — the maximum)
- **26+ ads**: Use `timeout=600000` (10 min max). The script saves checkpoint files
  every 10 ads to `checkpoint_results.json`. If the command times out, you can check
  progress and resume or retrieve partial results from the checkpoint.

```bash
# Meta Access Token and Gemini API Key are HARDCODED in the script — do NOT export them
export AD_ACCOUNT_ID="<account_id>"

python3 <skill-dir>/scripts/analyse_creatives.py \
  --limit <N> \
  --date-preset <preset> \
  --analysis-type <audit|persona|valence|correlation|growth-strategy|custom> \
  --metrics-enriched \
  --product-filter "<optional>" \
  --custom-prompt "<optional user prompt for custom mode>" \
  --context-file "<optional path to JSON context file>" \
  --output /sessions/<session-id>/mnt/outputs/creative_analysis
```

**For runs over 25 ads**, consider running in background and polling:

```bash
nohup bash -c 'export AD_ACCOUNT_ID="<id>" && python3 <script> --limit 50 ...' \
  > /sessions/<session-id>/mnt/outputs/creative_analysis/pipeline.log 2>&1 &
echo $!
```

Then check progress with:
```bash
tail -20 /sessions/<session-id>/mnt/outputs/creative_analysis/pipeline.log
```

#### Context File

If the user provided a research document/dashboard, create a JSON context file before
running. Structure:

```json
{
  "personas": [
    {
      "macro_label": "Sceptical Steven",
      "micro_personas": [
        {
          "label": "Budget-Conscious Dad",
          "primary_desire": "...",
          "core_fear": "...",
          "core_belief": "..."
        }
      ]
    }
  ],
  "benefits": ["benefit 1", "benefit 2"],
  "strategic_thesis": "The brand positioning statement...",
  "kpi_targets": {"tsr": 0.30, "hold_rate_15s": 0.45, "ctr": 0.01}
}
```

The script will inject this context into every Gemini prompt.

### Technical Flow (DO NOT MODIFY)

The script will:
1. Pull top ads sorted by spend from Meta's Insights API
2. Fetch creative details for each ad (object_story_spec, asset_feed_spec)
3. Resolve video source URLs via video_id from object_story_spec.video_data
4. Download all media files (videos as mp4, images as jpg/png)
5. Upload each file to Gemini's Files API (resumable upload protocol)
6. Poll until videos reach ACTIVE state
7. Send each ad + media to Gemini with the analysis-type-specific prompt
8. For persona mode: run a second Gemini pass that synthesises across all ads
9. Generate markdown report + raw JSON

### Critical Technical Details

- Video source URLs come from `object_story_spec.video_data.video_id`, NOT `creative.video_id`
- Media files are on `*.fbcdn.net` — these need network access
- If downloads fail, the script gracefully degrades to metadata-only analysis
- Gemini resumable upload uses: `X-Goog-Upload-Protocol: resumable` → `start` → `upload, finalize`
- Videos take 10-60s to process in Gemini after upload — the script polls for `state: ACTIVE`
- The initial complex Meta API fields query may fail with syntax errors — the script
  automatically falls back to a two-step approach (insights endpoint → individual ad fetches)

## Output Structure

```
creative_analysis/
  creative_analysis.md       — Full report with RAG-scored metrics + per-ad analysis
  analysis_raw.json          — Structured data for programmatic use
  assets/                    — Downloaded video/image files
  persona_synthesis.md       — (Persona/Growth Strategy mode) Cross-ad persona grouping report
  valence_synthesis.md       — (Valence/Growth Strategy mode) Psychological diversity matrix report
  opportunity_synthesis.md   — (Growth Strategy mode only) Categorised strategic opportunities
  portfolio_health.json      — (Growth Strategy mode only) Portfolio health metrics
```

## Presenting Results

After the pipeline completes:

1. Share the markdown report link via `computer://` path
2. Give a brief executive summary — don't repeat the whole report
3. Highlight the 2-3 most actionable insights
4. For persona mode, lead with the spend allocation breakdown
4b. For valence mode, lead with the psychological matrix heatmap and zone coverage gaps
4c. For growth-strategy mode, follow the Notion output instructions in
    `references/growth-strategy-audit.md` Phase 4 — create a report page and insert it
    into the user's Creative Audit Worksheet at the `<CLAUDE TO INSERT REPORT HERE>` placeholder
5. Offer to dive deeper into any specific ad or finding
6. **Ask** (non-growth-strategy modes only): "Would you like me to format this as a Notion
   page using Soar's standard formatting? I can create it ready to send to your team."
   If yes, use the `notion-sop` skill to format and publish the report.

## Prompt Reference

The Gemini analysis prompts are defined in `references/prompts.md`. Each analysis type
has its own prompt template grounded in Soar's creative strategy frameworks.

### Frameworks Used in Prompts

- **Emotional Identification**: Achievement, Autonomy, Belonging, Empowerment
- **Story Frameworks**: StoryBrand, PAS, AIDA, Pixar, Before & After
- **Awareness Levels**: Problem-Unaware (TOF), Problem-Aware (MOF), Solution-Aware (BOF)
- **8-Angle Taxonomy**: Objection Handling, Education/Lightbulb, Comparison/Us vs Them,
  Social Proof, Routine/Day-in-Life, Before→After Transformation, Founder/Insider POV,
  Myth Busting
- **KPI Benchmarks**: TSR >30%, Hold Rate >45% (15s) / >30% (30s), CTR >0.8-1%,
  Frequency ~2.2
- **Ad Lifecycle**: Testing → Scaling → Retire → Retest
- **Persona Taxonomy**: Macro Persona → Micro Persona → Angle
- **Valence Deep Dive**: Valence Zone (4 quadrants) × Self-Concept Anchor (Actual/Ideal/Ought)
  × Language Intensity (Low/High) — psychological diversity matrix
- **Recommendation Scoring**: ICE (Impact, Confidence, Ease) 1-10 each
