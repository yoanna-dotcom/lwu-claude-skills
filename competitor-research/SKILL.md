---
name: competitor-research
description: >
  Generic D2C competitor research skill. Researches named competitors for any brand, maps
  their messaging, strengths, weaknesses, and gaps against the client's confirmed USPs,
  identifies creative whitespace, and outputs COMPETITOR-BRIEF.md for the
  strategic-brief-builder. Trigger on: "competitor research", "analyse competitors",
  "what are competitors doing", "find whitespace", "competitor gaps", or when
  BRAND-INTELLIGENCE.md exists but COMPETITOR-BRIEF.md does not.
---

# Competitor Research

> **Note:** This is a research-heavy skill — multiple competitors x multiple sources.
> Expect significant web searching. `[client-folder]` = the current working directory.

This skill produces the competitive intelligence layer that the strategic-brief-builder uses
to define whitespace, differentiation angles, and hook territory. It runs after brand research
and persona research are complete.

**[PRODUCT]** throughout this document = the client's primary product category, pulled from
BRAND-INTELLIGENCE.md. Never hardcode a product name — always read it from the handover doc.

---

## Step 0 — Read handover documents (mandatory — do not skip)

Read in parallel:
- `[client-folder]/BRAND-INTELLIGENCE.md`
- `[client-folder]/PERSONA-STRATEGY.md`

If BRAND-INTELLIGENCE.md does not exist: stop and ask for it. Do not run competitor research
without confirmed USPs to test against.

Extract and hold in context:
- **[PRODUCT]** — the primary product category being sold
- **Competitor names** — from "Competitors (confirmed)" section of BRAND-INTELLIGENCE.md
- **Confirmed USPs** — only Proven USPs. These are what you're testing competitor ownership of.
- **Top pain points** — look for these as failure patterns in competitor reviews
- **Language to avoid** — so competitor research doesn't surface angles already ruled out
- **Persona descriptions** — to understand what the target audience is comparing the brand against

---

## Step 1 — Scrape all competitors (Sonnet subagents)

**Do NOT run web scraping in the main conversation.** Launch one Sonnet subagent per competitor
using the Agent tool (`model: "sonnet"`). Run them in parallel. This keeps raw web content out
of the Opus context and uses Sonnet's separate rate limits.

**Maximum 3 competitors.** If more than 3 are listed in BRAND-INTELLIGENCE.md, pick the 3
most relevant based on: (1) direct product overlap with client, (2) mentioned in client
reviews as alternatives, (3) strongest Meta ad presence. Note which competitors were skipped
and why.

**Per-competitor subagent prompt — include all of the following:**

> You are researching a competitor brand for a D2C creative strategy team.
> Scrape all sources and return ONLY structured extracted data.
>
> **Competitor: [competitor name]**
> **Domain: [competitor URL]**
> **Client brand for comparison: [client brand name]**
> **Product category: [PRODUCT]**
>
> **Scrape these pages (use WebFetch):**
> - Homepage — extract: hero copy, positioning statement, primary claims
> - Top 2 bestseller product pages — extract: features emphasised, how they describe [PRODUCT]
> - /about or /our-story — extract: brand positioning, differentiation claims
>
> **Scrape review sources:**
> - TrustPilot: `trustpilot.com/review/[competitor-domain]` — extract: rating, count, 10+ verbatim reviews (prioritise complaints and comparisons)
> - On-site product reviews (from bestseller pages) — extract: verbatim reviews
>
> **Scrape pricing (from bestseller pages + collection pages):**
> - Extract price range: cheapest product, most expensive product, bestseller price points
> - Note currency, whether prices include VAT, and any subscription/bundle pricing
> - Extract any visible discount mechanics (first order %, loyalty, bundles, sale frequency)
>
> **Scrape Meta Ad Library:**
> - Go to: `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=GB&q=[competitor name]`
> - Use WebFetch with prompt: "Extract the first 10-15 active ads. For each ad, extract: ad format (static/video/carousel), headline/primary text (first 2 lines), any visible CTA, and describe the visual creative briefly (what's shown in the image/thumbnail). Also note: total number of active ads shown, date range of oldest visible ad, and whether ads appear to target gifting/seasonal vs always-on."
> - If Meta Ad Library is blocked or returns no results, search: `"[competitor name] Facebook ads"` or `"[competitor name] Meta ads"` as fallback
>
> **Run these web searches (use WebSearch):**
> - `site:reddit.com "[competitor name]"` — extract: unprompted buyer comparisons and complaints (verbatim)
> - `"[competitor name] review"`
> - `"[competitor name] vs [client brand name]"`
>
> **Return format — use this exact structure:**
>
> ```
> COMPETITOR SCRAPE: [Competitor Name]
>
> ## Website
> Hero copy: ...
> Positioning: ...
> Primary claims: ...
> Product features emphasised: ...
> Differentiation claims: ...
>
> ## Pricing
> Price range: [lowest] - [highest]
> Bestseller price points: ...
> Currency: ... | VAT included: Y/N
> Discount mechanics: ...
> Bundle/subscription offers: ...
>
> ## Reviews
> TrustPilot: X/5 (N reviews)
> Verbatim reviews (prioritise complaints + comparisons):
> 1. "..."
> [all found]
>
> On-site reviews:
> 1. "..."
>
> ## Reddit mentions
> [verbatim quotes with subreddit + context]
>
> ## Meta Ad Library
> Total active ads: ...
> Oldest visible ad: ...
> Always-on vs seasonal: ...
> Top ads observed:
> 1. Format: ... | Headline: "..." | Visual: ... | CTA: ...
> 2. ...
> [up to 10-15]
>
> Ad patterns:
> - Dominant format: ...
> - Dominant hook type: ...
> - Messaging themes: ...
> - What's missing (formats/angles NOT used): ...
>
> ## Sources blocked or empty
> [list]
> ```

When all subagents return, proceed to Step 2 using their structured data. Do not re-scrape.

---

## Step 2 — Messaging, features & USP comparison

For each competitor, analyse in a single pass:

**Messaging overlap and divergence:**

| Claim / angle | Client uses it | Competitor uses it | Saturation risk |
|---|---|---|---|
| [claim] | Yes/No | Yes/No | High/Med/Low |

| What competitor says | What client says | Implication |
|---|---|---|
| [their angle] | [client angle] | [creative opportunity or conflict] |

**Pricing & value comparison:**

| Brand | Entry price | Bestseller price | Premium price | Discount mechanic | Value perception |
|---|---|---|---|---|---|
| [Client] | £X | £X | £X | [e.g. FAN 10% off] | [premium/mid/value] |
| Competitor A | £X | £X | £X | [e.g. 15% first order] | [premium/mid/value] |
| Competitor B | £X | £X | £X | [e.g. none] | [premium/mid/value] |
| Competitor C | £X | £X | £X | [e.g. sale events] | [premium/mid/value] |

**Pricing creative implications:**
- Where does the client sit vs competitors? (cheapest, mid, premium)
- Is price a creative asset or liability? (can they lead with value, or must they justify premium?)
- What pricing angles do competitors use in ads? (% off, free shipping, bundle, scarcity)
- **Recommendation:** one sentence on how price should/shouldn't feature in creative

**Tone comparison:** How does each competitor's tone differ from the client's? (formal/casual,
aspirational/functional, fear-led/desire-led). Where is the client's tone genuinely differentiated?

**Feature & USP comparison table:**

| Feature / USP | [Client brand] | Competitor A | Competitor B | Competitor C |
|---|---|---|---|---|
| [Feature] | ✅ confirmed | ✅ / ❌ | ✅ / ❌ | ✅ / ❌ |

- **Unique to client (no competitor has this confirmed):** strongest creative angles
- **Shared with 1 competitor:** available but not differentiating
- **Shared with 2+ competitors:** saturated, deprioritise in creative

**USP Whitespace Map:**

| USP | Competitor A owns it? | Competitor B owns it? | Competitor C owns it? | Whitespace? |
|---|---|---|---|---|
| [USP] | Yes/No + evidence | Yes/No + evidence | Yes/No + evidence | Clear / Contested / Saturated |

- **Clear:** client can own this in creative with no direct competition
- **Contested:** 1 competitor runs this angle — client can still win with better execution
- **Saturated:** 2+ competitors run this — only use if client has demonstrably better proof

---

## Step 3 — Gaps, differentiation & sentiment

Analyse each competitor's website, reviews, and ads to identify where [PRODUCT] has a
competitive advantage.

**Per competitor — strengths, weaknesses & sentiment:**

| Dimension | Strength | Weakness | Evidence |
|---|---|---|---|
| Product quality | | | "[verbatim]" |
| Messaging clarity | | | "[verbatim]" |
| Customer experience | | | "[verbatim]" |
| Creative angles used | | | [format + angle observed] |
| Price / value perception | | | "[verbatim]" |
| Audience fit | | | "[verbatim]" |

**Sentiment snapshot** (not trend analysis — point-in-time assessment):
- Overall sentiment: Positive / Mixed / Negative (with evidence)
- Dominant positive themes buyers mention
- Dominant negative themes — these signal unmet needs
- Emotional tone of complaints: frustrated / disappointed / betrayed / indifferent

**Cross-competitor pattern:** Is there a consistent emotional complaint across multiple
competitors? If yes — this is the most important creative insight. Name it explicitly.

**Gaps found (where their product/service falls short):**
- [Gap] — evidence: "[verbatim complaint from reviews/Reddit]"

**Opportunities for [PRODUCT] (where the gap maps to a confirmed client USP):**

| Competitor gap | Client USP that addresses it | Evidence from client reviews | Creative angle |
|---|---|---|---|
| [gap] | [USP] | "[verbatim]" | [one-line angle direction] |

**Rule:** Only list opportunities where there is BOTH a competitor gap AND confirmed client
strength. Gaps without client evidence are noted separately as unvalidated opportunities.

**Meta Ad Library competitive analysis:**

For each competitor, based on the Ad Library scrape from Step 1:

| Dimension | Competitor A | Competitor B | Competitor C | Client |
|---|---|---|---|---|
| Total active ads | | | | |
| Dominant format | | | | |
| Dominant hook type | | | | |
| Messaging themes | | | | |
| Gifting creative? | Y/N | Y/N | Y/N | Y/N |
| UGC used? | Y/N | Y/N | Y/N | Y/N |
| Lifestyle/culture creative? | Y/N | Y/N | Y/N | Y/N |
| Heritage/nostalgia creative? | Y/N | Y/N | Y/N | Y/N |
| Comparison ads? | Y/N | Y/N | Y/N | Y/N |

**Creative format gaps (competitor does it, client doesn't):**
- [format/angle] — [which competitor] runs this, client has zero creative

**Creative format whitespace (nobody does it):**
- [format/angle] — no competitor runs this. First-mover advantage if client tests it.

**Competitor ad weaknesses (what they do badly):**
- [weakness] — evidence: [what was observed in their ads]

**Differentiation strategies (minimum 3, maximum 6):**

For each:
- **Strategy:** [what to do differently]
- **Competitor weakness it exploits:** "[verbatim complaint from their reviews]"
- **Client strength it leverages:** [confirmed USP from BRAND-INTELLIGENCE.md]
- **Hook direction:** one line — how this becomes an ad angle

---

## Step 4 — Save COMPETITOR-BRIEF.md (handover to strategic-brief-builder)

Save to: `[client-folder]/COMPETITOR-BRIEF.md`

```markdown
# [CLIENT NAME] — Competitor Intelligence Handover
Generated: [YYYY-MM-DD]

---

## Competitors Researched
[list with URLs and research sources used]

---

## Per-Competitor Summary
### [Competitor Name]
- What they do well: [2 sentences]
- Primary weakness (verbatim evidence): "[quote]"
- Creative angles they run: [format + hook type]
- Tone: [descriptor]
- Sentiment: [Positive / Mixed / Negative]

[repeat per competitor]

---

## Pricing Landscape
[pricing comparison table from Step 2]
[pricing creative implications]

---

## Messaging Overlaps (avoid — saturated)
- [angle] — all competitors use this

## Messaging Gaps (use — whitespace)
- [angle] — no competitor owns this, client has confirmed USP for it

---

## USP Whitespace Map
[full table from Step 2]

---

## Meta Ad Library — Competitive Creative Landscape
[ad library comparison table from Step 3]
[creative format gaps]
[creative format whitespace]
[competitor ad weaknesses]

---

## Differentiation Strategies — Priority Ranked
1. [Strategy] — exploits: "[competitor weakness verbatim]" — leverages: [client USP]
2. [Strategy] — exploits: "[verbatim]" — leverages: [USP]
3. [Strategy] — exploits: "[verbatim]" — leverages: [USP]

---

## Competitor Failure Quotes — Hook Territory
These are verbatim complaints about competitors. They become hooks that name the problem
without naming the competitor.

| Quote | Competitor | Hook translation |
|---|---|---|
| "[exact complaint]" | [brand] | "[how to use this in a hook]" |

Minimum 6 quotes.

---

## Cross-Competitor Emotional Pattern
[The consistent emotional complaint found across multiple competitors — most important insight]

---

## Instructions for strategic-brief-builder
- USPs with Clear whitespace: [list] — prioritise in creative
- USPs with Contested whitespace: [list] — use with stronger proof
- Avoid: [saturated angles]
- Top differentiation hook territory: [2-3 specific directions with evidence]
```

Log the file path. If this file cannot be saved, the run is incomplete.

---

## Step 5 — Notion page (deferred — do not run during research)

Notion sync is handled separately after the research run completes. Do not create a Notion page
during this skill. The CS will run the notion-sync skill when ready.

---

## Quality gates — verify before declaring complete

- [ ] Every gap/opportunity has BOTH competitor weakness AND client strength evidence
- [ ] Every differentiation strategy has a verbatim competitor complaint
- [ ] USP Whitespace Map covers every confirmed USP from BRAND-INTELLIGENCE.md
- [ ] Competitor failure quotes section has minimum 6 verbatim quotes
- [ ] Cross-competitor emotional pattern identified (or explicitly noted as absent)
- [ ] No angle listed as whitespace unless zero competitors are confirmed running it
- [ ] COMPETITOR-BRIEF.md saved and path logged
- [ ] Notion page created — URL logged (or failure noted)
- [ ] Maximum 3 competitors researched
