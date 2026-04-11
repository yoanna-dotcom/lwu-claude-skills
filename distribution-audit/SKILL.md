---
name: distribution-audit
description: >
  Run an automated Distribution Audit on a Meta ad account using the Marketing API.
  Pulls account structure, campaign/ad set/ad performance metrics, 30-day daily trends,
  attribution window comparisons, landing page URLs with performance, ad identity analysis,
  exclusion coverage, audience segment breakdowns, and account activity/change log
  — then reasons through the data to produce a comprehensive Distribution pillar assessment
  aligned with the Growth Compass framework. Use this skill whenever someone asks to audit a
  Meta ad account's distribution health, run a distribution audit, analyse account structure,
  pull Meta API data for an account audit, or wants to understand how an ad account is structured
  and performing. Also trigger when someone mentions "account audit", "distribution health",
  "account structure analysis", "Meta account pull", or provides a Meta ad account ID and wants
  performance data extracted and analysed.
---

# Distribution Audit Skill

## What This Skill Does

This skill automates the data collection layer of the Distribution Audit Worksheet by pulling
structured data from the Meta Marketing API, then performs AI analysis on the results to produce
an actionable distribution health assessment aligned with the 7-part Worksheet structure.

It covers:
1. **Account Structure** — Brand size classification, campaign types (ASC/Catalogue/ABO/CBO), budget allocation vs benchmarks, consolidation, critical config, naming conventions
2. **Reach & Audience Health** — Frequency, CPMr, saturation diagnosis
3. **Partnership Ads & Identity Diversification** — 5-type identity taxonomy with performance per identity
4. **Media Mix & Channel Distribution** — Meta-only from API; flags manual completion needed for other channels
5. **Technical Infrastructure** — Attribution specs, existing customer caps, **exclusion coverage**, URL tracking, optimisation objectives
6. **Performance Snapshot** — Campaign, market, and landing page level metrics with trend analysis
6b. **Account Change Log Analysis** — Management cadence, change categories, daily activity vs performance correlation, management gaps, day-of-week patterns, key change event reconstruction
7. **Opportunities** — Up to 10 suggested opportunities (no ICE scoring)

## How to Run

### Step 0 — Ask the User

The Meta API token is pre-configured:
META_ACCESS_TOKEN: EAAUeobHyYdsBQZCVPLlEq42kOIGHojQbz8Ag2a007TJb7vQe8TRBfWuZAFcOZBFxd3k0Eqoh6wZBrRW85ZAUsZBxV5gz2cfYQb9wYk3SViWtjk13SGPa9ZAvh1gZB2ZAnjlKg9lq3doCNTHwdFZCDSBMExNAc3LguYBPqH1tIhsYVGoJFruNkJ8NttOGw2iECIHgZDZD

Before running anything, ask the user:
1. **What is the ad account ID?** (format: `act_123456789`)
2. **What timeframe should we analyse?** (default: 90 days)
3. **Any specific markets or campaigns to focus on?**

### Step 1 — Run the Data Extraction

**IMPORTANT: Use a 600-second (10 minute) timeout on the Bash command.** The default 120s timeout
is NOT enough — the script makes dozens of API calls with rate-limit handling and typically takes
3-8 minutes depending on account size.

```bash
# CRITICAL: Always set timeout=600000 (600 seconds) on your Bash tool call
python {SKILL_DIR}/scripts/pull_distribution_data.py <ad_account_id> --output-dir /tmp/distribution-audit-data --days 30
```

Replace `{SKILL_DIR}` with the actual path to this skill's directory.
Adjust `--days` based on the user's requested timeframe (default 30).

The script outputs progress as it runs so you can monitor each phase. If you see rate-limit
messages, that's normal — the script handles retries automatically.

### Step 2 — Load and Analyse the Data

Once the script completes, read the output files and perform the analysis below.

**Files produced:**

| File | Purpose | Read Priority |
|------|---------|--------------|
| `account_summary.json` | Pre-computed structure + spend distribution + reach health + brand size + **exclusions** | **Read first** |
| `identity_summary.json` | 5-type identity taxonomy with page/actor names | **Read first** |
| `identity_performance.json` | Spend, ROAS, CPP per identity | **Read first** |
| `optimisation_analysis.json` | Spend breakdown by optimisation objective | **Read first** |
| `market_data.json` | Market-level performance from ad set geo targeting | **Read first** |
| `non_conversion_flags.json` | Non-conversion campaigns and boosted posts flagged | **Read first** |
| `audience_segments.json` | **New/Engaged/Existing customer segment breakdown** | **Read first** |
| `landing_pages_aggregated.json` | LP performance grouped by URL | **Read second** |
| `attribution_comparison.json` | Performance under different attribution windows | **Read second** |
| `daily_account_trends.json` | Account-level daily spend/ROAS/CPM/frequency | **Read second** |
| `daily_campaign_trends.json` | Campaign-level daily breakdown | **Read second** |
| `campaign_insights_perf.json` | Performance-window campaign metrics | Reference as needed |
| `adset_insights_perf.json` | Performance-window ad set metrics | Reference as needed |
| `ad_insights_perf.json` | Performance-window ad-level metrics | Reference as needed |
| `campaigns_with_delivery.json` | Only campaigns with delivery in 90d | Reference as needed |
| `adsets_raw.json` | Ad set config (delivery campaigns only) | Reference as needed |
| `ads_raw.json` | Ads with creative data (delivery campaigns only) | Reference as needed |
| `activity_log.json` | **Account change log — daily activity, categories, gaps, day-of-week** | **Read second** |

### Step 3 — The Analysis Framework

Read the priority files first, then work through each section of the analysis below.
Write your analysis as a structured report following the 7-part Worksheet format.

**CRITICAL RULES:**
- **Only reference campaigns with delivery.** Dormant campaigns (active shell but no delivery in 90d) should be a single footnote, not headline numbers.
- **Anchor all structural analysis on `campaigns_with_delivery`**, not `campaigns_raw`.
- **Use the brand size tier** from `account_summary.json → brand_size` to apply the correct benchmarks throughout.
- **Do not ICE-score opportunities.** List up to 10 as plain suggestions.
- **Campaign types now include 4 categories:** ASC (Advantage+ Sales), Catalogue (DPA/Dynamic Product Ads), CBO, and ABO. Use the `campaign_type` field on each campaign in spend distribution data.

---

## Campaign Type Detection (v2 — Updated March 2026)

**IMPORTANT CONTEXT:** Meta deprecated the `AUTOMATED_SHOPPING_ADS` value for `smart_promotion_type` in 2025. All campaigns — including ASC — now return `smart_promotion_type: "GUIDED_CREATION"`. The script uses a multi-signal detection approach:

### ASC (Advantage+ Sales) Detection
A campaign is classified as ASC if ANY of these conditions are met:
1. **Legacy:** `smart_promotion_type == "AUTOMATED_SHOPPING_ADS"` (pre-2025 campaigns)
2. **Modern:** ALL of these conditions are true:
   - `objective == "OUTCOME_SALES"`
   - `smart_promotion_type == "GUIDED_CREATION"`
   - Campaign has a campaign-level budget (`daily_budget` or `lifetime_budget`)
   - At least one ad set has `targeting_automation.advantage_audience == 1`

### Catalogue / DPA Detection
A campaign is classified as Catalogue if:
- Campaign name contains "catalogue", "catalog", "dpa", or "dynamic product" (case-insensitive), OR
- Any ad set has `optimization_goal == "VALUE"`

### CBO vs ABO
- **CBO:** Has campaign-level budget (`daily_budget` or `lifetime_budget`) but doesn't meet ASC or Catalogue criteria
- **ABO:** No campaign-level budget (budget set at ad set level)

### `asc_detection_note` Field
The `account_summary.json` output includes an `asc_detection_note` field explaining the detection method used. Always reference this in your analysis for transparency.

---

## Exclusion Detection (v2 — New)

The script now extracts `excluded_custom_audiences` from every ad set's `targeting` field.

### Data Location
`account_summary.json → exclusions` contains:

```json
{
  "exclusions": {
    "adsets_with_exclusions": 9,
    "adsets_without_exclusions": 0,
    "total_adsets": 9,
    "exclusion_coverage_pct": 100.0,
    "unique_excluded_audiences": {
      "audience_id_1": "Purchasers - Klaviyo",
      "audience_id_2": "Purchasers - Pixel 180d"
    },
    "unique_excluded_audience_count": 6,
    "details": [
      {
        "adset_id": "...",
        "adset_name": "...",
        "campaign_id": "...",
        "exclusion_count": 6,
        "excluded_audiences": [
          {"id": "...", "name": "Purchasers - Klaviyo"}
        ]
      }
    ]
  }
}
```

### How to Use in Analysis
- **Coverage %**: `exclusion_coverage_pct` tells you what percentage of ad sets have exclusions. 100% = full coverage.
- **Audience names**: The `unique_excluded_audiences` dict shows what's being excluded (Klaviyo lists, pixel-based purchasers, etc.)
- **Per-ad-set detail**: The `details` array lets you identify which specific ad sets are missing exclusions.
- **Critical config checklist**: Use this data to definitively check the "ASC Core has purchaser exclusions" box — no more guessing.

---

## Audience Segments (v2 — New)

The script now fetches audience segment breakdowns (New / Engaged / Existing customers) using Meta's `user_persona_name` breakdown.

### Data Location
`audience_segments.json` contains:

```json
{
  "has_audience_segments_configured": true,
  "note": "Audience segments are active and returning data.",
  "segment_totals": {
    "New": {"spend": 1234.56, "impressions": 50000, "reach": 30000, "purchases": 50, "purchase_value": 5000.0},
    "Engaged": {"spend": 500.0, ...},
    "Existing": {"spend": 200.0, ...}
  },
  "by_campaign": [...]
}
```

### How to Use in Analysis
- **If `has_audience_segments_configured` is `true`**: Report the spend split between New/Engaged/Existing. Flag if Existing customer spend is >20% (acquisition efficiency concern).
- **If `has_audience_segments_configured` is `false`**: Flag this as a setup gap. The advertiser needs to define Engaged Audience and Existing Customer definitions in **Ads Manager → Account Settings → Audience Segments**. This is required for proper new customer acquisition tracking and should be recommended as a Quick Win opportunity.

---

## Activity / Change Log (v2 — New)

The script now fetches the account activity log from the Meta Marketing API, covering all changes made within the performance window.

### Data Location
`activity_log.json` contains:

```json
{
  "total_activities": 1886,
  "active_days": 10,
  "total_calendar_days": 31,
  "avg_changes_per_active_day": 188.6,
  "event_type_breakdown": {
    "update_ad_run_status": 1367,
    "edit_images": 69,
    "create_ad": 34,
    "update_ad_set_budget": 33
  },
  "category_breakdown": {
    "Ad Status Changes (on/off)": 1440,
    "Creative Changes": 123,
    "Budget Adjustments": 38,
    "New Ads/Sets/Campaigns": 37
  },
  "daily_activity": [
    {
      "date": "2026-02-24",
      "total_changes": 179,
      "status_changes": 164,
      "budget_changes": 2,
      "creative_changes": 0,
      "new_entities": 0,
      "targeting_changes": 0,
      "event_detail": {"update_ad_run_status": 164, ...}
    }
  ],
  "day_of_week_distribution": {
    "Monday": 120, "Tuesday": 807, "Wednesday": 133,
    "Thursday": 99, "Friday": 716, "Saturday": 0, "Sunday": 11
  },
  "management_gaps": [
    {"start": "2026-02-28", "end": "2026-03-08", "days": 9}
  ],
  "raw_events": [...]
}
```

### How to Use in Analysis
- **`active_days` vs `total_calendar_days`**: Calculate management coverage percentage. Compare against brand tier benchmarks.
- **`category_breakdown`**: Identify what types of changes dominate. Flag if >80% is a single category.
- **`daily_activity`**: Cross-reference each day with `daily_account_trends.json` to correlate changes with performance shifts.
- **`management_gaps`**: Flag any gap ≥3 days. For Mid-Market+, gaps >5 days are a concern.
- **`day_of_week_distribution`**: Identify if management is concentrated on specific days vs. distributed.
- **`raw_events`**: Only `event_type` and `event_time` are reliably returned — object IDs and names depend on token permissions.

---

## Analysis Framework

### Part 1: Account Structure Assessment

Look at `account_summary.json` → `brand_size`, `structure`, `spend_distribution_30d`, and the raw campaign/adset files.

#### 1.1 Brand Size Classification

From `account_summary.json → brand_size`:

| Brand Size | Monthly Meta Spend | Structure Focus |
|---|---|---|
| Small | Under £100k/mo | 2 campaigns (ASC Core + ABO Testing). Purchase optimisation only. |
| Mid-Market | £100k–500k/mo | 3-5 campaigns. Add Mid-Funnel (ATC/VC) at 10-20%. |
| Large | Over £500k/mo | 5-8+ campaigns. Add Upper Funnel (Reach/ThruPlay) at 5-15%. |

State the brand's tier and the relevant benchmarks that apply.

#### 1.2 Budget Allocation vs Benchmarks

Compare actual spend allocation against the tier-specific benchmarks. **Note: campaign types now include ASC, Catalogue, CBO, and ABO.** Catalogue campaigns should be reported separately from ASC.

| Campaign Type | Small Benchmark | Mid Benchmark | Large Benchmark | Current % | RAG |
|---|---|---|---|---|---|
| ASC Core | 70-90% | 60-75% | 40-60% | [from data] | 🔴🟡🟢 |
| Catalogue / DPA | Context dependent | Context dependent | Context dependent | [from data] | 🔴🟡🟢 |
| ABO Creative Testing | 10-30% | 10-25% | 5-20% | [from data] | 🔴🟡🟢 |
| Mid-Funnel (VC/ATC) | None | 10-20% | 15-25% | [from data] | 🔴🟡🟢 |
| Upper Funnel (Reach) | None | None | 5-15% | [from data] | 🔴🟡🟢 |

Flag any mismatches. For small brands running mid-funnel or upper funnel campaigns, flag this as structural misalignment.

#### 1.3 Campaign Volume Audit

From `account_summary.json → structure` and raw adset/ad files, calculate:

| Check | Benchmark | Current | RAG | Action |
|---|---|---|---|---|
| Total active campaigns (with delivery) | Small: 5–10 / Mid: 10–20 / Large: 20–40 | [from data] | 🔴🟡🟢 | |
| Active ad sets per campaign | 3–10 (tier-dependent) | [calculate average] | 🔴🟡🟢 | |
| Active ads per ad set | 3–5 | [calculate average] | 🔴🟡🟢 | |

If the account has significantly more campaigns than the benchmark, flag over-fragmentation.
If ad sets per campaign is very low (1-2) or very high (15+), flag consolidation opportunity or fragmentation.

#### 1.4 Naming Convention Compliance

Read `campaigns_with_delivery.json`, `adsets_raw.json`, and `ads_raw.json`. Assess the names:

| Check | RAG | Notes |
|---|---|---|
| Campaigns follow a consistent naming format | 🔴🟡🟢 | [assess patterns — e.g. "UK - ASC - Core" vs inconsistent] |
| Ad sets follow a consistent naming format | 🔴🟡🟢 | [assess patterns] |
| Ads follow a consistent naming format | 🔴🟡🟢 | [assess patterns] |
| Campaign type (ASC / Catalogue / ABO) is identifiable from name | 🔴🟡🟢 | [can you tell the campaign type from the name?] |

Good naming conventions should include: market/geo, campaign type, objective, and date or version. Flag inconsistencies.

#### 1.5 Optimisation Objective Assessment

Read `optimisation_analysis.json`.

| Optimisation Goal | Ad Sets | Spend | Spend % | RAG |
|---|---|---|---|---|
| OFFSITE_CONVERSIONS (Purchase) | [count] | [amount] | [%] | 🟢 |
| [other goals present] | [count] | [amount] | [%] | 🔴🟡🟢 |

**Per the Ad Account Structure Framework:**
- **Small brands (<£100k/mo):** Purchase optimisation should be primary. ATC/VC optimisation is not justified at this spend level — it's "hemorrhaging cash" without the volume to make mid-funnel worthwhile.
- **Mid brands (£100-500k/mo):** Purchase primary + Mid-funnel (ATC/VC) at 10-20% is justified.
- **Large brands (>£500k/mo):** Purchase primary + Mid-funnel + Upper funnel (Reach/ThruPlay) at 5-15%.

Flag any non-purchase objectives that don't match the brand's tier.

#### 1.6 Non-Conversion Campaigns & Boosted Posts

Read `non_conversion_flags.json`.

Flag any campaigns with POST_ENGAGEMENT, LINK_CLICKS, REACH, or VIDEO_VIEWS objectives and calculate their total spend. Identify boosted Instagram posts specifically. Recommend whether this spend is intentional brand investment or waste.

#### 1.7 Critical Configuration Checklist

Assess from the data available. **Exclusion data is now available directly from `account_summary.json → exclusions`.**

- [ ] **ASC Core has purchaser exclusions** — Check `exclusions.exclusion_coverage_pct` and `exclusions.unique_excluded_audiences`. Look for Klaviyo purchaser lists and pixel-based purchaser audiences. If coverage is <100%, identify which ad sets are missing exclusions.
- [ ] **Exclusions set between multiple ASC campaigns** — If multiple ASC campaigns exist, check if they share the same exclusion audiences (overlap risk) or have differentiated exclusions.
- [ ] ABO testing campaign is active and isolated from ASC
- [ ] Attribution window matches the brand's conversion cycle (check `attribution_specs` in account_summary)
- [ ] Existing customer cap is set correctly in ASC (0-10%) (check `existing_customer_caps` in account_summary)
- [ ] Value or manual bidding only active if 50+ conversions (check `bid_strategy` on campaigns)
- [ ] **Audience Segments configured** — Check `audience_segments.json → has_audience_segments_configured`. If false, flag as a setup gap.
- [ ] CAPI implementation — **Requires manual verification** (flag for growth strategist to check)
- [ ] Klaviyo purchaser sync — **Requires manual verification** (flag for growth strategist to check)

---

### Part 2: Reach & Audience Health

Look at `account_summary.json → reach_health_90d` and `daily_account_trends.json`.

#### 2.1 Core Reach Metrics

| Metric | Healthy Range | Current Value | RAG |
|---|---|---|---|
| Blended Frequency (90d) | <3.5 | [from data] | 🔴🟡🟢 |
| CPM (90d) | £8–£15 (category dependent) | [from data] | 🔴🟡🟢 |
| CPMr (CPM × Frequency) | Stable or declining week-over-week | [from data] | 🔴🟡🟢 |
| Unique Reach (90d) | Context dependent | [from data] | |

**CPMr is the key proxy metric for reach health.** Rising CPMr = paying more to reach the same people repeatedly = saturation. Calculate CPMr from the daily trends to assess the trend direction.

#### 2.2 Per-Campaign Frequency Check

For each campaign with delivery, check frequency against these thresholds:
- **Prospecting campaigns:** Frequency >3.5 = concern, >4.0 = saturation warning
- **Retargeting campaigns:** Higher frequency acceptable but >8.0 = concern

#### 2.3 Saturation Diagnosis

Check if 3+ of these signals are present (based on available data):
- [ ] CPAs rising despite stable creative performance
- [ ] Frequency above 3-4 on core prospecting campaigns
- [ ] Diminishing returns when increasing budget (check daily trends: spend up, ROAS down)
- [ ] New creatives fatiguing faster than before
- [ ] Conversion volume flat despite spend increases
- [ ] Strong engagement rates but weak conversion rates
- [ ] High CPMr and rising trend

If 3+ signals present: **Incremental reach is likely the primary scaling bottleneck.**

#### 2.4 Audience Segment Health

**New in v2:** If `audience_segments.json → has_audience_segments_configured` is true, analyse the spend split:

| Segment | Spend | Spend % | Purchases | ROAS | Flag |
|---|---|---|---|---|---|
| New | [amount] | [%] | [count] | [roas] | Healthy if >60% |
| Engaged | [amount] | [%] | [count] | [roas] | Flag if >30% |
| Existing | [amount] | [%] | [count] | [roas] | Flag if >20% |

High Existing customer spend relative to total indicates the account is over-indexing on remarketing and not driving incremental acquisition. Cross-reference with frequency data — high Existing % + high frequency = definitive saturation.

#### 2.5 FTI% and Audience Reached Ratio

Note: FTI% (First-Time Impression %) and Audience Reached Ratio are not available via the Marketing API. They require Delivery Insights access or a Meta rep report. **Recommend requesting this data from the client's Meta rep** as it's critical for reach health assessment.

---

### Part 3: Partnership Ads & Identity Diversification

Read `identity_summary.json` and `identity_performance.json`.

#### 3.1 Identity Inventory (5-Type Taxonomy)

The script provides page names and categories. Classify each unique page/identity into one of these 5 types:

| Identity Type | In Use? | Page Name(s) | Ad Count | RAG |
|---|---|---|---|---|
| Brand Page (primary) | [Yes — always] | [from data] | [count] | |
| Founder Identity | [Yes/No] | [page name if present] | [count] | 🔴🟡🟢 |
| Customer Persona Pages | [Yes/No] | [page names targeting specific segments] | [count] | 🔴🟡🟢 |
| Third-Party Positioning | [Yes/No] | [review sites, niche authorities, advertorials] | [count] | 🔴🟡🟢 |
| Creator/Partnership Ads | [Yes/No] | [creator pages/handles] | [count] | 🔴🟡🟢 |

Use the `page_inventory` in identity_summary to classify. The script marks pages as `brand_page` or `non_brand` — you need to refine `non_brand` into the 4 sub-types based on page name, category, and context.

**Detection hints:**
- **Founder:** Personal-sounding page name, typically the founder's actual name or personal brand
- **Customer Persona:** Brand-owned pages with segment-specific naming (e.g. "The Menopause Collective", "ADHD Focus Hub")
- **Third-Party Positioning:** Pages positioned as review sites, comparison platforms, or niche authorities (e.g. "Best Supplements UK", "Skin Science Reviews")
- **Creator/Partnership:** Instagram/Facebook accounts of creators/influencers — different fan_count profile, typically higher engagement pages not owned by the brand

#### 3.2 Identity Performance

From `identity_performance.json`, create a performance table:

| Identity | Type | Spend | Spend % | CPM | Frequency | Purchases | CPP | ROAS |
|---|---|---|---|---|---|---|---|---|
| [page name] | [type] | [amount] | [%] | [cpm] | [freq] | [count] | [cpp] | [roas] |

Analyse which identities are outperforming/underperforming the account average.

#### 3.3 Identity Diversification Opportunity

If the account is >80% brand page, flag identity diversification as a key opportunity:

| Lever | Opportunity Present? | Notes |
|---|---|---|
| Founder content (origin story, mission) | [Yes/No/Already Active] | |
| Team expert content (nutritionist, designer, etc.) | [Yes/No/Already Active] | |
| Customer persona page targeting specific segments | [Yes/No/Already Active] | |
| Review/comparison site positioning | [Yes/No/Already Active] | |
| Creator/partnership ads | [Yes/No/Already Active] | |

> Identity is the strongest multiplier for incremental reach because it signals to entirely different user clusters.

---

### Part 4: Media Mix & Channel Distribution

**Note:** This section requires data beyond Meta's API. Flag for manual completion:

"This audit covers Meta distribution only. For a complete media mix assessment, the growth strategist should manually assess spend allocation across Google (PPC/Shopping), TikTok, and other channels."

If the Meta data suggests the brand is heavily Meta-dependent (e.g. high frequency, saturation signals), recommend evaluating channel diversification.

---

### Part 5: Technical Infrastructure

From `account_summary.json` → `attribution_specs`, `existing_customer_caps`, `exclusions`, and ad set data:

| Check | Status | RAG | Notes |
|---|---|---|---|
| Attribution specs consistent across ad sets | [check] | 🔴🟡🟢 | |
| Attribution window matches conversion cycle | [check] | 🔴🟡🟢 | |
| Existing customer cap on ASC (0-10%) | [check] | 🔴🟡🟢 | |
| **Purchaser exclusions on ASC ad sets** | [from exclusions data] | 🔴🟡🟢 | Coverage: [exclusion_coverage_pct]% |
| **Exclusion audiences include Klaviyo sync** | [check audience names] | 🔴🟡🟢 | Look for "Klaviyo" in excluded audience names |
| **Audience Segments configured** | [from audience_segments.json] | 🔴🟡🟢 | Required for new customer tracking |
| URL parameter tracking configured | [check from ad url_tags] | 🔴🟡🟢 | |
| CAPI implementation | Requires manual check | ⚪ | Flag for verification |
| Klaviyo purchaser sync | Requires manual check | ⚪ | Flag for verification |
| Event Match Quality (>6.0) | Requires manual check | ⚪ | Flag for verification |
| Time zone & currency correct | [from account_info] | 🔴🟡🟢 | |

---

### Part 6: Performance Snapshot

#### 6.1 Market-Level Summary (if multi-market)

Read `market_data.json`. If multiple markets are present:

| Market | Campaigns | Ad Sets | Spend | Spend % | CPM | Freq | Purchases | CPP | ROAS |
|---|---|---|---|---|---|---|---|---|---|
| [country] | [count] | [count] | [amount] | [%] | [cpm] | [freq] | [count] | [cpp] | [roas] |

Identify which markets are performing vs struggling. Flag any markets with high frequency + declining ROAS as potential saturation.

#### 6.2 Campaign-Level Performance

From `account_summary.json → spend_distribution_30d.by_campaign`:

For each campaign with delivery, show: **campaign type (ASC/Catalogue/ABO/CBO)**, spend, spend %, impressions, reach, frequency, CPM, ROAS, CPP, unique outbound CTR.

Flag top performers and underperformers with clear reasoning.

**Benchmarks:**
- **Unique outbound CTR:** <0.8% is concerning
- **Frequency (30d):** >3.0 on prospecting = concern
- **ROAS:** Compare against account average and flag campaigns significantly below

#### 6.3 Trend Analysis

Read `daily_account_trends.json` and `daily_campaign_trends.json`.

Describe these trends:
- Daily spend — stable, increasing, or declining?
- Daily ROAS — trending up, down, or volatile?
- Daily CPM — increasing CPMs suggest saturation
- Daily frequency — creeping frequency is the clearest saturation signal
- **Daily CPMr** — calculate CPM × frequency per day. Rising CPMr = saturation proxy

**Key patterns:**
- **Spend up, ROAS down** → Diminishing returns, hitting scale ceiling
- **CPM up, frequency up** → Audience saturation — expand targeting or refresh creative
- **Spend stable, ROAS volatile** → Unstable, possibly too few conversions for stable learning
- **CPMr rising** → Paying more per marginal new impression — primary reach constraint

#### 6.4 Attribution Window Analysis

Read `attribution_comparison.json`.

Compare total conversions and ROAS under each window:
- **7d_click** — Strictest. What % of conversions survive?
- **7d_click + 1d_view** — Standard. How many view-through conversions added?
- **1d_view** — View-only. How reliant on view-through?

If 7DC and 7DC1DV very similar → 7DC is solid choice.
If 7DC1DV significantly higher → Lots of view-through, may inflate results.

#### 6.5 Landing Page Performance

Read `landing_pages_aggregated.json`.

| Landing Page | Ads | Spend | Spend % | CPM | Purchases | CPP | ROAS |
|---|---|---|---|---|---|---|---|
| [url] | [count] | [amount] | [%] | [cpm] | [count] | [cpp] | [roas] |

Flag misalignment between top-spend LPs and top-performing LPs.

#### 6.6 Testing → Scaling Pipeline

Assess whether a proper testing-to-scaling pipeline exists:
- ABO testing spend as % of total (benchmark: 10-30% for small)
- Number of active ad sets in ABO (proxy for test volume)
- Are ABO and ASC clearly separated as environments?
- Evidence of creative graduation (similar ad names appearing in both ABO and ASC campaigns)

---

### Part 6b: Account Change Log Analysis

Read `activity_log.json`. This file contains the account's change history from the Meta Marketing API for the performance window — every ad status change, budget adjustment, creative upload, targeting tweak, and new entity creation.

**Purpose:** Understand how actively and effectively the account is being managed, identify management gaps that correlate with performance dips, and assess whether the change cadence matches the spend level.

#### 6b.1 Management Cadence Overview

From `activity_log.json` → `total_activities`, `active_days`, `total_calendar_days`, `avg_changes_per_active_day`:

| Metric | Value |
|---|---|
| Total changes in period | [from data] |
| Active management days | [from data] / [total calendar days] |
| Average changes per active day | [from data] |
| Management coverage | [active_days / total_calendar_days as %] |

**Benchmarks by brand size:**
- **Small (<£100k/mo):** 3-4 active days per week minimum. Daily touch preferred.
- **Mid-Market (£100-500k/mo):** Daily or near-daily management expected. Gaps >3 days are a concern.
- **Large (>£500k/mo):** Daily management required. Any gap >2 days is a red flag.

Flag if management coverage is below the benchmark for the brand's tier.

#### 6b.2 Change Category Breakdown

From `activity_log.json` → `category_breakdown`:

| Category | Count | % of Total | What This Tells Us |
|---|---|---|---|
| Ad Status Changes (on/off) | [count] | [%] | Creative rotation activity — toggling ads on/off |
| Budget Adjustments | [count] | [%] | Budget reallocation frequency |
| Creative Changes | [count] | [%] | Image edits and additions — creative refresh rate |
| New Ads/Sets/Campaigns | [count] | [%] | New entity creation — production pipeline output |
| Targeting Changes | [count] | [%] | Audience/targeting iteration |
| Bid/Optimisation Changes | [count] | [%] | Bid strategy and objective changes |
| Naming/Admin | [count] | [%] | Housekeeping and renaming |
| System Events | [count] | [%] | Automated — first delivery events, billing charges |

**Key signals:**
- **>70% status changes** = account is primarily rotating existing creative rather than building new. Check if new ad creation is keeping pace with the status churn.
- **<2% budget changes** = budgets may be left on autopilot too long. Mid-market accounts should be adjusting budgets at least weekly.
- **0% targeting changes** = targeting is static. May be fine if ASC is handling targeting algorithmically, but flag if ABO campaigns also have no targeting iteration.

#### 6b.3 Daily Activity vs Performance Correlation

Cross-reference `activity_log.json` → `daily_activity` with `daily_account_trends.json` to show changes alongside spend and ROAS for each day.

| Date | Changes | Spend | ROAS | Notable Activity |
|---|---|---|---|---|
| [date] | [count] | [amount] | [roas] | [describe: +N ads, budget Δ, creative Δ, etc.] |

**Patterns to look for:**
- **Changes followed by ROAS improvement** = management is effective, changes are well-timed
- **Changes followed by ROAS decline** = changes may be disrupting learning phase or introducing weak creative
- **Long gaps with declining ROAS** = under-management, performance issues going unaddressed
- **Heavy change days with volatile ROAS** = too many changes at once can reset Meta's optimisation

Group contiguous days with zero changes into summary rows (e.g. "15-23 Feb: 0 changes, ROAS 1.63-2.10") to keep the table scannable.

#### 6b.4 Management Gaps

From `activity_log.json` → `management_gaps`:

List all gaps of 3+ consecutive days with zero changes. For each gap, note:
- Gap duration
- Performance during the gap (pull from daily_account_trends)
- Whether performance deteriorated during the gap

**Critical threshold:** For Mid-Market and above, any gap >5 days should be flagged as a risk. For Small brands, gaps >7 days.

#### 6b.5 Day-of-Week Pattern

From `activity_log.json` → `day_of_week_distribution`:

| Day | Changes | % of Total |
|---|---|---|
| Monday | [count] | [%] |
| Tuesday | [count] | [%] |
| ... | ... | ... |
| Sunday | [count] | [%] |

Flag if weekends have zero activity — for accounts spending £1k+/day, weekend monitoring matters.
Flag if activity is heavily concentrated on 1-2 days — indicates batch management rather than continuous optimisation.

#### 6b.6 Key Change Events Reconstruction

Using the daily activity patterns (burst days, new ad creation dates, budget change clusters), reconstruct a narrative of what likely happened during the period:

For each significant activity day (>50 changes or notable event mix), describe:
1. **What happened** — types and volume of changes
2. **Likely purpose** — creative rotation, campaign launch, budget reallocation, promotional setup
3. **Performance impact** — did ROAS improve, decline, or stay flat in the 1-2 days following?

This gives the growth strategist a clear picture of the previous media buyer's management rhythm and decision-making patterns.

#### 6b.7 Change Log Assessment

Summarise with two columns:
- **What's Working** — positive management patterns (e.g. active creative rotation, deliberate budget reallocation, changes correlating with performance improvement)
- **What Needs Attention** — gaps, irregular cadence, missing change types, reactive rather than proactive management

End with an overall assessment of management maturity for this spend level.

**Assign RAG:**
- 🟢 Daily/near-daily touch, changes correlate with performance improvement, balanced change categories
- 🟡 Active management but irregular cadence (burst pattern), some long gaps, limited change category diversity
- 🔴 Infrequent management, gaps >7 days, changes don't correlate with performance improvement, single change category dominance

---

### Part 7: Distribution Opportunities

List up to 10 suggested opportunities based on the analysis. **Do NOT ICE-score these.** The growth strategist and media buyer will rank them by ICE themselves.

For each opportunity, provide:
1. **Clear description** of the opportunity
2. **Supporting data point(s)** from the audit
3. **Impact category:** Quick Win / Medium-Term / Strategic

Example format:
```
1. **Consolidate dormant campaigns** — 367 active campaigns have no delivery in 90 days. Archiving these reduces noise and simplifies account management. [Quick Win]

2. **Switch ATC optimisation to Purchase** — £12,400/mo (29%) of spend optimising for Add to Cart instead of Purchase. Per framework, purchase optimisation should be primary at this spend level. ATC is hemorrhaging cash without conversion intent. [Quick Win]

3. **Introduce founder identity** — 100% of ads run through brand page. Adding a founder identity could unlock new audience pools and improve incremental reach. [Medium-Term]

4. **Configure Audience Segments** — Audience Segments not set up in Ads Manager. Defining New/Engaged/Existing customer definitions enables proper acquisition tracking and segment-level ROAS analysis. [Quick Win]
```

---

### Distribution Thesis

End with a 2-3 sentence thesis summarising the binding constraint in distribution and the primary lever to unlock it. This feeds directly into the Growth Compass.

---

## Output Format

Structure your analysis as a report with these sections matching the Worksheet:

```
# Distribution Audit: [Account Name]
## Date: [date] | Brand Size: [tier] | Performance Window: [X]d

## Executive Summary
[2-3 sentences: overall distribution health, the #1 finding, primary recommendation]

## Part 1: Account Structure Assessment
[Brand size, budget allocation (ASC/Catalogue/ABO/CBO), campaign volume, naming conventions, optimisation objectives, non-conversion flags, critical config checklist]

## Part 2: Reach & Audience Health
[Frequency, CPMr, saturation diagnosis, per-campaign frequency, audience segment health]

## Part 3: Partnership Ads & Identity Diversification
[5-type identity inventory, identity performance table, diversification opportunity]

## Part 4: Media Mix & Channel Distribution
[Note: Meta-only. Flag for manual completion]

## Part 5: Technical Infrastructure
[Attribution, existing customer caps, exclusion coverage, audience segments config, URL tracking, manual verification flags]

## Part 6: Performance Snapshot
[Market-level (if multi-market), campaign-level with campaign types, trends, attribution windows, landing pages, testing pipeline]

## Part 6b: Account Change Log Analysis
[Management cadence, change categories, daily activity vs performance correlation, management gaps, day-of-week pattern, key change events reconstruction, assessment]

## Part 7: Distribution Opportunities
[Up to 10 opportunities, no ICE scoring, with supporting data and impact category]

## Distribution Thesis
[2-3 sentence thesis for the Growth Compass]
```

Use 🔴🟡🟢 RAG ratings throughout. Be specific with numbers — don't hedge.
Every finding should have a "so what" — what does it mean and what should we do about it.
Section overall RAG ratings should be provided at the end of each Part.
