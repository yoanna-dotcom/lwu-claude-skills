---
name: tiktok-organic-analysis
description: >
  Runs a full TikTok organic content analysis for any D2C brand. Browses live TikTok hashtag
  pages using Claude in Chrome to collect real video URLs, captions, and creator data across
  2–5 product categories. Uses Perplexity for trend intelligence when available. Delivers
  two outputs: (1) a professional dark-theme HTML report with clickable video links saved to
  the workspace folder, and (2) a structured Notion page created under a user-specified parent.

  Trigger whenever someone says: "run TikTok analysis", "TikTok organic research", "what's
  working on TikTok for [brand]", "social research TikTok", "TikTok content analysis",
  "organic TikTok strategy", "TikTok content playbook", "what should we post on TikTok",
  "what formats are going viral for [category]", or any request to understand organic TikTok
  trends, content strategy, or creator insights for a brand or product category.
---

# TikTok Organic Content Analysis Skill

## Overview

This skill produces a comprehensive TikTok organic content intelligence report for any brand.
It collects real, live data from TikTok — actual video URLs, creator handles, captions, and
engagement data — rather than relying on general knowledge. The output is actionable: a specific
content playbook the team can execute immediately.

**Two deliverables every time:**
1. HTML report → saved to the workspace outputs folder
2. Notion page → created under a parent page the user specifies

---

## Step 1: Gather Inputs

Use AskUserQuestion to collect everything needed before starting work. Ask in a single round:

- **Brand name** — e.g. "Layered Lounge", "Carbeth Plants"
- **Product categories** — 2 to 5 categories to analyse (e.g. "Rattan & Storage, Tableware & Dining, Linen & Bedding")
- **Notion parent page URL** — where to create the new Notion page
- **Focus market** — UK, US, or global (default: UK)

If the user has already provided any of these in their message, don't ask again — extract them from context.

---

## Step 2: Plan Hashtags Per Category

Before browsing TikTok, determine the primary hashtag(s) to target for each category. Use your
knowledge of TikTok to pick 2–3 hashtags per category that are likely to have strong home decor /
lifestyle content. Think about:
- The category name as a hashtag (e.g. #tableware, #linenbedding)
- Related discovery hashtags (#homedecor, #homeinspo, #tiktokmademebuyit)
- UK-specific variants if market is UK (#ukhosting, #ukhomedecor)

Document your chosen hashtags — these become part of the report's Hashtag Landscape section.

---

## Step 3: Browse TikTok With Chrome

This is the core data collection step. For each category:

### 3a. Navigate to the hashtag page
Use the `navigate` tool to go to: `https://www.tiktok.com/tag/[hashtag]`
Wait 4 seconds for the page to load. Take a screenshot to confirm it loaded.

### 3b. Extract video URLs
Use the `javascript_tool` to extract all video links from the page:
```javascript
const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
const urls = [...new Set(links.map(a => a.href))].filter(h => h.includes('/video/'));
JSON.stringify({ title: document.title, count: urls.length, urls: urls.slice(0, 20) })
```
Also note the post count shown on the hashtag page (e.g. "104.1K posts") and any visible
caption snippets on the grid.

Scroll down once and re-run to capture more videos if needed. Aim for 15–20 URLs per category.

### 3c. Scroll to capture caption previews
While on the hashtag page, take a screenshot — the grid shows creator handles and caption
previews which are valuable data even before visiting individual videos.

### 3d. Visit top videos for metadata
Visit the top 3–5 video URLs individually. For each:
- Wait 4 seconds for the page to fully load
- Extract the page title (= the video title/caption):
```javascript
JSON.stringify({ title: document.title, counts: Array.from(document.querySelectorAll('strong')).map(el => el.innerText).filter(t => t && /[\d\.KkMm]/.test(t)).slice(0, 6) })
```
- The `counts` array returns [likes, comments, saves, shares] in that order
- Take a screenshot if the video thumbnail is informative

**Important:** Individual video pages can take 8–12 seconds to fully render. If `counts` returns
empty, wait 3 more seconds and retry. If a video is geo-blocked or unavailable, skip it.

### 3e. Move to the next category
Navigate to the next hashtag page and repeat. Don't go back to previous categories once you've
moved on — collect all data in a single forward pass.

### What to record for each category:
- Hashtag page post count
- 10–20 video URLs (for linking in report)
- Creator handles seen in the grid
- Caption previews from the grid and visited videos
- Engagement data (likes/saves/shares) for visited videos
- Any notable patterns observed (aesthetic styles, recurring hooks, common formats)

---

## Step 4: Perplexity Trend Research (if available)

After collecting Chrome data, run Perplexity research to enrich the analysis. This adds
intelligence about trending formats, audio, and hook patterns that may not be visible from
the handful of videos browsed.

For each category, run a `perplexity_ask` query (use `search_context_size: "high"`):

> "Analyse the most viral TikTok content in 2024–2025 for [category] in [market]. I need:
> 1) What specific video formats go viral? 2) What hooks grab attention in the first 3 seconds?
> 3) What aesthetic styles dominate? 4) What sounds/music are trending? 5) What do comment
> sections reveal about purchase intent? Give specific creator handle examples where possible."

**If Perplexity returns a quota error:** Skip this step gracefully. The Chrome data plus
your knowledge of TikTok trends is sufficient for a strong report. Do not mention the error
to the user — simply proceed with what you have.

Run all category queries in parallel (same message) to save time.

---

## Step 5: Synthesise Findings

Before building the report, compile your findings into a structured mental model for each category:

**Per category:**
- Hashtag landscape (post counts + which tags are high/medium/low volume)
- Top 3–5 content formats (ranked by how often they appear in viral content)
- 5–7 hook examples (real hooks observed or patterns that work in this category)
- 6+ real video examples with creator handle, caption, engagement stats, and URL
- Creator recommendations (5–8 handles worth following/approaching for collabs)
- Audio trends (2–4 trending sounds or music styles)
- 1 strategic insight specific to the brand's opportunity in this category

**Cross-category:**
- 4–6 universal patterns appearing across all categories
- A performance matrix (format → goal → metric → category fit)
- An overall strategic opportunity statement for the brand

**Playbook:**
- A content mix framework (types of posts, cadence)
- 4–5 specific content ideas with hooks, production notes, hashtags
- A 90-day roadmap (Month 1: Foundation → Month 2: Amplify → Month 3: Systematise)

---

## Step 6: Build the HTML Report

Create the HTML report and save it to:
`/sessions/.../mnt/[workspace-folder]/outputs/[Brand-Name]-TikTok-Organic-Analysis.html`

(Use the actual workspace path from the environment — check where other outputs have been saved.)

### Design system (use these consistently):

```css
/* Core palette */
--bg-primary: #0d0d0d
--bg-card: #1a1a1a
--border: #2a2a2a
--text-primary: #f0ebe3
--text-secondary: #9a9080
--text-muted: #5a5248
--accent-gold: #c9a96e
--accent-gold-light: #e8c896

/* Category accent colours — assign one per category */
Warm/earthy categories: #c9a96e (gold)
Dining/tableware: #b8a8d8 (lavender)
Soft/bedding: #8aab8a (sage)
Bold/industrial: #7a9aaa (slate)
Fresh/garden: #d4867a (rose)
```

### Report structure (6 sections, required):

**Section 1 — Header**
- Brand name + "TikTok Organic Content Analysis" title
- Subtitle with date, category count, market focus
- 4 key stat cards (post counts, key metrics)
- Sticky navigation bar with section links

**Section 2 — Executive Summary**
- 4 stat cards (biggest hashtag volumes)
- "The big unlock" callout (the #1 strategic insight for this brand on TikTok)
- 3-column mini-insight cards (one per category)
- Universal patterns table (pattern → why it works → brand application → priority)

**Section 3–N — Per Category Deep Dive** (one section per category)
Each category section must include:
- Category hero block with coloured background matching that category's accent
- Hashtag landscape (code-styled tags, annotated with 🔴/🟡/⬜ heat level)
- Top content formats (table or pill tags + performance bars)
- Hook examples (left-bordered quote cards with italic text)
- Real video examples (clickable card grid — each card is an `<a>` tag pointing to the TikTok URL)
  - Cards show: creator handle, caption, engagement stats, "▶ Watch on TikTok ↗" label
- Key creators table (handle, content type, UK flag)
- Audio trends
- Strategic opportunity callout

**Section N+1 — Cross-Category Patterns**
- 4 stat cards
- Universal mechanics (table or 2-column insight cards)
- Content performance matrix table

**Section N+2 — Brand Playbook**
- Warning callout with starting context
- Content mix table (type, frequency, description)
- Priority content ideas (each as a numbered opportunity card with: tag, title, description, production notes)
- 90-day roadmap table
- Closing "biggest unlock" callout

### Video card requirement (critical):
Every video card in the report MUST be an `<a>` tag with `href` pointing to the real TikTok URL,
`target="_blank"`, and `rel="noopener"`. Include a "▶ Watch on TikTok ↗" label that shows on hover.
This is the feature that makes the report actionable — links must work.

### For categories where you visited videos individually:
Use the real engagement numbers you collected (e.g. "1.7K likes · 419 saves").

### For videos you only have the URL for (didn't visit individually):
Show "Est. [X]K+ likes" based on the category's typical engagement range.

Read `references/html-template-guide.md` for the complete CSS design system and component patterns.

---

## Step 7: Create the Notion Page

Create a Notion page under the parent URL the user specified.

**Page title:** `[Brand Name] — TikTok Organic Content Analysis`
**Icon:** 🎵

Use this Notion content structure (enhanced markdown format):

```
<callout icon="🎵" color="gray_bg">
[Brand] TikTok Organic Content Analysis · [Date] · [Market] focus
[One-line description of what the report covers and why it matters]
</callout>

---

# 01 — Executive Summary
[4-column stat callouts in gray_bg]
[Strategic insight callout]
[Universal patterns table]

---

# 02 — [Category Name]
<callout icon="[emoji]" color="gray_bg">[Category strategic framing]</callout>

### Hashtag Landscape
[Inline code hashtags + heat legend]

### Top Content Formats
[Table: Format | Performance Signal]

### Hook Examples — What Stops the Scroll
[Quote blocks for each hook]

### Real Video Examples
[Table: Creator | Caption | Stats | Link — all links must be [Watch ↗](url)]

### Key Creators to Collaborate With
[Table: Handle | Content Type | UK?]

### Audio Trends
[Table: Audio Style | Best For]

<callout icon="🎯" color="gray_bg">[Strategic opportunity for this category]</callout>

---
[Repeat for each category]

# [N+1] — Cross-Category Patterns
[Stats table]
[Universal mechanics table]
[Performance matrix table]

# [N+2] — [Brand] TikTok Playbook
[Warning callout]
[Content mix table]
[Priority ideas as <details> toggle blocks]
[90-day roadmap table]
<callout icon="🚀" color="gray_bg">[Closing strategic statement]</callout>
```

**Key rules for Notion:**
- All video links must appear as `[Watch ↗](https://tiktok.com/...)` inside tables
- Use `>` (quote blocks) for hook examples — not bullet points
- Use `<details><summary>` for the playbook content ideas (collapsible)
- Use `<callout color="gray_bg">` for strategic insights
- Use `---` (divider) between every major section

---

## Step 8: Deliver to User

Share both outputs:

1. Link to HTML file: `[View TikTok Organic Analysis](computer:///path/to/file.html)`
2. Link to Notion page: `[Open in Notion](https://notion.so/...)`

Then give a 3-sentence executive summary: what the #1 opportunity is for this brand on TikTok,
which category has the most immediate potential, and the single first piece of content to make.

Do not repeat the full report — the user can open it. Keep the response brief.

---

## Troubleshooting

**TikTok page doesn't load (blank/loading state):**
Wait an additional 3–5 seconds and retry the JavaScript extraction. If still blank, try
the next hashtag in your list for that category. TikTok loads slowly but usually resolves.

**`get_page_text` fails on TikTok:**
Expected — TikTok's DOM is JS-heavy and the text extractor won't work. Always use
`javascript_tool` + `computer` screenshot instead.

**Video counts array returns empty:**
The page hasn't rendered yet. Wait 3 more seconds and retry. If still empty after retry,
note the video from the page title alone and move on.

**No Chrome tab available:**
Check available tabs first. If TikTok is already open in an existing tab, use that tab ID.
If no browser tab is available, skip Chrome browsing and rely on Perplexity + knowledge-based
analysis, making clear in the report that video examples are illustrative rather than live-browsed.

**Perplexity quota exceeded:**
Silently skip Perplexity. Proceed with Chrome data and knowledge. The report will still
be high quality — just note it in your own process, not in the report.

**Notion creation fails:**
If the parent page ID can't be resolved, ask the user to share just the page ID (the
alphanumeric part at the end of the Notion URL) and retry.
