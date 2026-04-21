---
name: creative-library-builder
description: >
  Imports ads from a Foreplay board into LWU's Notion creative library. For each ad,
  downloads the creative asset, sends to Gemini for classification against the 56 LWU
  frameworks, and uploads the result (image + Gemini analysis) to the matching
  framework subpage in Notion. Use this skill when someone wants to populate the
  creative library from Foreplay boards, import Foreplay saved ads to Notion, or
  build creative references for the open-brief-builder skill. Also trigger on
  "add foreplay board to library", "import ads from foreplay", "populate creative library".
---

# Creative Library Builder

## What This Skill Does

1. Reads one Foreplay board → pulls its ads via the Foreplay API
2. Downloads each ad's image/video/thumbnail
3. Sends each to Gemini → classified against LWU's 56 framework taxonomy
4. Uploads image + Gemini analysis to the matching Notion framework subpage

**Output:** Creative references live inside their correct framework subpage in Notion
(Frameworks DB: `https://www.notion.so/launchwithus/32af64437f9b8009913cc59c058d66a7`).

**Runtime:** ~30-60 sec per ad. A 10-ad board = ~10 min end-to-end.

**Cost:** 1 Foreplay credit per ad pulled. Hard cap defaults to 1,500 credits.

## How to Run

### Step 0 — Smoke Test (do this the first time only)

Before pulling any real boards, confirm auth works:

```bash
python3 {SKILL_DIR}/scripts/build_library.py --test-auth
```

Expected output: `✅ Foreplay auth works` + credits remaining.

If this fails, fix `~/.claude/api_keys.json` `foreplay_api_key` value before continuing.

### Step 1 — Cache the Frameworks from Notion

The script needs a local JSON file listing all 56 frameworks (name + category) so Gemini
can classify against them. Use Notion MCP to fetch the Frameworks DB data source, then
write this file:

**File path:** `{SKILL_DIR}/frameworks_cache.json`

**Format:**
```json
[
  {"name": "Before/After", "category": "Results & Transformation", "page_id": "abc123..."},
  {"name": "5-Star Review Stack", "category": "Social Proof & Testimonials", "page_id": "def456..."},
  ...
]
```

Fetch the data source at `collection://32af6443-7f9b-8070-946c-000ba25b8285` and iterate
every page. Store each page's title, Category multi-select values, and page ID. The `page_id`
is critical — it's how we upload examples to the right subpage in Step 4.

Cache only needs to be refreshed when the user adds/renames frameworks in Notion.

### Step 2 — List Boards (optional helper)

If the user doesn't know their board IDs, run:

```bash
python3 {SKILL_DIR}/scripts/build_library.py --list-boards
```

Returns all boards with IDs + names. Costs no credits beyond the initial auth check.

### Step 3 — Ask the User

Use AskUserQuestion:
1. **Which board(s)?** — board ID or URL (can batch multiple)
2. **Limit per board?** — smoke test = 5, first real batch = 10-30, full pull = 100+
3. **Board hint for Gemini?** — what framework/angle does this board represent? Used as
   a hint in the classification prompt (e.g., "Social Proof — Testimonials").
   Leave blank if the board is a mixed grab-bag.

**Important:** remind the user of credit cost. `N ads = N Foreplay credits` on top of
Gemini token spend.

### Step 4 — Run the Import

```bash
python3 {SKILL_DIR}/scripts/build_library.py \
  --board-id <id> \
  --board-hint "<optional category hint>" \
  --limit <N> \
  --frameworks {SKILL_DIR}/frameworks_cache.json \
  --output /tmp/creative-library/<board-slug>/import.json \
  --credit-cap 1500
```

**IMPORTANT:** Use `timeout=600000` (10 min) on the Bash call for boards >20 ads.

**Output:** `import.json` with a `results` array. Each entry contains:
- `ad_id`, `ad_name`, `headline`, `description`, `cta_title`, `link_url`
- `asset_url` (original Foreplay URL), `asset_local_path` (downloaded file)
- `classification.framework_match` — the framework name Gemini chose
- `classification.confidence` — high/medium/low
- `classification.angle`, `classification.hook_type`, `classification.production_style`
- `classification.summary` — Gemini's paragraph explaining the match
- `foreplay_ad_url` — link back to the ad in Foreplay

### Step 5 — Review Before Uploading (CRITICAL for first run)

**Do NOT skip on the first smoke test.** Read the JSON and present the user with a summary:

```
Smoke test complete: 5/5 ads classified.

Results:
1. [Ad name] → matched "Before/After" (confidence: high)
2. [Ad name] → matched "5-Star Review Stack" (confidence: medium)
3. ...

Credits used: 5. Credits remaining: 19,995.

Proceed with Notion uploads?
```

If confidence is low on most ads, or classifications look wrong, STOP. Tune the Gemini
prompt before burning credits at scale.

### Step 6 — Upload to Notion via MCP

For each entry in `results`:

1. **Find the target page.** Match `classification.framework_match` against
   `frameworks_cache.json` to get the `page_id`.

2. **Append a block to the framework subpage** with:
   - Divider
   - Heading 3: `📎 {ad_name}` (or first 50 chars of headline)
   - Image block: embed `asset_url` (Foreplay's CDN URL — works directly, no re-upload needed)
   - Paragraph: Gemini's `summary`
   - Bullet list:
     - `Angle: {classification.angle}`
     - `Hook Type: {classification.hook_type}`
     - `Production: {classification.production_style}`
     - `Source: Foreplay — {source_board_hint}`
   - Link: `View in Foreplay: {foreplay_ad_url}`

3. Use `notion-update-page` or the equivalent MCP tool to append these blocks.

4. Log each successful upload.

### Step 7 — Report Back

Tell the user:
- How many creatives got uploaded (and to which frameworks)
- Which frameworks now have examples
- Total credits used (Foreplay + approximate Gemini)
- Path to the `import.json` for future reference
- Link to 2-3 framework subpages so they can review

## Cost Management

| Scenario | Foreplay credits | Notes |
|----------|------------------|-------|
| Smoke test (5 ads) | 5 | Always run first on new boards |
| Single board (30 ads) | 30 | First real batch |
| Full client library (10 boards × 30 ads) | 300 | Spread across sessions |
| Cap per single run | 1,500 (`--credit-cap`) | Hard stop, configurable |

Credits remaining is logged on every Foreplay response. Surface it to the user after each run.

## Known Limitations

- **Video classification is slower.** Gemini processes videos in 30-60 sec vs 5-10 sec
  for images. For first passes, the script prefers image/thumbnail over video to stay fast.
- **Confidence ≠ correctness.** Gemini is confident and wrong sometimes. Spot-check the
  first batch before scaling.
- **Foreplay CDN URLs may expire** — worth testing. If embedded images stop rendering in
  Notion after days/weeks, we'll need to re-host. First version assumes they're stable.
- **No duplicate detection yet.** If the same ad is in two boards, it'll get uploaded twice.
  Future: compare `ad_id` against existing library entries before uploading.

## When NOT to use this skill

- For your own clients' winning ads — use the Meta API directly (separate skill to build).
- When the user wants to classify a single ad from a URL — overkill for single asset.
- When the Frameworks DB has been restructured — refresh `frameworks_cache.json` first.
