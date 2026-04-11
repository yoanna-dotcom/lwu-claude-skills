# Reddit Audience Mining — Search Prompts

All prompts below are passed to `perplexity_ask`. Perplexity Sonar Pro is web-grounded and returns real Reddit citations when results come from Reddit.

## How to use

- Substitute `{SUBJECT}` — brand / category / audience segment
- Substitute `{BRAND_BRIEF}` — the brand brief the user provided (positioning, value prop, key differentiator)
- Substitute `{COMPETITORS}` — competitor list, or delete the instruction if auto-discovering
- Substitute `{PERSONA}` — persona focus, or delete if general
- Pass each complete prompt as the `question` parameter to `perplexity_ask`
- Collect every response + citation list including any upvote counts mentioned
- Do not modify the prompts — they're written to force Reddit-specific, quote-heavy, engagement-signal results

---

## Search 1 — Brand-specific mentions

```
Search Reddit for recent discussions mentioning "{SUBJECT}". I want to see what real people are saying about this brand/product in unprompted conversations — not marketing content, not press releases.

Brand context for relevance filtering: {BRAND_BRIEF}

Focus on:
- Direct brand mentions in relevant subreddits
- Sentiment — are people positive, negative, mixed?
- What specific aspects of the brand do they talk about most?
- Which subreddits have the highest concentration of mentions?
- Include upvote counts for any threads or comments if available — higher upvotes = stronger signal

For each finding, give me:
1. The verbatim quote (do not paraphrase)
2. The subreddit name (e.g. r/nutrition)
3. The upvote count if visible
4. The context — what was the thread about?

Return at least 8-12 verbatim quotes with subreddit sources. If you can't find that many, tell me explicitly "only found X quotes" rather than padding with generic commentary.
```

---

## Search 2 — Brand-specific pain points

```
Search Reddit for complaints, frustrations, and negative experiences related to "{SUBJECT}". I want to understand what real customers struggle with, in their own words.

Brand context: {BRAND_BRIEF}

Focus on:
- Specific complaints about the product/brand
- Things people wish were different
- Moments of frustration — what triggered them
- Recurring themes across multiple threads
- Include upvote counts for highly-upvoted complaints — these are the validated pain points

For each pain point, give me:
1. A clear label for the pain point (e.g. "Shipping takes too long", "Taste is chalky")
2. At least 2 verbatim quotes supporting it
3. The subreddits where these complaints appear
4. Upvote counts if visible — prioritise the highest-upvoted complaints
5. Rough frequency — is this mentioned once, occasionally, or constantly?

Return the top 5-8 pain points ranked by frequency and upvote weight. Use the exact language people use — do not clean up grammar or paraphrase.
```

---

## Search 3 — Brand-specific golden quotes

```
Search Reddit for high-signal, memorable, quotable posts about "{SUBJECT}". I'm looking for organic customer comments a copywriter could use verbatim in an ad.

Brand context: {BRAND_BRIEF}

Focus on:
- Transformation stories ("I tried X and it changed...")
- Strong emotional reactions (positive or negative)
- Comparisons with alternatives ("I used to use Y but now...")
- Specific, concrete outcomes with numbers/details
- Surprising insights no one else is saying
- Include upvote counts — a quote with 400 upvotes is infinitely more valuable than one with 2

For each quote, give me:
1. The full verbatim quote — keep it intact, don't edit for grammar
2. The username if available (or "anonymous")
3. The subreddit (e.g. r/fitness)
4. Upvote count if visible
5. Brief context — what was the original question or thread about?

Return 10-15 golden quotes. Prioritise quotes that are specific, emotional, and high-upvote over generic praise.
```

---

## Search 4 — Category conversations

```
Search Reddit for discussions about the broader category that "{SUBJECT}" operates in — not brand-specific, but the wider conversation about the problem space and product type.

Brand context for relevance filtering: {BRAND_BRIEF}

For example, if {SUBJECT} is a bedding brand, the category is "bed sheets" or "sleep quality". If {SUBJECT} is a meal replacement brand, the category is "meal replacements" or "busy people who skip meals".

Focus on:
- What problems is this category trying to solve?
- What are the biggest frustrations with category-wide options?
- What do newcomers ask when they're first exploring? ("I'm new to X, where do I start?")
- What debates and disagreements are ongoing?
- What subreddits are the category epicentres?
- Which threads have the highest upvotes — these reveal the most resonant category tensions

Return:
1. The top 5 most-discussed themes with at least 2 verbatim quotes each (with subreddit + upvote count)
2. The 3-5 subreddits most active on this category
3. Any ongoing debates or tensions worth flagging
4. The single most-upvoted thread you found and what it reveals about the category
```

---

## Search 5 — Competitor mentions

```
{IF COMPETITORS PROVIDED:}
Search Reddit for discussions mentioning these competitors to {SUBJECT}: {COMPETITORS}. I want to see how they're discussed, what language people use when comparing them, and where each one falls short.

{IF NO COMPETITORS PROVIDED:}
Search Reddit for discussions where people compare {SUBJECT} to alternatives or ask for recommendations in this category. What competitors come up most often? What language do people use when comparing options?

Brand context: {BRAND_BRIEF}

Focus on:
- Head-to-head comparison threads ("X vs Y")
- Why people switched from one brand to another (in both directions)
- What each competitor is seen as being "best for"
- Specific weaknesses and complaints — not just general sentiment
- Price/value comparison language
- Include upvote counts — highly-upvoted competitor criticism is the most actionable finding

For each competitor, give me:
1. The competitor name
2. Overall sentiment (positive/mixed/negative) with a rough percentage
3. At least 2 verbatim comparison quotes with subreddit + upvotes
4. The most common complaint or weakness mentioned
5. The "reason to switch away from them" — the most actionable gap

Return the top 5 competitors ranked by mention frequency. Flag any competitor with a specific exploitable weakness.
```

---

## Search 6 — Community language

```
Search Reddit to extract the exact phrases and vocabulary real people use when talking about "{SUBJECT}" and its problem space. I'm looking for language a copywriter could use verbatim in ads to sound like an insider, not a brand.

Brand context: {BRAND_BRIEF}

Focus on:
- Slang and community-specific terms
- How they describe the problem (the "before" state)
- How they describe success or the solution (the "after" state)
- Emotional language — words that carry strong feeling
- Phrases that come up repeatedly across multiple threads
- "Before" language vs "After" language — what changes in how they talk once they've found a solution

Return:
1. A list of 15-20 exact verbatim phrases (no paraphrasing)
2. The subreddit where each phrase appeared
3. Whether it's "before" language (describing the problem) or "after" language (describing success)
4. Upvote signal where available
5. Group the phrases into themes: "Describing the problem", "Describing success", "Expressing frustration", "Comparing options", "What they want but can't find"

These phrases will be used directly in ad copy. Accuracy and authenticity matter more than coverage.
```

---

## Search 7 — Problem-first phrasing *(deep mode only)*

```
Search Reddit for threads where people describe the problem that "{SUBJECT}" solves, WITHOUT knowing {SUBJECT} exists. I want the exact language people use before they've discovered the solution.

Brand context: {BRAND_BRIEF}

For example, if {SUBJECT} is a natural fibre bedding brand, I'm looking for posts like "I sweat so much at night, I've tried everything" — NOT posts specifically about bedding brands.

Focus on:
- Threads titled "Anyone else...", "Is this normal...", "I'm struggling with..."
- People asking for help, advice, or recommendations without knowing the solution
- The emotional weight of the problem — are they frustrated, desperate, resigned, embarrassed?
- How long they've been dealing with the problem before posting
- Include upvotes — high-upvote "is this normal?" posts are the best cold-audience hook fuel

Return 8-12 verbatim "problem-first" quotes with:
1. The full quote
2. Subreddit source + upvote count if visible
3. Thread context (what were they asking for?)
4. Emotional state — what do they sound like? Desperate? Resigned? Fed up?
5. Whether the thread had replies pointing to solutions like {SUBJECT}

These are the exact hooks for top-of-funnel creative targeting people at zero awareness.
```

---

## Search 8 — Failed solutions *(deep mode only)*

```
Search Reddit for posts where people describe things they tried that DIDN'T work for the problem "{SUBJECT}" solves. I want to understand their previous failed attempts and why they gave up.

Brand context: {BRAND_BRIEF}

Focus on:
- "I tried X but..." posts
- Frustration with previous attempts — what specifically let them down
- Which failed solutions come up most often
- How much money/time/effort they wasted before giving up
- The emotional aftermath — are they cynical, hopeful, exhausted?
- High-upvote posts about failed solutions are the strongest "before" state evidence

Return the top 5-8 failed solutions ranked by frequency:
1. The failed solution name
2. Why it failed in their words (verbatim quotes, at least 2 per solution)
3. Subreddits + upvote counts
4. How long they tried before giving up (if mentioned)
5. The specific moment they gave up

This maps the "before" state for creative — what audiences have already rejected, so we know what NOT to sound like.
```

---

## Search 9 — Persona signals *(deep mode only)*

```
{IF PERSONA FOCUS PROVIDED:}
Search Reddit to build a detailed picture of the "{PERSONA}" audience who might care about {SUBJECT}. I want demographic, lifestyle, psychographic, and behavioural signals.

{IF NO PERSONA FOCUS:}
Search Reddit to identify who the actual person discussing {SUBJECT} and its problem space is. I want demographic, lifestyle, psychographic, and behavioural signals from their posts.

Brand context: {BRAND_BRIEF}

Focus on:
- Age range indicators (explicit mentions or inferred from life stage references)
- Life stage markers (single, new parent, first home, empty nester)
- Occupation or income signals (even indirect — "I can't afford X", "just got a promotion")
- Daily routines and constraints — when is the problem most acute?
- Other subreddits they participate in (their digital footprint reveals who they are)
- Values and identity markers — what do they care about beyond the product?
- How they talk — formal/casual, emotionally open/guarded, expert/novice

Return:
1. A 3-4 sentence persona sketch based only on evidence from searches
2. Supporting verbatim quotes for each claim (minimum 2 per claim with subreddit sources)
3. Other subreddits they hang out in — list them all, this reveals media buying opportunities
4. Key psychographic markers: what they care about, what they avoid, what they aspire to
5. The one insight about this person that would most change how we speak to them in ads

Every claim must be evidence-backed. If you can't find supporting quotes, say so.
```

---

## Search 10 — Emotional state *(deep mode only)*

```
Search Reddit for posts about "{SUBJECT}"'s problem space where people express strong emotions. I want to map the emotional landscape — what they feel before, during, and after engaging with this category.

Brand context: {BRAND_BRIEF}

Focus on:
- Frustration, desperation, resignation (negative emotions about the problem)
- Relief, joy, pride (positive emotions after finding a solution)
- Fear, anxiety, worry (what they're scared of)
- Shame or embarrassment (things people admit on anonymous Reddit they wouldn't say publicly)
- Hope, optimism (what they're reaching for)
- Include upvotes — the most emotionally resonant posts tend to get the most upvotes

Return:
1. The dominant emotional states, ranked by frequency
2. At least 3 verbatim quotes per state — use the exact emotional language (with subreddit + upvotes)
3. The trigger event that causes each emotion — what happened right before they posted?
4. The emotional arc: what does the journey from problem to solution actually feel like for them?
5. Which emotions are most underrepresented in current brand advertising — these are creative gaps

This maps the emotional terrain we need to match in creative. If the audience feels desperate, the ad should acknowledge desperation before offering hope.
```

---

## Synthesis Guidance

After all searches, synthesise raw Perplexity responses into the output template in SKILL.md Step 5.

**The single most important synthesis rule: interpret through the brand brief.**

Don't just report what Reddit says. For every finding, ask: "Given what this brand is and who they serve, what does this mean? What should they do about it?"

**Hidden Gems checklist — a gem must have all of these:**
- A specific, memorable, quotable moment from the research (not a general theme)
- A written hook idea — actual copy you'd put at the start of an ad
- A persona tag
- A messaging bucket label
- Upvote count or engagement signal if available

If you can't write a hook from something, it's not a gem. Put it in Golden Quotes instead.

**Next Steps checklist — a next step must have all of these:**
- A written hook (the actual words, not a description of the words)
- The persona it targets
- The format to test it in (UGC / brand video / static / carousel)
- One sentence citing the specific Reddit finding that justifies it

**Engagement signal guidance:**
- 1,000+ upvotes: Category-defining pain — the audience has voted this as universal
- 400-999 upvotes: Strong validated pain — highly actionable
- 100-399 upvotes: Real pain with meaningful resonance
- Under 100: Single data point — useful but needs corroboration
- No upvote data: Note as "engagement unknown" — don't inflate its weight
