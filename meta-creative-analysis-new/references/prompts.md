# Gemini Analysis Prompts

This file documents the prompt templates used for each analysis mode. The script
loads the right prompt based on `--analysis-type`. Each prompt is injected with
the ad's metadata, performance metrics, and (when available) the uploaded media file.

All prompts are grounded in Soar Group's creative strategy frameworks.

## Table of Contents

1. [Core Frameworks](#core-frameworks)
2. [End-to-End Audit Prompt](#end-to-end-audit)
3. [Persona & Spend Gap Analysis Prompt](#persona-gap-analysis)
4. [Valence Deep Dive Prompt](#valence-deep-dive)
5. [Performance-Creative Correlation Prompt](#performance-correlation)
6. [Persona Synthesis Prompt](#persona-synthesis)
7. [Valence Synthesis Prompt](#valence-synthesis)
8. [Framework Audit (Selective)](#framework-audit-selective)
9. [Growth Strategy Opportunity Synthesis](#growth-strategy-opportunity-synthesis)
10. [Metrics-Enriched Add-on](#metrics-enriched-addon)

---

## Core Frameworks

These frameworks are injected into every prompt to ground analysis in Soar's methodology.

### Emotional Identification

Every ad targets one or more of these four core emotions:

| Emotion | Definition | Example Triggers |
|---------|-----------|-----------------|
| **Achievement** | Desire to succeed, improve, or reach goals | Progress, mastery, results, competition |
| **Autonomy** | Desire for control, independence, freedom | Choice, simplicity, self-reliance |
| **Belonging** | Desire to connect, fit in, be part of something | Community, shared experience, validation |
| **Empowerment** | Desire to feel capable, confident, in charge | Knowledge, tools, transformation |

### Story Frameworks

Classify which narrative structure the ad follows:

| Framework | Structure | Best For |
|-----------|----------|----------|
| **StoryBrand** | Hero (customer) has problem → Guide (brand) offers plan → Success | Brand positioning |
| **PAS** | Problem → Agitate → Solution | Pain-point driven |
| **AIDA** | Attention → Interest → Desire → Action | Direct response |
| **Pixar** | Once upon a time... Every day... One day... Because of that... Until finally... | Emotional narrative |
| **Before & After** | Life before → Transformation → Life after | Results-driven |

### Awareness Levels (Funnel Stage)

| Level | Funnel | The Viewer... | Creative Should... |
|-------|--------|--------------|-------------------|
| **Problem-Unaware** | TOF | Doesn't know they have a problem | Educate, disrupt, create awareness |
| **Problem-Aware** | MOF | Knows the problem but not the solution | Agitate, present the solution category |
| **Solution-Aware** | BOF | Knows solutions exist, comparing options | Differentiate, prove, overcome objections |

### 8-Angle Taxonomy

Every ad's messaging angle maps to one of these:

1. **Objection Handling** — Pre-empts and addresses a common purchase objection
2. **Education / Lightbulb** — Teaches something new that reframes the category
3. **Comparison / Us vs Them** — Direct or indirect comparison to alternatives
4. **Social Proof** — Reviews, testimonials, UGC, press mentions, stats
5. **Routine / Day-in-Life** — Shows product integrated into daily life
6. **Before → After Transformation** — Visual or narrative transformation
7. **Founder / Insider POV** — Behind-the-scenes, founder story, brand mission
8. **Myth Busting** — Challenges a common misconception in the category

### KPI Benchmarks (RAG Scoring)

| Metric | 🟢 Green | 🟡 Amber | 🔴 Red |
|--------|----------|----------|--------|
| TSR (Thumbstop Rate) | >30% | 20-30% | <20% |
| Hold Rate (15s) | >45% | 30-45% | <30% |
| Hold Rate (30s) | >30% | 20-30% | <20% |
| CTR | >1% | 0.5-1% | <0.5% |
| Frequency (30d blended) | <2.5 | 2.5-3.5 | >3.5 |

### Ad Lifecycle Classification

| State | Criteria | Action |
|-------|---------|--------|
| **Testing** | <3-5 days live, insufficient data for judgement | Monitor, don't judge yet |
| **Scaling** | Exceeding benchmarks, consistent performance | Increase budget, iterate |
| **Retire** | Below benchmarks, no recovery trend | Kill, learn from it |
| **Retest** | Promising on one metric but failing another | Iterate the weak element |

### Valence Deep Dive — 3-Dimensional Psychological Matrix

The Valence Deep Dive maps creative across three dimensions of psychological distinctness.
Ads that differ only on surface variables (hook style, background colour) but occupy the
same psychological zone are NOT strategically distinct. True creative diversity means
covering different zones in this matrix.

#### Dimension 1: Valence Zone (Emotional Charge)

The emotional charge of the ad mapped to a 4-quadrant model:

| Zone | Valence | Arousal | Examples | Effect |
|------|---------|---------|----------|--------|
| **Zone 1: High Valence / Positive** | Positive | High | Excitement, joy, triumph, surprise delight, celebration | Energises and inspires — great for aspiration, launches, wins |
| **Zone 2: Low Valence / Positive** | Positive | Low | Calm confidence, contentment, gentle reassurance, warmth, trust | Builds trust equity — great for organic-feel, nurture, retention |
| **Zone 3: Low Valence / Negative** | Negative | Low | Subtle worry, quiet dissatisfaction, FOMO, nagging doubt, melancholy | Slow-burn tension — great for problem awareness without alarm |
| **Zone 4: High Valence / Negative** | Negative | High | Fear, urgency, shock, frustration, anger, "you're doing it wrong" | Scroll-stopping shock — great for direct response, but exhausting |

Most brands over-index on Zone 4 (fear/urgency) because performance marketing has
conditioned this behaviour. A psychologically diverse portfolio covers all 4 zones.

#### Dimension 2: Self-Concept Anchor (Identity Layer)

Which version of the customer's identity does this ad speak to?

| Self-Concept | Definition | Mechanism | Example Copy Signal |
|-------------|-----------|-----------|-------------------|
| **Actual Self** | Who they are right now | Problem recognition — makes them aware of current pain | "You're spending 3 hours a day on..." / "Struggling with..." |
| **Ideal Self** | Who they want to become | Aspiration — paints a future worth pursuing | "Imagine waking up to..." / "Become the person who..." |
| **Ought Self** | Who they feel they should be | Duty & responsibility — shifts from guilt to determination | "Do it for them" / "You owe it to yourself" / "It's time to..." |

Most brands (est. 75%) only run Actual Self messaging (pain-point → solution).
Testing all three Self-Concepts gives a bigger performance delta than testing
surface variables because you're testing whether the audience is more motivated
by moving away from pain (Actual), moving toward pleasure (Ideal), or fulfilling
responsibility (Ought).

#### Dimension 3: Language Intensity (Cognitive Friction)

The cognitive friction level of the ad's copy and presentation:

| Intensity | Characteristics | Best For | Trust Effect |
|-----------|----------------|----------|-------------|
| **Low Intensity** | Subtle, suggestive, conversational, organic-feeling, doesn't announce itself as an ad | Cold traffic, organic placements, TOF, building Trust Equity | High — viewer doesn't trigger ad-defense mechanisms |
| **Mid Intensity** | Balanced, clear value statements with moderate assertiveness, some urgency without desperation | Warm traffic, MOF, retargeting | Medium — feels like a recommendation |
| **High Intensity** | Assertive, superlative-heavy, direct-response, all-caps declarations, urgency stacking, exclamation points | Hot traffic, BOF, purchase-ready audiences, flash sales | Low — triggers ad-defense but works for ready-to-buy |

2026 data shows Low Intensity creates "Trust Equity" — higher engagement, longer
watch times, better conversion rates. High Intensity still works for solution-aware
audiences but causes fatigue when overused.

### ICE Scoring for Recommendations

Every recommendation gets an ICE score:
- **Impact** (1-10): How much will this move the needle?
- **Confidence** (1-10): How sure are we this will work?
- **Ease** (1-10): How easy/fast is this to implement?

Total = I + C + E. Prioritise by total score descending.

---

## End-to-End Audit

The audit prompt is the most comprehensive per-ad analysis. It uses every framework.

### Framework

1. **Emotional Identification** — Which of the 4 emotions does this ad target?
   (Achievement, Autonomy, Belonging, Empowerment). Rate primary + secondary.

2. **Story Framework** — Which narrative structure? (StoryBrand, PAS, AIDA, Pixar,
   Before & After, or None/Other). Explain how the ad follows this structure.

3. **Awareness Level** — Problem-Unaware (TOF), Problem-Aware (MOF), or Solution-Aware
   (BOF)? What tells you this?

4. **Angle Classification** — Which of the 8 angles? (Objection Handling, Education,
   Comparison, Social Proof, Routine, B&A Transformation, Founder POV, Myth Busting)

5. **Hook & Attention (first 1-3 seconds)**
   - Transcribe the primary voiced hook (first audio that grabs attention)
   - Describe the visual hook — what stops the scroll?
   - Additional spoken hooks throughout
   - Visual hooks — transitions, animations, on-screen text

6. **Visual Composition**
   - Branding integration — prominence and effectiveness
   - Imagery quality — authentic, staged, relatable, UGC?
   - Editing: pacing, rhythm, cut frequency
   - Text overlays: frequency, font, readability, positioning
   - Colour palette and significance

7. **Audio Analysis**
   - Music selection and mood fit
   - Voiceover style and tone
   - Sound effects and their purpose

8. **CTA Assessment**
   - Strength, clarity, urgency (rate 1-10)
   - Offer type (discount, free trial, limited-time, risk reversal)
   - Soft CTAs — money-back guarantees, PR backing, social proof

9. **Stand-Out Messaging**
   - Primary value proposition
   - Key phrases, statistics, or USPs
   - Secondary reinforcing messages

10. **Target Audience** — Inferred target. How do creative elements serve them?

11. **RAG-Scored Metrics** — Score each available metric against Soar benchmarks
    (🟢🟡🔴). Flag any metrics in 🔴.

12. **Ad Lifecycle Classification** — Testing / Scaling / Retire / Retest. Why?

13. **Performance Hypothesis** — Why is this ad performing at this level? Which
    specific creative elements drive results?

14. **ICE-Scored Recommendations** — 3-5 specific, actionable improvements.
    Each with I/C/E scores and total. Sorted by total descending.

### Attribution & Frequency Flags

If data is available:
- Flag if >60% of conversions are view-through (lower confidence signal)
- Flag if ad frequency >3.5 (creative fatigue warning)
- Note funnel stage distribution balance

### Output Format

Keep each section to 2-4 bullet points maximum. No padding. Every word earns its place.

---

## Persona Gap Analysis

For persona mode, the per-ad prompt focuses on 3-layer persona classification.

### Per-Ad Classification Framework

1. **Product** — Which product is this ad promoting?

2. **Macro Persona** — The headline persona bucket.
   Label + 1-sentence description.

3. **Micro Persona** — The dominant motivator within that macro persona:
   - Primary Desire (what they want)
   - Core Fear (what they're afraid of)
   - Core Belief (what they currently believe)

4. **Angle** — Which of the 8 angles is being used?
   (Objection Handling / Education / Comparison / Social Proof / Routine / B&A /
   Founder POV / Myth Busting)

5. **Emotional ID** — Primary emotion targeted
   (Achievement / Autonomy / Belonging / Empowerment)

6. **Awareness Level** — Problem-Unaware / Problem-Aware / Solution-Aware

7. **Story Framework** — StoryBrand / PAS / AIDA / Pixar / Before & After / None

8. **Creative Format** — UGC / Branded / Hybrid / Static / Educational / Testimonial

9. **Hook Type** — Describe the hook strategy in 1 sentence

10. **Key Message** — Core value proposition for this persona

11. **Problem / Before State** — What problem or pain point does this creative address?

12. **New State** — What transformation does the creative promise?

### Output Format

Structured output for easy parsing:
```
**Product:** [product name]
**Macro Persona:** [label]
**Micro Persona:** [label] — Desire: [x], Fear: [y], Belief: [z]
**Angle:** [one of 8]
**Emotional ID:** [one of 4]
**Awareness Level:** [one of 3]
**Story Framework:** [one of 5 or None]
**Creative Format:** [format]
**Hook Type:** [1 sentence]
**Key Message:** [1 sentence]
**Before State:** [the problem]
**New State:** [the transformation]
```

---

## Valence Deep Dive

For valence mode, the per-ad prompt classifies each ad across the 3-dimensional
psychological matrix: Valence Zone, Self-Concept Anchor, and Language Intensity.

### Per-Ad Classification Framework

1. **Product** — Which product is this ad promoting?

2. **Valence Zone** — Which of the 4 quadrants?
   - Zone 1: High Valence / Positive (excitement, joy, triumph)
   - Zone 2: Low Valence / Positive (calm, warmth, trust, reassurance)
   - Zone 3: Low Valence / Negative (subtle worry, nagging doubt, quiet FOMO)
   - Zone 4: High Valence / Negative (fear, urgency, shock, frustration)
   - Explain: What specific creative elements (visuals, audio, copy, pacing) create
     this emotional charge? Is it consistent throughout or does it shift zones?

3. **Self-Concept Anchor** — Which identity layer?
   - Actual Self (problem recognition — who they are now)
   - Ideal Self (aspiration — who they want to become)
   - Ought Self (duty/responsibility — who they should be)
   - Explain: What in the copy/visual tells you which self-concept is being addressed?
     Quote the specific language or describe the visual cues.

4. **Language Intensity** — What level of cognitive friction?
   - Low Intensity (subtle, conversational, organic-feeling)
   - Mid Intensity (balanced, clear but not aggressive)
   - High Intensity (assertive, superlative-heavy, urgency-stacking)
   - Explain: Rate the intensity on a 1-10 scale. What specific copy elements drive
     the rating? (superlatives, caps, exclamation points, urgency words, conversational
     tone, etc.)

5. **Psychological Matrix Position** — Express as a coordinate:
   `[Zone X] × [Self-Concept] × [Intensity Level]`
   Example: `Zone 4 × Actual Self × High Intensity`

6. **Trust Equity Assessment** — Does this ad build or spend Trust Equity?
   - Build: organic-feeling, low friction, viewer doesn't feel "sold to"
   - Spend: aggressive, high friction, viewer immediately knows it's an ad
   - Neutral: balanced approach

7. **Emotional ID** — Primary emotion (Achievement / Autonomy / Belonging / Empowerment)

8. **Awareness Level** — Problem-Unaware / Problem-Aware / Solution-Aware

9. **Story Framework** — StoryBrand / PAS / AIDA / Pixar / Before & After / None

10. **Creative Format** — UGC / Branded / Hybrid / Static / Educational / Testimonial

11. **Hook Type** — Describe the hook strategy in 1 sentence

12. **Key Message** — Core value proposition in 1 sentence

### Output Format

Structured output for easy parsing:
```
**Product:** [product name]
**Valence Zone:** [Zone 1/2/3/4] — [High/Low Valence] / [Positive/Negative]
**Valence Reasoning:** [1-2 sentences on what creates this emotional charge]
**Self-Concept:** [Actual Self / Ideal Self / Ought Self]
**Self-Concept Reasoning:** [1-2 sentences with specific copy/visual evidence]
**Language Intensity:** [Low / Mid / High] — Intensity Score: [1-10]
**Intensity Reasoning:** [1-2 sentences on specific copy elements]
**Matrix Position:** [Zone X] × [Self-Concept] × [Intensity]
**Trust Equity:** [Build / Spend / Neutral]
**Emotional ID:** [one of 4]
**Awareness Level:** [one of 3]
**Story Framework:** [one of 5 or None]
**Creative Format:** [format]
**Hook Type:** [1 sentence]
**Key Message:** [1 sentence]
```

---

## Performance Correlation

This prompt connects creative elements to metric outcomes using Soar's frameworks.

### Framework

1. **Classification**
   - Format: UGC / Branded / Hybrid / Static
   - Production: Lo-fi / Mid / High
   - Content type: Testimonial / Demo / Educational / Problem-solution / Lifestyle
   - Emotional ID: Achievement / Autonomy / Belonging / Empowerment
   - Story Framework: StoryBrand / PAS / AIDA / Pixar / B&A / None
   - Awareness Level: Problem-Unaware / Problem-Aware / Solution-Aware
   - Angle: [one of 8-angle taxonomy]

2. **Hook Analysis**
   - Hook type and first 3 seconds description
   - Thumbstop potential (1-10) with reasoning

3. **Engagement Drivers**
   - What keeps someone watching past 3s?
   - Pattern interrupts used
   - Information density: sparse / moderate / dense

4. **CTA Strength** (1-10 with reasoning)

5. **RAG Metric Scoring**
   - Score each metric against Soar benchmarks (🟢🟡🔴)
   - Flag any 🔴 metrics with likely creative cause

6. **Performance Verdict**
   - Compare CPC/CTR/CPM against batch averages AND Soar benchmarks
   - Which creative elements are driving performance? Be specific.
   - Attribution flag: if data shows heavy view-through, note this

7. **Ad Lifecycle** — Testing / Scaling / Retire / Retest with reasoning

8. **One Key Takeaway** for the creative team

---

## Persona Synthesis

Cross-ad synthesis prompt used AFTER all individual ads have been analysed in persona mode.

### Framework

1. **Persona Spend Allocation Table**
   Group all ads into persona buckets. For each persona:
   | Persona (Macro → Micro) | # Ads | Total Spend | % of Total | Avg CPC | Avg CTR | Dominant Angle | Dominant Emotion | Products |

2. **Awareness Level Distribution**
   | Awareness Level | # Ads | % Spend | Dominant Formats |
   Flag if any level has 0% coverage (the Kurk finding).

3. **Story Framework Distribution**
   Which frameworks are in use? Which are untested?

4. **Spend Balance Assessment**
   - Which personas get most/least investment?
   - Are high-performing segments under-invested?
   - Frequency health per persona (if data available)

5. **Creative Gap Analysis**
   - Personas with <3 creative variants (fatigue risk)
   - Missing angles per persona (which of the 8 are untested?)
   - Missing creative formats per persona
   - Persona × Awareness Level gaps (e.g., no TOF creative for a key persona)
   - Persona × Product combinations with no creative

6. **Cross-Persona Patterns**
   - Which angles/emotions/frameworks work across multiple personas?
   - Which are persona-specific?
   - Formats that could be adapted to underserved segments

7. **ICE-Scored Recommendations**
   Top 5 strategic recommendations. Each with:
   - Description
   - Rationale
   - Impact (1-10), Confidence (1-10), Ease (1-10)
   - ICE Total
   Sort by ICE Total descending.

### Output Format

Start with the spend allocation table, then awareness distribution, then narrative
analysis. Keep it strategic and actionable.

---

## Valence Synthesis

Cross-ad synthesis prompt used AFTER all individual ads have been analysed in valence mode.
This is the strategic payoff — mapping the psychological landscape to find diversity gaps.

### Framework

1. **Psychological Matrix Heatmap**
   Create a visual matrix showing ad distribution. For each cell:
   | | Actual Self | Ideal Self | Ought Self |
   |---|---|---|---|
   | **Zone 1** (High+) | X ads / $Y spend | ... | ... |
   | **Zone 2** (Low+) | ... | ... | ... |
   | **Zone 3** (Low-) | ... | ... | ... |
   | **Zone 4** (High-) | ... | ... | ... |

   Flag cells with 0 ads as **UNMAPPED TERRITORY** — these are the biggest strategic
   opportunities. Flag cells with 5+ ads as **SATURATED** — diminishing returns.

2. **Valence Zone Distribution**
   | Zone | # Ads | % Spend | Avg CPC | Avg CTR | Dominant Self-Concept | Dominant Intensity |
   Flag which zones are over/under-represented. Most brands over-index Zone 4.

3. **Self-Concept Distribution**
   | Self-Concept | # Ads | % Spend | Avg CPC | Avg CTR | Dominant Zone | Dominant Intensity |
   Flag if >60% of ads target Actual Self (the typical imbalance).

4. **Language Intensity Distribution**
   | Intensity | # Ads | % Spend | Avg CPC | Avg CTR | Avg Intensity Score | Dominant Zone |
   Flag if >50% of ads are High Intensity (audience fatigue risk).

5. **Trust Equity Balance**
   - How many ads Build vs Spend Trust Equity?
   - Is the portfolio net-positive or net-negative on Trust Equity?
   - Flag if >70% of ads Spend Trust Equity (unsustainable — audience will tune out)

6. **Psychological Diversity Score**
   Rate the portfolio's psychological diversity on a scale:
   - **12/12 cells covered** = Exceptional diversity
   - **8-11 cells covered** = Good diversity with gaps
   - **5-7 cells covered** = Moderate — significant blind spots
   - **1-4 cells covered** = Poor — operating in a narrow psychological lane

7. **Biggest Opportunity Zones**
   For each unmapped or under-served matrix cell, describe:
   - What a creative brief for this zone would look like
   - Which existing ad could be adapted to fill this gap
   - Expected audience response based on the theory

8. **Cross-Zone Performance Patterns**
   - Which matrix positions outperform? Which underperform?
   - Is there a correlation between zone and funnel stage performance?
   - Do certain Self-Concept × Intensity combinations show standout metrics?

9. **ICE-Scored Recommendations**
   Top 5 strategic recommendations for improving psychological diversity.
   For EACH:
   | # | Recommendation | Matrix Gap Addressed | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Total |
   Sort by ICE Total descending.

### Output Format

Lead with the Psychological Matrix Heatmap and Diversity Score. Then zone distributions.
Then opportunity zones with specific creative brief suggestions. Close with ICE
recommendations. Keep it strategic — this should reshape how the team thinks about
creative production, not just their next 3 ads.

---

## Framework Audit (Selective)

A slimmed-down version of the full end-to-end audit used in the Growth Strategy Audit.
Extracts only the most informative framework classifications and messaging analysis —
no visual composition, audio analysis, or full CTA deep-dive.

### Framework

1. **Emotional ID** — Primary + secondary emotion (Achievement / Autonomy / Belonging / Empowerment)
2. **Story Framework** — Which structure? (StoryBrand / PAS / AIDA / Pixar / Before & After / None). 1-sentence explanation.
3. **Awareness Level** — Problem-Unaware (TOF) / Problem-Aware (MOF) / Solution-Aware (BOF). What signals this?
4. **Angle** — Which of the 8 angles?
5. **Hook Analysis** — Transcribe the primary hook (first 3 seconds). Describe the visual hook.
6. **Key Message** — Primary value proposition in 1 sentence.
7. **Stand-Out Messaging** — Notable phrases, statistics, or USPs (2-3 bullets max).

### Output Format

Structured output for easy parsing:
```
**Product:** [product name]
**Emotional ID (Primary):** [one of 4]
**Emotional ID (Secondary):** [one of 4 or None]
**Story Framework:** [one of 5 or None] — [1-sentence explanation]
**Awareness Level:** [one of 3] — [1-sentence evidence]
**Angle:** [one of 8]
**Hook (Voiced):** [transcription of first audio hook]
**Hook (Visual):** [1-sentence description of visual hook]
**Key Message:** [1 sentence]
**Stand-Out Messaging:** [2-3 notable phrases/USPs]
```

---

## Growth Strategy Opportunity Synthesis

Cross-analysis synthesis prompt used AFTER all four analysis passes (correlation, valence,
persona, framework) and both synthesis reports (valence + persona) are complete. This is
the strategic capstone of the Growth Strategy Creative Audit.

### Purpose

Combine findings from all analysis dimensions into a single, categorised list of strategic
opportunities. Each opportunity should be actionable and framed for subsequent Reddit
deep-dive research.

### Framework

1. **Executive Summary**
   Write 2-3 paragraphs summarising the overall state of the creative portfolio:
   - How many ads analysed, total spend, top performer ratio
   - Headline findings from each dimension (correlation, valence, persona, framework)
   - The single most important strategic insight

2. **Categorised Opportunity List**
   For EACH opportunity identified across all analysis passes, categorise and describe:

   | # | Category | Opportunity | Evidence | ICE Score | Reddit Research Prompt |
   |---|----------|-------------|----------|-----------|----------------------|

   Categories:
   - **Valence Gap** — Unmapped psychological zones in the valence matrix
   - **Persona Gap** — Under-served, missing, or over-saturated personas
   - **Creative Diversity** — Format, style, or production variety gaps
   - **Framework Gap** — Untested story frameworks, awareness levels, or angles
   - **Messaging Gap** — Missing hooks, value propositions, or language styles
   - **Fatigue Signal** — High frequency creatives with declining performance
   - **Performance Correlation** — Creative elements strongly linked to metrics

   For each opportunity:
   - **Description**: What the gap/opportunity is (2-3 sentences)
   - **Evidence**: Which specific data points from the analysis support this (reference ad names, metrics, matrix positions)
   - **ICE Score**: Impact (1-10) + Confidence (1-10) + Ease (1-10) = Total
   - **Reddit Research Prompt**: A specific search query or topic to explore on Reddit to understand the messaging style, audience language, and framework that would work for this opportunity. Frame it as: "Search Reddit for [topic/subreddit] to understand [what we need to learn] for [how it informs the creative brief]."

3. **Opportunity Priority Matrix**
   Rank all opportunities by ICE Total descending. Group the top 5 as "Priority Opportunities"
   and the rest as "Secondary Opportunities."

4. **Next Steps for the Strategist**
   Write 3-4 bullet points telling the user what to do next:
   - Review and filter the opportunities above
   - Select 3-5 priority opportunities for Reddit deep-dive
   - Use the Reddit Research Prompts to mine audience language and messaging frameworks
   - Use Reddit findings to write creative briefs for each selected opportunity

### Output Format

Lead with the Executive Summary. Then the full categorised opportunity table sorted by ICE.
Then the Next Steps section. This report should feel like a strategic brief that directly
sets up the next phase of work — it's not an end in itself, it's the bridge to Reddit
research and creative brief writing.

---

## Metrics-Enriched Add-on

When `--metrics-enriched` is active, append this section to any prompt:

```
## Performance-Creative Cross-Reference

You have access to this ad's performance metrics. Use them to enrich your analysis:

- Calculate thumbstop ratio: 3-second video views / impressions (if video)
- Compare this ad's metrics against BOTH the batch average AND Soar's benchmarks:
  - TSR: 🟢 >30% | 🟡 20-30% | 🔴 <20%
  - Hold Rate (15s): 🟢 >45% | 🟡 30-45% | 🔴 <30%
  - Hold Rate (30s): 🟢 >30% | 🟡 20-30% | 🔴 <20%
  - CTR: 🟢 >1% | 🟡 0.5-1% | 🔴 <0.5%
  - Frequency: 🟢 <2.5 | 🟡 2.5-3.5 | 🔴 >3.5
- RAG score each metric
- Identify which specific creative elements likely drive above/below benchmark performance
- Note: high view-through attribution ratio (>60%) means lower confidence in creative driving conversions

Batch averages for reference:
{batch_averages}
```

---

## Context-Enriched Add-on

When `--context-file` provides client-specific context, append:

```
## CLIENT CONTEXT

The following context comes from the client's research documentation. Use it to
make your analysis client-specific rather than generic.

{context_block}

IMPORTANT: Classify ads against the EXISTING personas listed above when possible.
Only suggest a new persona if the ad clearly doesn't fit any existing one. Check
benefit claims against the documented benefits. Assess strategic alignment against
the Strategic Thesis.
```
