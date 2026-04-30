---
name: psm-brief-builder
description: >
  PSM-facing brief builder for non-creative-service clients. Conversational entry —
  Claude asks structured questions, loads all Growth Centre context automatically,
  writes 3–4 production-ready concepts with 3 variations each (9–12 assets),
  provides framework + Foreplay references for PSM to embed manually, pushes brief to Notion.
  Trigger: "/psm-brief-builder [client-name]"
---

# PSM Brief Builder

## Who this is for

Paid Social Managers running briefs for clients not on the creative service. No creative strategy background needed — Claude handles the strategy layer. Your job is to answer the questions, check the output makes sense for the client, and attach the visual references before sending.

---

## Trigger

```
/psm-brief-builder [client-name]
```

Example: `/psm-brief-builder art-of-football`

---

## Step 0 — Load all context (silent — not shown to PSM)

Always load these two files first — they apply to every brief regardless of client:
- `~/.claude/skills/psm-brief-builder/LWU-SCRIPTING-BEST-PRACTICES.md` — universal creative standards (banned language, hook rules, awareness stages)
- `~/.claude/skills/psm-brief-builder/LWU-CREATIVE-CONTEXT.md` — complete LWU creative intelligence system: static/UGC/HP frameworks, psychological triggers, iteration logic, quality benchmarks. Log ✅ or ⚠️ MISSING.

Search for the client folder at `~/Desktop/[client-name]/` and read the following simultaneously:

- `MUST-READ-SCRIPTING.md` → log ✅ or ⚠️ MISSING
- `STRATEGIC-BRIEF.md` → log ✅ or ⚠️ MISSING
- `BRAND-INTELLIGENCE.md` → log ✅ or ⚠️ MISSING
- `PERSONA-STRATEGY.md` → log ✅ or ⚠️ MISSING
- `feedback/performance-log.md` → log ✅ with cycle count, or ⚠️ NOT YET STARTED

**Notion fallback** — if local files are missing, run `notion-search` for "[client-name] Growth Strategy OS". Fetch the Persona Bank, Brand Intelligence, and Strategic Brief pages if found.

**Hard stops:**
- If neither BRAND-INTELLIGENCE.md nor any Notion equivalent is found:
  → STOP. Output: "I can't find any brand context for [client]. The Growth Centre needs to be set up first. Reach out to your CS to run the onboarding research before using this tool."

**Must-read auto-generation** — if MUST-READ-SCRIPTING.md is missing:
  → Do not silently continue. Output this to the PSM:

  ```
  ⚠️ No client-specific scripting rules found for [client].
  This is a one-time setup — takes about 2 minutes. I'll create the file automatically.

  Please answer these 5 questions:

  1. What are 2–3 things that are unique or non-obvious about this brand?
     (e.g. production method, origin, a guarantee, something competitors don't have)

  2. What language or phrases should NEVER appear in this brand's ads?
     (e.g. words that feel off-brand, competitor phrases, anything the client has flagged)

  3. Who is the primary customer in one sentence?
     (e.g. "Women 35–55 buying plants for their garden, nervous about killing them")

  4. What is the #1 thing this brand's customers are afraid of or frustrated by before they buy?

  5. Is there anything specific the client has asked for or flagged in the past?
     (e.g. "always show the product in use", "never use discount language", "client hates the word 'premium'")
  ```

  Once PSM answers → generate `[client-folder]/MUST-READ-SCRIPTING.md` using their answers + LWU universal standards. Save it. Confirm: "✅ Must-read file created and saved. I'll use this from now on for every [client] brief."

  Then continue to Step 1.

**Performance log:**
- If `feedback/performance-log.md` exists: read it. Extract angles/formats to avoid, what to repeat, any client feedback notes.
- If missing: log "No performance history yet — applying brand intelligence only."

---

## Step 1 — Brief the PSM on what's loaded

Output this before asking any questions:

```
Hi! I've loaded everything for [Client Name].

Here's what I have:
[✅/⚠️] Brand Intelligence
[✅/⚠️] Persona Strategy
[✅/⚠️] Strategic Brief + Scripting Rules
[✅/⚠️] Performance History ([N] cycles logged / Not yet started)

[If anything ⚠️ MISSING — one plain-English sentence on what that means]

Let's build your brief. 8 quick questions:
```

---

## Step 2 — Ask questions using AskUserQuestion tool

Use the AskUserQuestion tool for every question. One question per tool call. Wait for the answer before calling the next. This renders a clickable interactive widget — PSM clicks, never types.

---

### Question 1 — Format
Call AskUserQuestion with:
- question: "What type of ad are we making?"
- header: "Format"
- options:
  - label: "Static", description: "Image-based — no video needed, fastest to produce"
  - label: "UGC", description: "A creator films themselves talking about the product"
  - label: "HP Video", description: "Existing footage edited together with voiceover"
  - label: "Not sure", description: "I'll recommend based on what's underinvested in the account"

---

### Question 2 — Persona
Call AskUserQuestion with:
- question: "Who are we targeting?"
- header: "Persona"
- options: [pull from PERSONA-STRATEGY.md — max 4, use plain-English descriptions]
  For AOF:
  - label: "Culture Curator", description: "Football is his identity, not just his team — wears it as fashion, not uniform"
  - label: "Club Loyalist", description: "Match-going fan who wants something better than the replica kit"
  - label: "Gift Solver", description: "She's buying for him — he has every shirt, she needs something he doesn't have"
  - label: "Heritage Collector", description: "Obsessed with a specific era — 'so hard to get things with this era of club crest'"

---

### Question 3 — Awareness Stage
Call AskUserQuestion with:
- question: "What awareness stage is this audience at?"
- header: "Awareness Stage"
- options:
  - label: "Unaware", description: "They don't know the problem exists — emotional storytelling, pattern interrupt, no brand assumption"
  - label: "Problem Aware", description: "They feel the pain but haven't found a solution — name it, introduce the brand as the answer"
  - label: "Solution Aware", description: "They know solutions exist but haven't chosen — why your mechanism specifically"
  - label: "Product Aware", description: "They know the brand but haven't bought — remove the final objection, proof, guarantee"
  - label: "Most Aware", description: "Ready to buy — friction removal, offer clarity, urgency"

---

### Question 4 — Angle
AskUserQuestion supports max 4 options. Show the top recommended angles from STRATEGIC-BRIEF.md tier list. PSM can use "Other" (auto-provided) to type any angle from the full list.

Call AskUserQuestion with:
- question: "What's the main message direction? (Type any angle in 'Other' if not listed)"
- header: "Angle"
- options: [top 4 Tier 1/2 angles from STRATEGIC-BRIEF.md for this client]
  For AOF:
  - label: "Lifestyle Integration", description: "Football as part of who he is — wearable anywhere, not just at the ground"
  - label: "Gifting", description: "'He has every shirt. He doesn't have this.' — works year-round, not just Christmas"
  - label: "Social Proof", description: "Real fan reviews and compliments at the ground — 6,198 reviews available"
  - label: "Before & After", description: "Failed solution (club shop, transfers, generic merch) → AOF resolution"

Once angle selected → cross-reference with STRATEGIC-BRIEF.md and flag tier in Step 2.5.

---

### Question 5 — Product
Call AskUserQuestion with:
- question: "What product or collection are we focusing on?"
- header: "Product"
- options: [pull priority SKUs from STRATEGIC-BRIEF.md]
  For AOF:
  - label: "Hoodies", description: "Embroidered range — best CTR, embroidery mechanism most visible"
  - label: "Guinness Collab", description: "17–31% of spend, validated commercial engine"
  - label: "Era-specific designs", description: "90s, Clough, Invincibles — Heritage Collector territory"
  - label: "Tees", description: "Lower price entry point, gift-friendly, year-round"

PSM can type a specific product via "Other".

---

### Question 6 — Asset Type
Call AskUserQuestion with:
- question: "Who's producing this asset?"
- header: "Asset type"
- options:
  - label: "Brand-produced", description: "Shot in-house or studio"
  - label: "Creator", description: "Someone films it themselves — UGC style"

---

### Question 7 — Destination
Call AskUserQuestion with:
- question: "Where does the ad click through to?"
- header: "Destination"
- options:
  - label: "Homepage", description: "Broad appeal — good for cold audiences"
  - label: "Product page", description: "Specific product — use 'Other' to paste the URL or product name"

---

### Question 8 — Number of Concepts
Call AskUserQuestion with:
- question: "How many concepts do you need? (Each includes 3 variations)"
- header: "Concepts"
- options:
  - label: "1 concept", description: "3 assets total"
  - label: "2 concepts", description: "6 assets total"
  - label: "3 concepts", description: "9 assets total — recommended starting point"
  - label: "4 concepts", description: "12 assets total — maximum per cycle"

Once answered → move to Step 2.5 confirmation.

---

## Step 2.5 — Confirm before writing

Once PSM replies, output a brief confirmation block:

```
Got it. Here's what I'm building:

Format: [answer]
Persona: [name + one-line description]
Awareness stage: [selected] — [Unaware: emotional storytelling, no brand assumption / Problem Aware: name the pain, introduce brand / Solution Aware: why this mechanism / Product Aware: remove final objection / Most Aware: friction removal + urgency]
Angle: [name] — [Tier X / not yet tested / ⚠️ saturated]
Product: [product name]
Asset type: [Brand / Creator]
Destination: [HP / PDP]
Concepts: [N] × 3 variations = [N×3] assets

[If angle is Saturated]: ⚠️ This angle is heavily used by competitors. I'll make sure the mechanism — the specific how and why the product works — is doing the heavy lifting, not just the message type.
[If performance log flags this angle as Kill]: ⚠️ This angle underperformed last cycle ([result]). Proceeding as you've asked — flagged in the brief.
[If performance log shows a strong repeater]: ✅ This angle has a strong track record ([result]). I'll use that as the quality benchmark.

Starting now.
```

---

## Step 3 — Pre-Write Declaration (internal — not shown to PSM)

Complete this for every concept before writing a single word of copy. If any field cannot be filled from real brand data — note the gap in the brief output. Do not fabricate.

```
CONCEPT [N] — PRE-WRITE DECLARATION
─────────────────────────────────────────────
Persona: [name + one-line from PERSONA-STRATEGY.md]
Awareness stage: [selected by PSM — drives hook approach, assumed knowledge, copy intensity]
Core tension: [exact phrase from VOC glossary or BRAND-INTELLIGENCE.md — not paraphrased]
Brand mechanism that resolves it: [specific differentiator — not "quality" or "great product"]
Hook territory: [fear / curiosity / identity / reward / realisation / seasonal timing]
VOC phrase to use verbatim: [exact quote from brand docs]
Performance basis (if extending what worked): [reference from performance log]
Whitespace basis (if new territory): [gap from competitor brief or angle tier]
─────────────────────────────────────────────
```

---

## Step 4 — Write each concept

Produce [N] concepts, each with 3 variations. Use the structure matching the selected format.

---

### Static concept structure

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCEPT [N] — [DESCRIPTIVE NAME IN CAPS]
Format: Static | Persona: [name] | Angle: [name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS CONCEPT
[2 sentences max. What specific tension does this resolve for this persona? What data or VOC supports it?]

Each variation uses a DIFFERENT framework — never repeat the same framework within a concept.

VARIATION 1 — Static — [descriptor] | Framework: Static Headliner
Headline: [3–6 words — instant clarity OR instant curiosity. Not a brand statement. Not vague.]
Supporting copy: [1 short line — verbatim VOC phrase OR one scannable claim. Not an explanation. Readable in under 1 second.]
Trust signals: [1 line — e.g. "★★★★★ 6,198 reviews" / press mention / retailer. Required on every static.]
Visual: [What needs to be shown — product in context, key feature, lifestyle moment]
CTA: [brand CTA]

VARIATION 2 — Static — [descriptor] | Framework: Static Review
Headline: [3–6 words]
Supporting copy: [verbatim customer quote — unedited, the exact words they used. Not paraphrased.]
Trust signals: [star rating + review count]
Visual:
CTA:

VARIATION 3 — Static — [descriptor] | Framework: [Native UI / PR Headline / Problem-Solution — pick best fit for this angle]
Headline: [3–6 words]
Supporting copy: [1 scannable line matching the framework — PR Headline: editorial-style claim; Problem-Solution: resolution claim; Native UI: platform-mimicking text]
Trust signals: [1 line]
Visual:
CTA:

VISUAL REFERENCES
Open the board matching your variation framework — pick 2–3 specific ads, screenshot and embed. No links to client.
→ Static Headliner: https://app.foreplay.co/share/boards/gxLnlhUi4K2Bely46BMh
→ Static Review: https://app.foreplay.co/share/boards/uUBuIboDXCjys4uZfsqu
→ PR Headline: https://app.foreplay.co/share/boards/Udtg1DJlXHlALhdYowLi
→ Problem-Solution: https://app.foreplay.co/share/boards/b1Yz3JGG7rXKPa9iwtb0
→ General statics: https://app.foreplay.co/share/boards/NOYRM2XK633Vw6G05nOt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### UGC concept structure

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCEPT [N] — [DESCRIPTIVE NAME IN CAPS]
Format: UGC | Persona: [name] | Angle: [name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS CONCEPT
[2 sentences — what tension this resolves + why it's specific to this brand]

HOOK 1 — Tension / Fear
Spoken (1 sentence, no warm-up): [names a specific failure or anxiety]
Opening visual: [what creator does in first 3 seconds]

HOOK 2 — Identity / Realisation
Spoken (1 sentence): [moment of recognition — "I didn't know..." or "I used to..."]
Opening visual:

HOOK 3 — Reward / Curiosity
Spoken (1 sentence): [solution-first or payoff moment]
Opening visual:

BODY FLOW (same for all 3 hooks)
⚠️ This is a guide — creator uses their own words

Example script:
[Natural spoken English. First person. Brand named in first 10 seconds.
One thought per sentence. Mechanism → outcome → CTA.]

Scene breakdown:
• Scene 1 (0–3s): Hook + opening visual
• Scene 2 (3–12s): Problem / context
• Scene 3 (12–22s): Brand + mechanism introduced naturally
• Scene 4 (22–28s): Outcome + CTA

Creator requirements:
[Demographics and tone from persona — keep it plain, e.g. "feels like a real customer, not an actor"]
Avoid: [specific things not to do — wrong product angle, mismatched energy, etc.]

VISUAL REFERENCES
Match the board to the creator style — pick 2–3 specific ads, screenshot and embed. No links to client.
→ General UGC: https://app.foreplay.co/share/boards/p8fQ6Tqz35v54XqLMoJ1
→ POV: https://app.foreplay.co/share/boards/p4hQFrRJWJU0ISedeE3u
→ Testimonial: https://app.foreplay.co/share/boards/uUBuIboDXCjys4uZfsqu
→ Street interview: https://app.foreplay.co/share/boards/gHztbXoAasVfp2aXdowl
→ Storytelling: https://app.foreplay.co/share/boards/SpV2QHelwoPlzGz779CY
→ Founder: https://app.foreplay.co/share/boards/tQCIm4ta9ItnxFpFSCWo
→ Us vs Them: https://app.foreplay.co/share/boards/XMtPmitGPSWVYjUxut7X
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### HP Video concept structure

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONCEPT [N] — [DESCRIPTIVE NAME IN CAPS]
Format: HP Video | Persona: [name] | Angle: [name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY THIS CONCEPT
[2 sentences]

VARIATION 1 — HP Video — [descriptor]
Hook (0–3s): [Visual + VO copy]
Problem (3–8s): [VO line + scene description]
Mechanism (8–15s): [Product moment or proof beat]
Proof (15–22s): [VOC line or social proof]
CTA (22–30s): [Verbal line + text overlay]
Editor notes: [pacing, music direction, any format rules]

VARIATION 2 — HP Video — [descriptor]
[Same structure, different hook direction]

VARIATION 3 — HP Video — [descriptor]
[Same structure, different hook direction]

VISUAL REFERENCES
Pick 2–3 video examples, screenshot thumbnail + key frame. Embed in brief. No links to client.
→ VSL: https://app.foreplay.co/share/boards/z8p818F3rqxEZvigmQYn
→ Podcast style: https://app.foreplay.co/share/boards/pAsPaNDspB8mM2l1SfiD
→ AI Voiceover: https://app.foreplay.co/share/boards/cCRd1KTcQEHB57bmxUqn
→ Storytelling: https://app.foreplay.co/share/boards/SpV2QHelwoPlzGz779CY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 5 — Quality gates (blocking — fix before output, not shown to PSM)

Every concept passes all of these before it is output. Fix failures inline — do not flag them to the PSM.

- [ ] Swap test — a direct competitor cannot say this unchanged. If they can, rewrite.
- [ ] VOC grounding — at least 1 verbatim phrase from brand docs used per concept
- [ ] No banned language from MUST-READ-SCRIPTING.md
- [ ] Headline: 3–6 words (static). Hook: 1 punchy spoken sentence (video/UGC). No clause before the point.
- [ ] Static supporting copy: 1 short line max. Not an explanation. Reads in under 1 second.
- [ ] Static trust signals: present on every variation (reviews / press / retailer)
- [ ] Static frameworks: 3 variations use 3 different frameworks (Static Headliner / Static Review / Native UI / PR Headline / Problem-Solution)
- [ ] Awareness stage match — copy matches the stage PSM selected. Unaware/Problem Aware: no brand knowledge assumed. Solution/Product Aware: some familiarity OK. Most Aware: full brand knowledge assumed.
- [ ] No invented data — if account insight is missing, note it, do not fabricate
- [ ] Platform-native — would a real person stop scrolling for this in feed?

---

## Step 6 — Save locally + output to PSM

Save to: `[client-folder]/briefs/brief-[client]-[YYYY-MM-DD].md`

Output to PSM:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Brief complete — [Client Name]
[N] concepts | [N×3] variations | [Angle] | [Persona]

📁 Saved locally: [client-folder]/briefs/brief-[client]-[date].md

BEFORE SENDING TO CLIENT:
→ Open the Foreplay / Framework links in each concept
→ Pick 2–3 specific examples per concept that match the visual direction
→ Screenshot and drop them directly into the brief
→ Remove the reference links — client sees images only

When you're happy with the output:
→ Send: "Push [Client] brief to Notion — [date]"
Claude will then create the Notion page and format everything for client delivery.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 7 — Push to Notion (on explicit sign-off only)

Only runs when PSM sends: "Push [client] brief to Notion — [date]"

The client's Open Brief System database URL should be in STRATEGIC-BRIEF.md or the PSM pastes it in the trigger message.

Create **one page per concept** inside the client's Open Brief System database using `notion-create-pages`.

---

### Page title

`[format emoji] [CONCEPT NAME] — "[hook or headline]"`

Emoji key: Static → 🖼️ | UGC → 🎬 | HP Video → 📹

---

### Database properties (set on every page)

- **Format**: "Static" / "UGC" / "HP Video"
- **Angle**: [angle from brief]
- **Creator**: "Brand" or creator name
- **Destination**: "HP" or "PDP"
- **Macro Persona**: [persona label from PERSONA-STRATEGY.md]
- **Product/Offer**: [product name]
- **Variations**: "3"
- **Date**: [date from PSM trigger message, format YYYY-MM-DD]

---

### Page content — build in this order

**1. Yellow callout — Strategy**

Insert a 2-column table inside (left column: label field, yellow_bg, 160px):

| | |
|---|---|
| Angle | [angle name] |
| Funnel stage | [awareness stage selected by PSM] |
| Persona | [persona name + one-line description] |
| Core tension | [exact phrase from Pre-Write Declaration — no paraphrase] |
| Hypothesis | [what this creative is testing — 1 sentence] |
| Evidence | [verbatim VOC phrase or performance data supporting this direction] |

---

**2. Blue callout — Variations**

For each of the 3 variations:
- H3 heading: `Variation [N] — [descriptor] | [Framework]`
- 2-column table below the heading (left column: label field, blue_bg, 160px)

Static rows: **Headline** (bold) | Supporting copy | Trust signals | Visual | CTA | Framework

UGC rows: Hook | Opening visual | Body (guide — creator uses own words) | Scene breakdown | Creator requirements

HP Video rows: Hook (0–3s) | Problem (3–8s) | Mechanism (8–15s) | Proof (15–22s) | CTA (22–30s) | Editor notes

---

**3. Purple callout — Design Notes**

Visual direction for this concept: tone, color, product placement, lifestyle context. Specific enough that a designer or editor knows what to select or shoot.

---

**4. Green callout — ⚠️ Rules**

Top 3 scripting rules from MUST-READ-SCRIPTING.md most likely to be violated for this format and angle. Write as ✅ Do / ❌ Don't pairs.

Then the format-specific checklist:
- **Static**: Headline 3–6 words | Supporting copy 1 short line | Trust signals on every variation | 3 different frameworks
- **UGC**: Hook 1 spoken sentence, no warm-up | Brand named in first 10 seconds | No ad language
- **HP Video**: Hook stacks visual + VO | Re-hook by 15s | Specific numbers over claims

---

**5. Blue 👀 callout — References**

Three sections:

_Foreplay boards_ — link to the board for each framework used in this concept (pull URLs from Step 4 VISUAL REFERENCES). Add note: "Screenshot 2–3 examples per framework. Drop images directly into brief. Remove these links before client delivery."

_VOC used_ — every verbatim quote that appears in this concept, labelled by source (review / VOC doc / performance log).

_Competitor context_ — 1 sentence on what competitors are doing in this space (from performance log or COMPETITOR-BRIEF.md). If no data: omit.

---

## Step 8 — Remind PSM to update the performance log

After outputting the brief, always add:

```
📊 After this campaign runs (2–4 weeks):
→ Update [client-folder]/feedback/performance-log.md with results + verdict
→ The more cycles logged, the more specific your next brief will be
```

---

## Universal scripting rules (always active — no exceptions)

1. Specificity over genericism — if 10 other brands could say it, rewrite it
2. Fear removal over aspiration — solve an anxiety, not a dream
3. Speak, don't write — ads are heard in feed, not read. No written clauses.
4. Hooks are decisions — static: 3–6 words. Video/UGC: 1 punchy sentence. No warm-up lines.
5. Swap test is mandatory — not optional
6. VOC is the brief — real buyer language beats any copywriter instinct
7. Platform-native — would a real person stop for this in feed? If not, rewrite.
8. No awareness stage mismatches — cold audiences don't know the brand. Don't write like they do.
9. Mechanism beats claim — "grows in British soil hardened to British weather" beats "high quality plants"
