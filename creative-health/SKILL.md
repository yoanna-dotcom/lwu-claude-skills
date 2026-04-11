---
name: creative-health
description: >
  Run a Creative Health audit on a Meta ad account. Pulls all active ads via Marketing API,
  parses the LWU naming convention into structured dimensions (funnel, angle, media type, product,
  pain point, identity), normalises variants, calculates per-dimension diversity scores (HHI),
  classifies ads as winner/mid/loser, analyses video performance (thumbstop rate, hold rate),
  detects dead-weight spend, cross-tabs dimensions, and produces a composite Creative Health Score
  (0-100) with an interactive HTML report. Use this skill when someone asks to audit creative
  health, check creative diversity, analyse ad naming compliance, review creative performance
  distribution, or wants to understand what's working and what's missing in an ad account's
  creative portfolio. Also trigger when someone mentions "creative health", "creative diversity",
  "creative audit data", "ad performance breakdown", or provides a Meta ad account ID and wants
  creative-level analysis.
---

# Creative Health Skill

## What This Skill Does

Automates the data layer of creative health analysis by pulling ad-level performance data from
the Meta Marketing API, parsing the LWU naming convention into structured dimensions, and
scoring the portfolio across diversity, performance efficiency, video health, and naming compliance.

**Output:** Interactive HTML report + enriched CSV + JSON summary.

**Runtime:** 3-5 minutes. Token-light — Python does the heavy lifting, Claude orchestrates.

## How to Run

### Step 0 — Gather Input

The Meta API token is pre-configured:
META_ACCESS_TOKEN: EAAUeobHyYdsBQZCVPLlEq42kOIGHojQbz8Ag2a007TJb7vQe8TRBfWuZAFcOZBFxd3k0Eqoh6wZBrRW85ZAUsZBxV5gz2cfYQb9wYk3SViWtjk13SGPa9ZAvh1gZB2ZAnjlKg9lq3doCNTHwdFZCDSBMExNAc3LguYBPqH1tIhsYVGoJFruNkJ8NttOGw2iECIHgZDZD

Ask the user:
1. **What is the ad account ID?** (format: `act_123456789` — accept with or without `act_` prefix)
2. **What's the primary metric for this account?** CPA or ROAS?
3. **What's the target?** (e.g., "£25 CPA" or "2.5x ROAS")
4. **What date range?** (default: 30 days. Accept: 7, 14, 30, 60, 90)
5. **Client name?** (for report title and file naming)

If the user provides an account ID inline (e.g., "run creative health on act_249000693"), extract it and ask only what's missing. The metric choice is important — it changes every table and comparison in the report.

### Step 1 — Pull Ad Data

```bash
python3 {SKILL_DIR}/scripts/pull_ads.py <ad_account_id> --days <N> --output /tmp/creative-health/<client_slug>
```

**IMPORTANT:** Use `timeout=600000` (10 min) on the Bash call. The script makes many API calls
with rate-limit handling and fetches video durations for video ads.

If a compare period was requested, run a second pull:
```bash
python3 {SKILL_DIR}/scripts/pull_ads.py <ad_account_id> --days <compare_N> --output /tmp/creative-health/<client_slug>-compare
```

**Output:** CSV file with columns: ad_name, ad_id, campaign_name, adset_name, spend, impressions,
clicks, ctr, cpc, cpm, purchases, purchase_value, roas, video_3sec, thruplay, video_p25,
video_p50, video_p75, video_p100, video_duration_sec

### Step 2 — Generate Report

```bash
python3 {SKILL_DIR}/scripts/generate_report.py --input /tmp/creative-health/<client_slug>/ads.csv --client "<Client Name>" --account "<account_id>" --days <N> --metric <cpa|roas> --target <number> --output <client_working_dir>/creative-health-report.html
```

- `--metric cpa` or `--metric roas` — sets the primary metric for the entire report
- `--target 25` — sets the CPA target (£25) or ROAS target (2.5x) depending on metric choice

**Output files:**
| File | Purpose |
|------|---------|
| `creative-health-report.html` | Interactive HTML report — open in browser |
| `creative-health-enriched.csv` | Every ad with parsed dimensions + calculated metrics |
| `creative-health-summary.json` | Structured summary for downstream skills |

### Step 3 — Read Project Context

Before writing interpretations, gather all available context from the client's working directory:

- Read `BRAND-INTELLIGENCE.md` if it exists — brand positioning, USPs, product details
- Read `PERSONA-STRATEGY.md` if it exists — persona framework, priority ranking, hooks
- Read `STRATEGIC-BRIEF.md` if it exists — confirmed strategy, messaging territories
- Read `MUST-READ-SCRIPTING.md` if it exists — scripting rules, format guidance
- Read `ACCOUNT-AUDIT.md` if it exists — previous audit findings

If none exist, interpret purely from the data. If they exist, ground every interpretation
and iteration in the confirmed strategy — not generic advice.

### Step 4 — Write Interpretations

Read the summary JSON file (`creative-health-report-summary.json`). For each section that has
an `<!-- INTERPRETATION:section_id -->` placeholder in the HTML, write a narrative interpretation.

**How to write interpretations:**
- Lead with the single most important finding in that section
- State what the data shows, then what it means for creative strategy
- Reference specific ads by name when making claims
- Compare against the persona strategy / strategic brief if available
- Be confident and direct — this is expert analysis, not hedging
- 3-5 sentences per section, no filler

**Sections to interpret:**
1. `volume` — creative volume and spend concentration
2. `winners` — winner distribution, where winners cluster, what makes them win
3. `funnel` — funnel balance, skew, what's missing
4. `angle` — angle diversity, which angles perform vs which get spend
5. `media` — format mix, what formats are being underused
6. `heatmap` — cross-dimensional gaps (e.g., "Social Proof × MOF = £0 — zero mid-funnel proof ads")
7. `video` — video performance, hook vs hold performance, duration insights
8. `deadweight` — patterns in dead weight ads, what they have in common

Use the Edit tool to replace each `<!-- INTERPRETATION:section_id -->` placeholder with
the narrative HTML wrapped in `<p>` tags.

### Step 5 — Write Iteration Scripts

This is the most important section. Read the top 10 ads from the summary JSON. For each
ad that has iteration potential, write a **specific, production-ready script**.

**Iteration candidates (pick 4-6):**
- Winners with untested format variants (e.g., winning static → test as UGC video)
- High-spend ads with weak metric performance (strong hook, weak conversion — fix the body)
- Angles with zero presence in a funnel stage (from heatmap gaps)
- Dead weight ads with salvageable elements (good concept, wrong execution)

**Script format for each iteration:**

```html
<div class="iteration-card">
    <h4>Iteration: [New concept name]</h4>
    <p class="muted">Based on: [original ad name] · [what we're changing and why]</p>
    <div class="script-section"><span class="script-label">Hook (0-3s):</span> [Exact opening line or visual description]</div>
    <div class="script-section"><span class="script-label">Body (3-15s):</span> [What happens in the middle — proof, story, demonstration]</div>
    <div class="script-section"><span class="script-label">CTA:</span> [Closing line + action]</div>
    <div class="script-section"><span class="script-label">Headline:</span> [Ad headline text]</div>
    <div class="script-section"><span class="script-label">Primary text:</span> [Ad primary text / caption]</div>
    <div class="script-meta">
        <span class="meta-tag">Format: [Static/Video/UGC/Carousel]</span>
        <span class="meta-tag">Funnel: [TOF/MOF/BOF]</span>
        <span class="meta-tag">Angle: [angle name]</span>
        <span class="meta-tag">Product: [product]</span>
    </div>
</div>
```

**Rules for iteration scripts:**
- Every script must reference a specific live ad it's iterating on
- State clearly what you're changing and why (format? angle? funnel stage? hook?)
- Use the client's confirmed brand language (from BRAND-INTELLIGENCE.md / MUST-READ-SCRIPTING.md)
- Match hook/body structure to the persona it's targeting (from PERSONA-STRATEGY.md)
- If the iteration involves a format change (static → video), describe the visual, not just the copy
- Include headline + primary text — these are production-ready, not placeholders

Use the Edit tool to replace `<!-- ITERATIONS -->` with the iteration cards HTML.

### Step 6 — Open and Present

Open the completed HTML report:
```bash
open <client_working_dir>/creative-health-report.html
```

Tell the user:
- The report is open with data + interpretations + iteration scripts
- Highlight the composite score and 2-3 key findings
- Flag which iteration scripts are highest priority based on the data

## Naming Convention

The skill parses the LWU naming convention:
```
LWUBTR{conceptID}-{variant}_{funnel}_{angle}_{painpoint?}_{mediatype}_{product}_{date}_{identity?}
```

### Normalisation

The parser handles inconsistent separators (spaces, hyphens, tildes) and collapses variants:

**Funnels:** Problem Aware / Problem-Aware / Problem~Aware → TOF | Solution Aware → MOF | Product Aware → BOF

**Angles:** See ANGLE_ALIASES in generate_report.py — 20+ raw variants collapse to ~10 canonical angles.

**Media types:** Detected by anchor matching (Static, Video, UGC, Carousel) — position-independent.

**Inherited/unstructured ads** (ID_, img_, vid_ prefixes) are flagged separately with whatever
can be extracted from campaign/adset names.

## Scoring Model

### Composite Creative Health Score (0-100)

| Sub-score | Weight | What it measures |
|-----------|--------|------------------|
| Funnel Balance | 10% | Penalises >70% in one stage |
| Angle Diversity | 10% | HHI-based concentration |
| Media Type Diversity | 10% | Penalises >80% one format |
| Winner Hit Rate | 15% | % of ads that are winners (10x median spend + purchases) |
| Spend on Winners | 15% | % of spend going to winning ads |
| Thumbstop Rate | 10% | Avg 3-sec view rate vs 30% benchmark |
| Hold Rate | 10% | Avg ThruPlay/3-sec vs 25% benchmark |
| Naming Compliance | 10% | % of ads that parse cleanly |
| Creative Volume | 10% | Ads per week vs tier benchmark |

### Dimension Scoring

Each dimension (funnel, angle, media type, product) is scored via HHI (Herfindahl-Hirschman Index):
- HHI < 1500 = Diverse (green)
- HHI 1500-2500 = Moderate (amber)
- HHI > 2500 = Concentrated (red)

### Winner Classification

Based on Motion 2026 Creative Benchmarks methodology:
- **Winner:** Spend ≥ 10× account median AND ≥1 purchase
- **Mid:** Has purchases but below winner threshold
- **Loser:** Zero purchases

## Future Enhancements (not built yet)

- `--deep` mode: Download creative assets + Gemini analysis for messaging territory detection,
  hook type classification, and visual diversity scoring
- Dual-period trend comparison in the HTML report
- Auto pre-fill of the manual Creative Audit Notion template
- Persona dimension scoring (once naming convention includes persona codes)
