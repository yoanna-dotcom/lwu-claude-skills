---
name: Creative Demand Forecast
version: 1.5
description: Pulls live Meta ad data across four 90-day windows, computes the five LWU creative health metrics, calculates monthly production volume needed to hit a target spend level, and delivers a clear SUFFICIENT / BORDERLINE / INSUFFICIENT verdict. Outputs a formatted .docx report that can be opened directly in Google Docs.
author: Launch With Us
tools_required:
  - meta_mcp
  - docx_skill
trigger: "Run the creative demand forecast for [client name]"
changelog:
  v1.5: "Rewrote input collection to match meta-creative-analysis conversational flow. Step-by-step questions using ask_user_input_v0, with sensible defaults surfaced at each step. Confirmation screen before data pull."
  v1.4: "Replaced Notion page output with a .docx file (Google Docs compatible)."
  v1.3: "Added creative_id-based deduplication. Replaced single test tax with three-bucket split. Added 60-day spend roadmap."
---

# Creative Demand Forecast Skill
# Launch With Us — v1.5 — April 2026

## WHAT THIS SKILL DOES

Pulls live Meta ad account data, computes the five creative health metrics, and answers one primary question: **is this account producing enough creative to meet demand?** It delivers a clear verdict (SUFFICIENT / BORDERLINE / INSUFFICIENT), shows what spend level current production can sustain, calculates what it would take to hit the target, and outputs a formatted .docx report the user can open directly in Google Docs or share with clients.

The distinction between **ads** and **concepts** is maintained throughout. An ad is a single deployed unit. A concept is the underlying creative idea — one concept typically spawns multiple ads via hook variants. Volume targets are expressed in both.

---

## USER FLOW

Collect inputs conversationally. Do not dump all questions at once. Move through each step in sequence, using `ask_user_input_v0` where options are involved. Confirm everything before pulling data.

---

### STEP 1 — CLIENT AND ACCOUNT

Ask for two things together — client name and account ID. These are always known upfront.

Ask:
> "Which client is this for, and what's their Meta Ad Account ID? (Format: act_XXXXXXXXXXXX)"

If the account ID is missing or malformed, prompt again before proceeding. Verify the account exists and has spend data before moving to Step 2.

---

### STEP 2 — WIN METRIC

Use `ask_user_input_v0` to ask:

> "How is this account measured — CAC or ROAS?"

Options:
- **CAC** — Target cost per acquisition (£)
- **ROAS** — Minimum return on ad spend (x)

After they select, ask for the specific threshold number:
- If CAC: "What's the target CAC in £?"
- If ROAS: "What's the minimum ROAS threshold?"

Do not mix CAC and ROAS in the same forecast. If the account uses both, ask which one should govern this run.

---

### STEP 3 — MINIMUM SPEND THRESHOLD

Use `ask_user_input_v0`:

> "What's the minimum spend an ad needs before it qualifies for the forecast? This filters out ads that haven't had enough budget to show real performance."

Options:
- **£100** — Recommended for low-spend accounts or tight CAC targets
- **£500** — Standard for most accounts
- **£1,000** — Conservative, ensures meaningful data
- **Custom** — I'll enter my own

If Custom is selected, ask for the value directly.

Default if they skip: £100.

---

### STEP 4 — TARGET MONTHLY SPEND

Ask directly (no options needed):

> "What monthly spend are we forecasting towards? This is the number we'll work backwards from."

Accept any £ figure. If they're unsure, suggest they think about it in terms of the next 90-day growth target, not where they are today.

---

### STEP 5 — CURRENT PRODUCTION

Use `ask_user_input_v0`:

> "How many new ads is the team launching per month? If you're not sure, I can estimate this from the account data."

Options:
- **I know the number** — I'll tell you
- **Estimate from the data** — Pull from ad naming conventions and created_time

If they know it: ask for the number of ads, then ask "And roughly how many of those are distinct concepts vs. hook variants of the same concept?" Accept a rough split or a single number.

If estimating from data: proceed — flag the estimate clearly in the output and ask them to verify.

Default `avg_hooks_per_concept`: 3. Always flag this assumption and invite correction — it materially affects concept count.

---

### STEP 6 — MAYBE ZONE BUFFER

Use `ask_user_input_v0`:

> "When we classify non-winning ads, I split them into three buckets: dead spend (clear losers), a 'maybe zone' (near-misses worth monitoring), and active testing (still learning). The maybe zone is defined as a % above your CAC threshold — so at £15 CAC and 20% buffer, ads with a £15–£18 CAC are 'maybes' rather than kills. What buffer should I use?"

Options:
- **10%** — Tighter margins, less tolerance for near-misses
- **20%** — Default, works for most accounts
- **30%** — More generous, flag more ads as worth watching
- **Custom** — I'll enter my own

Default: 20%.

---

### STEP 7 — CONFIRM BEFORE RUNNING

Before pulling any data, display a confirmation summary:

> "Here's what I'm about to run — confirm and I'll pull the data."

```
Client:              [Name]
Account:             act_XXXXXXXXXXXX
Win metric:          CAC / ROAS
Threshold:           £X / Xx
Min spend to qualify: £X
Target monthly spend: £X/month
Current production:  X ads/month (~X concepts/month) [estimated / confirmed]
Avg hooks/concept:   X [assumed / confirmed]
Maybe zone buffer:   X% (CAC/ROAS range: [value] to [value])
```

Use `ask_user_input_v0`:

Options:
- **Run it** — Pull the data
- **Change something** — Go back

If they want to change something, ask which input and loop back to the relevant step.

---

## DATA PULL — PULL META DATA

Once confirmed, pull ad-level insights for FOUR consecutive 90-day windows:

- Window 1: Last 90 days (most recent)
- Window 2: Days 91–180
- Window 3: Days 181–270
- Window 4: Days 271–360

For each window, pull at the **ad level** with these fields:
`ad_id, ad_name, creative_id, spend, purchase_roas, actions (purchases), impressions, created_time`

**Deduplication — always apply before any metric calculation:**

Group rows by `creative_id` first. If `creative_id` is unavailable, fall back to `ad_name`. Aggregate spend and purchases across all rows sharing the same key. Always report which method was used and how many instances were collapsed.

Always surface the deduplication report:
- Raw rows pulled per window
- Unique creatives after deduplication
- Instances collapsed
- Method used (creative_id or ad_name fallback)

**Other flags:**
- If the account has fewer than 90 days of data, flag that the forecast will be unreliable and ask whether to proceed.
- From `created_time` in Window 1, estimate how many unique creatives were launched in the last 30 days if production was not provided. Use creative_id grouping as primary; name patterns as fallback. Flag as estimated.

---

## ANALYSIS — COMPUTE THE FIVE HEALTH METRICS

All metrics computed on deduplicated creative-level data. Show working throughout.

### Metric 1: Win Rate

For each of the four windows:
1. Filter to creatives that have spent ≥ the minimum spend threshold
2. Of those, count how many hit the win threshold (CAC ≤ target OR ROAS ≥ threshold)
3. Win rate = winners ÷ qualifying creatives
4. Record for all four windows to show trend

**Healthy range: 10–25%**
- Below 10%: RED — creative strategy and/or post-click CVR is broken
- 10–15%: AMBER — below LWU standard, investigate
- 15–25%: GREEN — healthy
- Above 25%: NOTE — strong, but verify kill decisions aren't being made too late

### Metric 2: Winner Half-Life (Cohort Survival Method)

1. Take all creatives that qualified as winners in Window 1
2. Check which were also active (spending ≥ 10% of their Window 1 spend) in Window 2, Window 3, Window 4
3. Survival rate = count still active ÷ original cohort
4. Half-life = the point where survival crosses 50%. Interpolate between windows if needed.
5. If insufficient cohort data, estimate from average active lifespan and flag

**Healthy range: 30–90 days**
- Below 30 days: RED — severe fatigue, check distribution/frequency
- 30–60 days: AMBER — acceptable but watch trend
- 60–90 days: GREEN — solid
- Above 90 days: NOTE — strong longevity, check concentration risk

### Metric 3: Monthly Churn Rate

`monthly_churn = 1 − (0.5 ^ (30 ÷ half_life_days))`

**Healthy range: 25–50%**
- Below 25%: NOTE — verify winners aren't being kept alive artificially
- 25–40%: GREEN
- 40–55%: AMBER — production pipeline needs to be robust
- Above 55%: RED — fatigue is severe, investigate saturation

### Metric 4: Concentration Risk

1. Rank all Window 1 winners by spend, highest to lowest
2. Compute three tiers:
   - **Whales (top 10%)**: % of total winner spend, count, names of top 3
   - **Mid-tier (next 30%)**: % of total winner spend, count
   - **Foundation (bottom 60%)**: % of total winner spend, count
3. Identify the best segment — naming-convention group with highest win rate

**Healthy range: Whale concentration below 40%**
- Below 30%: GREEN
- 30–40%: AMBER — some concentration, monitor
- Above 40%: RED — account is fragile

### Metric 5: Test Tax (Three-Bucket Split)

**Define the maybe zone from the user-provided buffer (default 20%):**
- CAC account: maybe zone = win_threshold to win_threshold × (1 + buffer). E.g. £15 + 20% = £15.01–£18.00
- ROAS account: maybe zone = win_threshold × (1 − buffer) to win_threshold

**Three buckets — qualifying creatives only (≥ min spend):**

**Bucket 1 — Active Testing:**
Creatives below minimum spend. Still learning. Not waste — cost of process.

**Bucket 2 — Maybe Zone:**
Qualifying creatives whose performance falls within the buffer of the threshold. Near-misses. List by name. Do not kill yet.

**Bucket 3 — Dead Spend:**
Qualifying creatives clearly outside the maybe zone, or with zero purchases despite qualifying spend.
- **Dead spend % is the primary actionable number.**

| Bucket | Spend | % of total | Action |
|---|---|---|---|
| Active testing (below min spend) | £X | X% | Normal — cost of testing |
| Maybe zone (within [X]% of threshold) | £X | X% | Monitor — list creatives |
| Dead spend (clear losers) | £X | X% | Kill immediately — list creatives |

**Status thresholds apply to dead spend % only:**
- Below 5%: GREEN
- 5–15%: AMBER — review kill cadence
- Above 15%: RED — kill thresholds need tightening

---

## ANALYSIS — BOTTLENECK DIAGNOSTIC

Work through in order. Only move to the next if the current one is clear.

### Bottleneck 1: Creative Strategy
Win rate below 10%, OR declining across all four windows?
- If YES: "Run a Performance Creative Analysis before increasing production. Volume built on weak strategy burns budget faster."

### Bottleneck 2: Post-Click CVR
Win rate low but engagement metrics look healthy?
- If YES: "Audit the post-click experience before briefing more creative."

### Bottleneck 3: Kill Decisions
Dead spend % above 15% — losers running too long?
- If YES: "Implement a weekly kill review. Any creative at minimum spend with CAC > [threshold × (1 + buffer)] should be cut within 48 hours."
Active testing spend below 5% — killing too early?
- If YES: "Align on a minimum spend threshold of £[1–2x target CAC] before making kill decisions."

### Bottleneck 4: Saturation
Win rate and strategy healthy, but half-life below 30 days?
- If YES: "Audience architecture review before adding more creative volume. More creative won't fix a frequency problem."

### Bottleneck 5: Pure Velocity
Win rate ≥ 15%, half-life ≥ 30 days, no other bottleneck — but production is below 75% of `new_ads_needed`?
- If YES: "Volume is the binding constraint. Production throughput needs to increase."
- Note: This is the only bottleneck that maps to a production increase recommendation.

---

## ANALYSIS — VOLUME CALCULATION

**Inputs:**
- `current_winners` = Window 1 winners (deduplicated)
- `avg_winner_spend` = total winner spend in Window 1 ÷ 90 × 30 ÷ current_winners (monthly)
- `monthly_churn` = from Step 3
- `win_rate` = Window 1 (most recent)
- `target_monthly_spend` = from user input
- `current_production_ads` = from user input or estimated
- `avg_hooks_per_concept` = from user input or default 3 (always flag if assumed)

**Calculations:**

Step A: `winners_needed = ceil(target_monthly_spend ÷ avg_winner_spend)`
Step B: `monthly_winner_loss = round(current_winners × monthly_churn)`
Step C: `net_new_winners_needed = max(0, winners_needed − (current_winners − monthly_winner_loss))`
Step D: `new_ads_needed = ceil(net_new_winners_needed ÷ win_rate)`
Step E: `new_concepts_needed = ceil(new_ads_needed ÷ avg_hooks_per_concept)`
Step F: `production_gap_ads = new_ads_needed − current_production_ads`
         `production_gap_concepts = new_concepts_needed − ceil(current_production_ads ÷ avg_hooks_per_concept)`
Step G: `current_sustained_winners = current_winners − monthly_winner_loss + (current_production_ads × win_rate)`
         `current_sustainable_spend = current_sustained_winners × avg_winner_spend`

---

## OUTPUT — VOLUME VERDICT

Compute before generating the .docx. Place at the top of the document.

**SUFFICIENT:**
`current_production_ads ≥ new_ads_needed`
Output: ✅ SUFFICIENT — current production meets demand at target spend of £[X]/month.

**BORDERLINE:**
`current_production_ads ≥ 0.8 × new_ads_needed`
Output: ⚠️ BORDERLINE — current production is within 20% of what's needed. A minor increase closes the gap.

**INSUFFICIENT:**
`current_production_ads < 0.8 × new_ads_needed`
Output: ❌ INSUFFICIENT — current production can sustain ~£[current_sustainable_spend]/month. Reaching £[target]/month requires [gap_ads] more ads ([gap_concepts] more concepts) per month.

If INSUFFICIENT with no other bottleneck: *"Volume is the binding constraint on growth for this account."*
If INSUFFICIENT with a non-velocity bottleneck: *"Volume is insufficient, but adding production before resolving [bottleneck] will burn budget without improving outcomes."*

---

## OUTPUT — SPEND UNLOCK TABLE

Five scenarios: current production, 25%, 50%, 100%, and 150% of `new_ads_needed`.

For each:
- `sustained_winners = current_winners − monthly_winner_loss + (scenario_ads × win_rate)`
- `sustainable_spend = sustained_winners × avg_winner_spend`
- `scenario_concepts = ceil(scenario_ads ÷ avg_hooks_per_concept)`

| Monthly new ads | Monthly concepts | New winners | Total winners | Sustainable spend |
|---|---|---|---|---|
| [current] | ... | ... | ... | £... ← current |
| [25% of needed] | ... | ... | ... | £... |
| [50% of needed] | ... | ... | ... | £... |
| [needed] | ... | ... | ... | £... ← target |
| [150% of needed] | ... | ... | ... | £... |

---

## OUTPUT — GENERATE .DOCX REPORT

Generate a formatted .docx using the docx skill. File name:
`[Client Name] — Creative Demand Forecast — [Month Year].docx`

Clean enough to share directly with a client or open in Google Docs without editing.

**Formatting rules:**
- Arial throughout, 12pt body, 14pt H2, 18pt H1
- A4, 1 inch margins
- Use proper docx tables — WidthType.DXA, dual widths (columnWidths + cell width), ShadingType.CLEAR
- Light grey (#F2F2F2) header rows on all tables
- Volume Verdict rendered as a visually distinct shaded callout box
- Status indicators: use GREEN / AMBER / RED in bold — no emoji (unreliable in docx)
- Page numbers in footer
- Client name + report title in header

**Document structure:**

1. **Cover block** — Client name, report title, date, account ID, win metric, threshold, buffer, target spend
2. **Volume Verdict** — Shaded callout, first substantive section, visually distinct
3. **Summary** — 2–3 sentences, plain English, client-facing tone, lead with verdict not metrics
4. **Deduplication Report** — Raw rows, unique creatives, instances collapsed, method used
5. **Creative Health Scorecard** — Table: Metric / Value / Trend / Status (GREEN/AMBER/RED) / Benchmark
6. **Test Tax Breakdown** — Three-bucket table with creative names listed in maybe zone and dead spend rows
7. **Winner Breakdown** — Whales / mid-tier / foundation tiers with spend % and top creative names
8. **Bottleneck Diagnostic** — One sentence per bottleneck; specific recommendation for any triggered
9. **Volume Calculation** — Clean data block showing all inputs and outputs
10. **Spend Unlock Table** — Target row highlighted (bold + light blue fill)
11. **Trend Data (4-Window View)** — Table: Window / Period / Qualifying creatives / Winners / Win rate / Avg winner spend/mo
12. **60-Day Spend Roadmap** — Three phases (see below). Mandatory for INSUFFICIENT verdict.
13. **Next Steps** — Maximum 4 numbered items, verdict-driven
14. **Footer** — Generated by LWU Creative Demand Forecast Skill v1.5 | [Date] | Deduplication: [method] | Buffer: [X]%

**60-Day Spend Roadmap — always three phases for INSUFFICIENT verdicts:**

Phase 1 — Immediate (Days 1–14): Free up budget before adding volume.
List dead spend creatives to cut. Calculate budget freed. Estimate resulting spend lift from concentrating behind existing winners only.

Phase 2 — Month 1 (Days 15–45): Scale proven concepts, not new ones.
Identify top concept families from Winner Breakdown. Brief hook variants, not new concepts. State: target ad count, expected new winners at current win rate, monthly spend milestone.

Phase 3 — Month 2 (Days 45–60): Introduce one new concept category.
Based on best segment from Winner Breakdown, identify the most logical new angle. Single focused batch. State expected spend milestone.

Each phase must include: specific action, expected new winners, resulting estimated monthly spend.

---

## IMPORTANT NOTES FOR CLAUDE

- **The Volume Verdict is the primary output.** It must appear at the top of the document before any metrics or calculations.
- **Never present the production gap number without the Spend Unlock Table.** The gap in isolation is not actionable.
- **Always express volume in both ads AND concepts.** The client needs to see both.
- **Lead with spend, not volume.** The verdict frames the spend implication; the volume numbers explain how to get there.
- **If win rate is below 8%, always recommend a Performance Creative Analysis before scaling production.**
- **The four windows are non-negotiable.** A single snapshot is interesting. A trend is actionable.
- **Deduplication is non-negotiable.** Use creative_id as primary key; fall back to ad_name only if unavailable. Always report which method was used.
- **Test tax is always three buckets.** Never report a single test tax %. Dead spend % is the headline number.
- **The maybe zone buffer is a named input, not a hardcoded assumption.** Default 20%, always confirm with user at Step 6 of the user flow.
- **Do not skip the bottleneck diagnostic** even if all metrics look healthy.
- **If INSUFFICIENT with a non-velocity bottleneck triggered, do NOT recommend increasing production as the primary action.** Resolve the bottleneck first.
- **`avg_hooks_per_concept` defaults to 3.** Always flag if assumed — it materially affects concept count.
- **The 60-day spend roadmap is mandatory for INSUFFICIENT verdicts.** The production gap is context. The roadmap is the deliverable. Sequenced: free up budget first, scale proven concepts second, introduce new concepts third. Always include spend milestones.
- **Output is a .docx file, not a Notion page.** Follow all docx skill rules: WidthType.DXA for tables, ShadingType.CLEAR for shading, LevelFormat.BULLET for lists, no unicode bullets, no \n in text runs, explicit page size. Present the file to the user for download once generated.
