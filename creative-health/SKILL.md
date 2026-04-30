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

API keys are stored in `~/.claude/api_keys.json` (Meta token + Gemini key). Scripts read from
this file automatically. If a key is missing or expired, the script will fail with a clear error.

**Client roster:** All LWU clients are pre-configured in `{SKILL_DIR}/clients.json`. Read that
file first — it contains each client's account ID, metric, target, icon, cover image, and
output directory. The user should NOT have to type account IDs or targets.

Ask the user (use AskUserQuestion):
1. **Which client?** (Show the list from clients.json — e.g., "Butter & Crust 🥐", "Carbeth Plants 🪴", "A-Game 🏃", "Flow Hair 🎀", "Heist Of London 💇")
2. **What date range?** (7, 14, 30 [default], 60, or 90 days)
3. **Deep mode?** (default: no. Deep mode downloads top creative assets and sends them to Gemini for hook/headline extraction. Adds ~5 min but gives you a hooks performance table in the report.)

Once the client is picked, load their config entry and use those values for everything downstream:
- `account` → ad account ID
- `metric` → CPA or ROAS
- `target` → metric target (0 means no target — skip the Target KPI)
- `icon` → emoji for the header
- `cover` → cover image path (resolved relative to SKILL_DIR)
- `output_dir` → archive root (expand `~` to the user's home directory)

If the user mentions a client inline (e.g., "run creative health for Carbeth"), match the name
against `clients.json` keys/names and skip question 1.

**Adding a new client:** edit `clients.json` directly. No other files need to change.

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

### Step 2 — Validate Numbers Before Proceeding

**CRITICAL: Do NOT generate the report until the user confirms these numbers.**

After the pull completes, read the `pull_metadata.json` and `account_frequency.json` from the
output directory. Present the key metrics to the user in this exact format:

```
Data Validation — please check these against Ads Manager:

| Metric          | API Value       | Where to check in Ads Manager            |
|-----------------|-----------------|------------------------------------------|
| Date Range      | [start] – [end] | Match your Ads Manager date range        |
| Total Spend     | £X,XXX          | Account overview → total spend           |
| Total Purchases | XXX             | Actions column → Purchases               |
| Blended CPA     | £XX.XX          | Spend ÷ Purchases                        |
| Frequency       | X.XX            | Account overview → Frequency             |
| Active Ads      | XXX             | Ads tab → filter spend > 0               |
| Video Ads       | XX              | Ads tab → filter by video                |

Do these match? Type 'yes' to proceed or flag any discrepancies.
```

Use AskUserQuestion to present this and wait for confirmation.

- If the user confirms → proceed to Step 3
- If the user flags a discrepancy → investigate. Common causes:
  - Date range off by 1 day (re-run with exact dates)
  - Attribution window difference (API defaults to 7d click / 1d view)
  - Currency mismatch
  - Purchases metric type (omni_purchase vs purchase)

Do NOT skip this step. Do NOT proceed on assumption.

### Step 2.5 — Deep Mode: Gemini Asset Analysis (if requested)

**Only run this step if the user opted into deep mode.**

```bash
python3 {SKILL_DIR}/scripts/analyse_assets.py --ads-csv /tmp/creative-health/<client_slug>/ads.csv --account <ad_account_id> --top-n 15 --output /tmp/creative-health/<client_slug>
```

**IMPORTANT:** Use `timeout=600000` (10 min). This downloads creative assets and uploads them to
Gemini for analysis. Expect ~2 seconds per ad + video processing time.

**Output:** `gemini_analysis.json` in the same output directory. Contains per-ad hook text,
headline text, hook type, visual description, and asset type — paired with spend/CPA/CTR.

The report generator auto-detects this file in the input directory and adds a Hooks & Headlines
Performance section to the HTML report.

### Step 3 — Generate Report

Reports are archived to `<output_dir>/<YYYY-MM-DD>/`, where `output_dir` comes from the
client's entry in `clients.json`. Expand `~` to the user's home. Create the directory
if it doesn't exist.

```bash
python3 {SKILL_DIR}/scripts/generate_report.py \
  --input /tmp/creative-health/<client_slug>/ads.csv \
  --client "<config.name>" \
  --account "<config.account>" \
  --days <N> \
  --metric <config.metric> \
  --target <config.target> \
  --cover-image {SKILL_DIR}/<config.cover> \
  --icon "<config.icon>" \
  --output <config.output_dir>/<YYYY-MM-DD>/creative-health-report.html
```

- All values come from the client's config — don't prompt for them
- If `config.target` is 0, the Target KPI is omitted automatically
- `--cover-image` and `--icon` are mandatory per client so branding is consistent

**Output files (all saved to the archive directory):**
| File | Purpose |
|------|---------|
| `creative-health-report.html` | Self-contained HTML report — shareable, downloadable |
| `creative-health-enriched.csv` | Every ad with parsed dimensions + calculated metrics |
| `creative-health-summary.json` | Structured summary for downstream skills |

### Step 3 — Read Project Context

The client's working directory is typically `~/Desktop/<client-slug>/` (same folder where
reports are archived — see `output_dir` in clients.json, just go up one level if needed).

Before writing interpretations, gather all available context from that directory:

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
8. `hooks` — (deep mode only) hook type patterns, which hooks drive lowest CPA, headline patterns
9. `deadweight` — patterns in dead weight ads, what they have in common

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

Open the completed HTML report using the archive path from the client's config:
```bash
open <config.output_dir>/<YYYY-MM-DD>/creative-health-report.html
```

Tell the user:
- The report is open with data + interpretations + iteration scripts
- Highlight the composite score and 2-3 key findings
- Flag which iteration scripts are highest priority based on the data
- Remind them the HTML is self-contained and ready to share — just send the `.html` file

**Previous reports** for the same client live in sibling date folders inside the client's
`output_dir`. Each run creates a new dated folder — older reports are kept automatically.

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

- Dual-period trend comparison in the HTML report
- Auto pre-fill of the manual Creative Audit Notion template
- Persona dimension scoring (once naming convention includes persona codes)
