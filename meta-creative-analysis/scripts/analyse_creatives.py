#!/usr/bin/env python3
"""
Meta Creative Analysis Pipeline
Pulls top-spending ads from Meta Marketing API, downloads creative assets,
uploads to Gemini Files API for multimodal analysis, and generates reports.

Analysis is grounded in Soar Group's creative strategy frameworks:
  - Emotional Identification (Achievement, Autonomy, Belonging, Empowerment)
  - Story Frameworks (StoryBrand, PAS, AIDA, Pixar, Before & After)
  - Awareness Levels (Problem-Unaware, Problem-Aware, Solution-Aware)
  - 8-Angle Taxonomy
  - RAG-scored KPI benchmarks
  - Ad Lifecycle Classification (Testing, Scaling, Retire, Retest)
  - 3-Layer Persona Taxonomy (Macro → Micro → Angle)
  - Valence Deep Dive (Valence Zone × Self-Concept × Language Intensity)
  - ICE-scored recommendations

Supports multiple analysis modes:
  - audit: End-to-end creative audit (deep per-ad analysis)
  - persona: Persona & spend gap analysis (classification + synthesis)
  - valence: Valence Deep Dive (psychological diversity matrix + synthesis)
  - correlation: Performance-creative correlation
  - growth-strategy: Growth Strategy Creative Audit (multi-pass: correlation + valence + persona + framework → opportunity synthesis)
  - custom: User-defined analysis focus

Usage:
  python3 analyse_creatives.py \
    --limit 10 \
    --date-preset last_7d \
    --analysis-type audit \
    --output ./creative_analysis
"""

import argparse
import json
import os
import sys
import time
import re
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests --break-system-packages")
    sys.exit(1)

def _load_key(name):
    kf = os.path.join(os.path.expanduser("~"), ".claude", "api_keys.json")
    if os.path.exists(kf):
        with open(kf) as f:
            return json.load(f).get(name, "")
    return ""
# ── Configuration ──────────────────────────────────────────────────────────
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", _load_key("meta_access_token"))
AD_ACCOUNT_ID = os.environ.get("AD_ACCOUNT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", _load_key("gemini_api_key"))
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
META_API_VERSION = os.environ.get("META_API_VERSION", "v21.0")
META_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"

# ── Soar KPI Benchmarks ───────────────────────────────────────────────────
SOAR_BENCHMARKS = {
    "tsr": {"green": 0.30, "amber": 0.20, "label": "TSR (Thumbstop Rate)"},
    "hold_rate_15s": {"green": 0.45, "amber": 0.30, "label": "Hold Rate (15s)"},
    "hold_rate_30s": {"green": 0.30, "amber": 0.20, "label": "Hold Rate (30s)"},
    "ctr": {"green": 1.0, "amber": 0.5, "label": "CTR"},
    "frequency": {"green": 2.5, "amber": 3.5, "label": "Frequency (30d)"},
}

# ── Soar Framework Constants ──────────────────────────────────────────────
SOAR_FRAMEWORKS_BLOCK = """
## SOAR CREATIVE STRATEGY FRAMEWORKS

Use these frameworks to classify and analyse this ad:

### Emotional Identification
Every ad targets one or more of these 4 core emotions:
- **Achievement** — Desire to succeed, improve, reach goals (progress, mastery, results)
- **Autonomy** — Desire for control, independence, freedom (choice, simplicity)
- **Belonging** — Desire to connect, fit in, be part of something (community, validation)
- **Empowerment** — Desire to feel capable, confident, in charge (knowledge, transformation)

### Story Frameworks
Classify which narrative structure the ad follows:
- **StoryBrand** — Hero (customer) has problem → Guide (brand) offers plan → Success
- **PAS** — Problem → Agitate → Solution
- **AIDA** — Attention → Interest → Desire → Action
- **Pixar** — Once upon a time... Every day... One day... Because of that... Until finally...
- **Before & After** — Life before → Transformation → Life after
- **None** — No clear narrative structure

### Awareness Level (Funnel Stage)
- **Problem-Unaware (TOF)** — Viewer doesn't know they have a problem. Creative educates, disrupts.
- **Problem-Aware (MOF)** — Viewer knows the problem, not the solution. Creative agitates, presents solution.
- **Solution-Aware (BOF)** — Viewer knows solutions exist, comparing options. Creative differentiates, proves.

### 8-Angle Taxonomy
Classify the ad's messaging angle:
1. Objection Handling — Pre-empts a common purchase objection
2. Education / Lightbulb — Teaches something new that reframes the category
3. Comparison / Us vs Them — Direct or indirect comparison to alternatives
4. Social Proof — Reviews, testimonials, UGC, press, stats
5. Routine / Day-in-Life — Product integrated into daily life
6. Before → After Transformation — Visual or narrative transformation
7. Founder / Insider POV — Behind-the-scenes, founder story, brand mission
8. Myth Busting — Challenges a common misconception

### KPI Benchmarks (RAG Scoring)
Score metrics against these thresholds:
- TSR: 🟢 >30% | 🟡 20-30% | 🔴 <20%
- Hold Rate (15s): 🟢 >45% | 🟡 30-45% | 🔴 <30%
- Hold Rate (30s): 🟢 >30% | 🟡 20-30% | 🔴 <20%
- CTR: 🟢 >1% | 🟡 0.5-1% | 🔴 <0.5%
- Frequency (30d): 🟢 <2.5 | 🟡 2.5-3.5 | 🔴 >3.5

### Ad Lifecycle Classification
- **Testing** — <3-5 days live, insufficient data. Action: Monitor.
- **Scaling** — Exceeding benchmarks, consistent. Action: Increase budget, iterate.
- **Retire** — Below benchmarks, no recovery. Action: Kill, learn.
- **Retest** — Promising on one metric, failing another. Action: Iterate weak element.
"""


# ── Helpers ────────────────────────────────────────────────────────────────

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def safe_filename(name, max_len=60):
    name = re.sub(r'[^\w\s-]', '', name).strip()
    name = re.sub(r'[\s]+', '_', name)
    return name[:max_len] if name else "unnamed"


def rag_score(value, green_threshold, amber_threshold, higher_is_better=True):
    """Return RAG emoji based on thresholds."""
    try:
        v = float(value)
    except (ValueError, TypeError):
        return "⚪"
    if higher_is_better:
        if v >= green_threshold:
            return "🟢"
        elif v >= amber_threshold:
            return "🟡"
        else:
            return "🔴"
    else:  # lower is better (e.g., frequency)
        if v <= green_threshold:
            return "🟢"
        elif v <= amber_threshold:
            return "🟡"
        else:
            return "🔴"


def load_context_file(filepath):
    """Load optional client context file."""
    if not filepath or not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"Failed to load context file: {e}", "WARN")
        return None


def build_context_block(context):
    """Build a context string from client context data."""
    if not context:
        return ""
    parts = []

    if context.get("personas"):
        parts.append("### Existing Personas (classify ads against these FIRST)")
        for p in context["personas"]:
            parts.append(f"**{p.get('macro_label', 'Unknown')}**")
            for mp in p.get("micro_personas", []):
                parts.append(f"  - {mp.get('label', '?')}: Desire={mp.get('primary_desire', '?')}, "
                             f"Fear={mp.get('core_fear', '?')}, Belief={mp.get('core_belief', '?')}")

    if context.get("benefits"):
        parts.append("\n### Documented Product Benefits")
        for b in context["benefits"]:
            parts.append(f"  - {b}")

    if context.get("strategic_thesis"):
        parts.append(f"\n### Strategic Thesis\n{context['strategic_thesis']}")

    if context.get("kpi_targets"):
        parts.append("\n### Client-Specific KPI Targets")
        for k, v in context["kpi_targets"].items():
            parts.append(f"  - {k}: {v}")

    if not parts:
        return ""

    block = "\n".join(parts)
    return f"""

## CLIENT CONTEXT (from research documentation)
{block}

IMPORTANT: Classify ads against the EXISTING personas listed above when possible.
Only suggest a new persona if the ad clearly doesn't fit any existing one.
Check benefit claims against documented benefits. Assess alignment with Strategic Thesis.
"""


# ── Step 1: Pull top ads by spend ──────────────────────────────────────────

def fetch_top_ads(limit=10, date_preset="last_7d"):
    """Fetch top ads sorted by spend descending."""
    log(f"Fetching top {limit} ads by spend (date_preset={date_preset})...")

    # Use the insights endpoint directly — it's more reliable than the complex
    # nested fields query on the /ads endpoint which can hit syntax errors.
    url = f"{META_BASE_URL}/{AD_ACCOUNT_ID}/insights"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "fields": "ad_id,ad_name,spend,impressions,clicks,cpc,cpm,ctr,actions,cost_per_action_type",
        "date_preset": date_preset,
        "level": "ad",
        "sort": "spend_descending",
        "limit": min(limit, 100),  # API max per page
    }

    all_insights = []
    next_url = None

    while len(all_insights) < limit:
        if next_url:
            resp = requests.get(next_url, timeout=60)
        else:
            resp = requests.get(url, params=params, timeout=60)

        if resp.status_code != 200:
            log(f"Insights API error {resp.status_code}: {resp.text[:300]}", "ERROR")
            return []

        data = resp.json()
        insights = data.get("data", [])
        all_insights.extend(insights)

        paging = data.get("paging", {})
        next_url = paging.get("next")
        if not next_url or not insights:
            break

    all_insights = all_insights[:limit]
    log(f"Got {len(all_insights)} ad insights (pre-dedup)")

    # Deduplicate by ad_id — the insights endpoint can return the same ad
    # multiple times (e.g. different date breakdowns). Keep the first (highest spend).
    seen_ids = set()
    unique_insights = []
    for insight in all_insights:
        aid = insight.get("ad_id")
        if aid and aid not in seen_ids:
            seen_ids.add(aid)
            unique_insights.append(insight)
    if len(unique_insights) < len(all_insights):
        log(f"Deduplicated: {len(all_insights)} → {len(unique_insights)} unique ads")
    all_insights = unique_insights

    log(f"Got {len(all_insights)} unique ad insights")

    # Fetch creative details for each ad
    ads = []
    for i, insight in enumerate(all_insights):
        ad_id = insight.get("ad_id")
        if not ad_id:
            continue

        ad_url = f"{META_BASE_URL}/{ad_id}"
        ad_params = {
            "access_token": META_ACCESS_TOKEN,
            "fields": "name,status,effective_status,creative{id,name,title,body,image_url,thumbnail_url,object_story_spec,asset_feed_spec}",
        }

        try:
            ad_resp = requests.get(ad_url, params=ad_params, timeout=30)
            if ad_resp.status_code == 200:
                ad_data = ad_resp.json()
                ad_data["insights"] = {"data": [insight]}
                ads.append(ad_data)
                if (i + 1) % 10 == 0 or i == 0:
                    log(f"  Fetched creative {i+1}/{len(all_insights)}: {ad_data.get('name', 'unnamed')[:50]}")
            else:
                log(f"  Failed to fetch ad {ad_id}: {ad_resp.status_code}", "WARN")
                ads.append({
                    "id": ad_id,
                    "name": insight.get("ad_name", f"Ad {ad_id}"),
                    "insights": {"data": [insight]},
                })
        except Exception as e:
            log(f"  Error fetching ad {ad_id}: {e}", "WARN")
            ads.append({
                "id": ad_id,
                "name": insight.get("ad_name", f"Ad {ad_id}"),
                "insights": {"data": [insight]},
            })

    log(f"Fetched creative details for {len(ads)} ads")
    return ads


# ── Step 2: Resolve asset URLs ─────────────────────────────────────────────

def resolve_asset_urls(ad):
    """Extract video/image URLs from ad creative data."""
    creative = ad.get("creative", {})
    assets = []

    oss = creative.get("object_story_spec", {})
    video_data = oss.get("video_data", {})
    video_id = video_data.get("video_id")

    if video_id:
        video_url = get_video_source_url(video_id)
        if video_url:
            assets.append({
                "type": "video",
                "url": video_url,
                "video_id": video_id,
                "filename": f"{safe_filename(ad.get('name', 'video'))}_{video_id}.mp4",
            })

    link_data = oss.get("link_data", {})
    if not video_id and link_data:
        for child in link_data.get("child_attachments", []):
            vid = child.get("video_id")
            if vid:
                video_url = get_video_source_url(vid)
                if video_url:
                    assets.append({
                        "type": "video", "url": video_url, "video_id": vid,
                        "filename": f"{safe_filename(ad.get('name', 'video'))}_{vid}.mp4",
                    })

    image_url = creative.get("image_url") or creative.get("thumbnail_url")
    if not image_url and link_data:
        image_url = link_data.get("picture")

    if image_url and not assets:
        ext = "png" if ".png" in image_url.lower() else "jpg"
        assets.append({
            "type": "image", "url": image_url,
            "filename": f"{safe_filename(ad.get('name', 'image'))}.{ext}",
        })

    thumb = creative.get("thumbnail_url")
    if thumb and not assets:
        assets.append({
            "type": "image", "url": thumb,
            "filename": f"{safe_filename(ad.get('name', 'thumb'))}_thumb.jpg",
        })

    afs = creative.get("asset_feed_spec", {})
    if afs and not assets:
        for video_item in afs.get("videos", []):
            vid = video_item.get("video_id")
            if vid:
                video_url = get_video_source_url(vid)
                if video_url:
                    assets.append({
                        "type": "video", "url": video_url, "video_id": vid,
                        "filename": f"{safe_filename(ad.get('name', 'video'))}_{vid}.mp4",
                    })
                    break
        for img_item in afs.get("images", []):
            img_hash = img_item.get("hash")
            if img_hash and not assets:
                img_url = get_image_url_from_hash(img_hash)
                if img_url:
                    assets.append({
                        "type": "image", "url": img_url,
                        "filename": f"{safe_filename(ad.get('name', 'image'))}_{img_hash[:8]}.jpg",
                    })
                    break

    return assets


def get_video_source_url(video_id):
    """Get video source URL from Meta API."""
    url = f"{META_BASE_URL}/{video_id}"
    params = {"access_token": META_ACCESS_TOKEN, "fields": "source,length,title"}
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("source")
        else:
            log(f"    Video {video_id} fetch failed: {resp.status_code}", "WARN")
    except Exception as e:
        log(f"    Video {video_id} error: {e}", "WARN")
    return None


def get_image_url_from_hash(image_hash):
    """Try to get image URL from ad image hash."""
    url = f"{META_BASE_URL}/{AD_ACCOUNT_ID}/adimages"
    params = {"access_token": META_ACCESS_TOKEN, "hashes": json.dumps([image_hash])}
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            for key, val in data.items():
                img_url = val.get("url") or val.get("url_128") or val.get("permalink_url")
                if img_url:
                    return img_url
    except Exception as e:
        log(f"    Image hash lookup error: {e}", "WARN")
    return None


# ── Step 3: Download files ──────────────────────────────────────────────────

def download_asset(asset, output_dir):
    """Download a media file."""
    filepath = os.path.join(output_dir, asset["filename"])
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        asset["local_path"] = filepath
        return True
    try:
        resp = requests.get(asset["url"], timeout=120, stream=True, allow_redirects=True)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            log(f"    Downloaded {asset['type']} ({size_mb:.1f}MB)")
            asset["local_path"] = filepath
            return True
        else:
            log(f"    Download failed: HTTP {resp.status_code}", "WARN")
            return False
    except Exception as e:
        log(f"    Download error: {e}", "WARN")
        return False


# ── Step 4: Upload to Gemini Files API ──────────────────────────────────────

def upload_to_gemini(filepath, mime_type=None):
    """Upload a file to Gemini Files API using resumable upload."""
    if not mime_type:
        ext = os.path.splitext(filepath)[1].lower()
        mime_map = {
            ".mp4": "video/mp4", ".mov": "video/quicktime",
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
        }
        mime_type = mime_map.get(ext, "application/octet-stream")

    file_size = os.path.getsize(filepath)
    display_name = os.path.basename(filepath)

    # Step 1: Initiate resumable upload
    init_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={GEMINI_API_KEY}"
    init_headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(file_size),
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(init_url, headers=init_headers,
                             json={"file": {"display_name": display_name}}, timeout=60)

        if resp.status_code not in (200, 201):
            log(f"    Gemini upload init failed: {resp.status_code}", "ERROR")
            return None

        upload_url = None
        for key, val in resp.headers.items():
            if key.lower() == "x-goog-upload-url":
                upload_url = val
                break

        if not upload_url:
            log("    No upload URL in response", "ERROR")
            return None

        # Step 2: Upload bytes
        with open(filepath, 'rb') as f:
            file_bytes = f.read()

        upload_headers = {
            "X-Goog-Upload-Command": "upload, finalize",
            "X-Goog-Upload-Offset": "0",
            "Content-Length": str(file_size),
        }

        resp2 = requests.post(upload_url, headers=upload_headers, data=file_bytes, timeout=300)
        if resp2.status_code not in (200, 201):
            log(f"    Gemini upload failed: {resp2.status_code}", "ERROR")
            return None

        file_info = resp2.json().get("file", {})
        state = file_info.get("state", "")

        # Step 3: Poll for ACTIVE state
        if state != "ACTIVE" and file_info.get("uri"):
            file_info = poll_gemini_file(file_info["uri"]) or file_info

        return file_info

    except Exception as e:
        log(f"    Gemini upload error: {e}", "ERROR")
        return None


def poll_gemini_file(file_uri, max_wait=120, interval=5):
    """Poll Gemini file until ACTIVE."""
    file_name = file_uri.split("/")[-1]
    poll_url = f"https://generativelanguage.googleapis.com/v1beta/files/{file_name}?key={GEMINI_API_KEY}"

    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = requests.get(poll_url, timeout=30)
            if resp.status_code == 200:
                info = resp.json()
                state = info.get("state", "")
                if state == "ACTIVE":
                    return info
                elif state == "FAILED":
                    log("    File processing FAILED", "ERROR")
                    return None
        except Exception:
            pass
        time.sleep(interval)

    log("    Timed out waiting for ACTIVE", "WARN")
    return None


# ── Step 5: Build analysis prompts ──────────────────────────────────────────

def extract_ad_copy(ad):
    """Extract ad copy text from creative data."""
    creative = ad.get("creative", {})
    oss = creative.get("object_story_spec", {})

    body = creative.get("body", "") or ""
    title = creative.get("title", "") or ""

    link_data = oss.get("link_data", {})
    if not body and link_data:
        body = link_data.get("message", "") or link_data.get("description", "") or ""
    if not title and link_data:
        title = link_data.get("name", "") or ""

    video_data = oss.get("video_data", {})
    if not body and video_data:
        body = video_data.get("message", "") or ""
    if not title and video_data:
        title = video_data.get("title", "") or ""

    return body, title


def format_metrics_block(insights, batch_avgs=None):
    """Format the metrics section for prompts with RAG scoring."""
    spend = insights.get("spend", "N/A")
    impressions = insights.get("impressions", "N/A")
    clicks = insights.get("clicks", "N/A")
    cpc = insights.get("cpc", "N/A")
    cpm = insights.get("cpm", "N/A")
    ctr = insights.get("ctr", "N/A")

    # RAG score CTR
    ctr_rag = rag_score(ctr, 1.0, 0.5, higher_is_better=True)

    actions_str = ""
    for a in (insights.get("actions") or [])[:8]:
        actions_str += f"\n  - {a.get('action_type', '?')}: {a.get('value', '?')}"

    cpa_str = ""
    for c in (insights.get("cost_per_action_type") or [])[:8]:
        cpa_str += f"\n  - {c.get('action_type', '?')}: ${c.get('value', '?')}"

    block = f"""## PERFORMANCE METRICS
- Spend: ${spend}
- Impressions: {impressions}
- Clicks: {clicks}
- CPC: ${cpc}
- CPM: ${cpm}
- CTR: {ctr}% {ctr_rag}
- Actions: {actions_str or 'N/A'}
- Cost per Action: {cpa_str or 'N/A'}"""

    if batch_avgs:
        block += f"""

## BATCH AVERAGES (for comparison)
- Avg CPC: ${batch_avgs.get('avg_cpc', 'N/A')}
- Avg CPM: ${batch_avgs.get('avg_cpm', 'N/A')}
- Avg CTR: {batch_avgs.get('avg_ctr', 'N/A')}%
- Total Spend: ${batch_avgs.get('total_spend', 'N/A')}"""

    return block


def build_audit_prompt(ad, has_media, insights, batch_avgs=None, context_block=""):
    """End-to-end creative audit prompt using Soar frameworks."""
    body, title = extract_ad_copy(ad)
    metrics = format_metrics_block(insights, batch_avgs)

    media_section = ""
    if has_media:
        media_section = """
Analyse the attached creative file in detail using the Soar frameworks below.
"""
    else:
        media_section = "\nNo media file available — analyse based on copy, metadata, and metrics only.\n"

    return f"""You are an expert paid social creative strategist at Soar Group.
Analyse this Meta ad using the frameworks below.

## AD METADATA
- Ad Name: {ad.get('name', 'Unknown')}
- Status: {ad.get('effective_status', ad.get('status', 'Unknown'))}
- Ad Copy: {body or 'N/A'}
- Headline: {title or 'N/A'}

{metrics}
{SOAR_FRAMEWORKS_BLOCK}
{media_section}
{context_block}

## YOUR ANALYSIS — provide ALL of the following:

1. **Emotional ID**: Primary emotion (Achievement / Autonomy / Belonging / Empowerment). Note secondary if present.
2. **Story Framework**: Which structure? (StoryBrand / PAS / AIDA / Pixar / Before & After / None). Briefly explain how.
3. **Awareness Level**: Problem-Unaware (TOF) / Problem-Aware (MOF) / Solution-Aware (BOF). What signals this?
4. **Angle**: Which of the 8 angles? (Objection Handling / Education / Comparison / Social Proof / Routine / B&A Transformation / Founder POV / Myth Busting)
5. **Hook & Attention** (first 1-3 seconds):
   - Transcribe the primary voiced hook
   - Describe the visual hook — what stops the scroll?
   - Note additional hooks throughout
6. **Visual Composition**: Branding integration, imagery quality (UGC/staged/authentic), editing pace, text overlays, colour palette
7. **Audio**: Music, voiceover style, sound effects
8. **CTA Assessment**: Strength (1-10), offer type, soft CTAs (risk reversals, social proof)
9. **Stand-Out Messaging**: Primary value prop, key USPs, notable phrases/stats
10. **Target Audience**: Who is this for? How do creative elements serve them?
11. **RAG Metrics**: Score each available metric against Soar benchmarks (🟢🟡🔴). Flag any 🔴.
12. **Ad Lifecycle**: Testing / Scaling / Retire / Retest — with reasoning.
13. **Performance Hypothesis**: Why is this ad performing at this level? Which creative elements drive results?
14. **Recommendations** (3-5, ICE-scored):
    For each: Description | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Total
    Sort by ICE Total descending.

Keep each section to 2-4 bullet points. Be direct and specific — no filler."""


def build_persona_prompt(ad, has_media, insights, context_block=""):
    """Persona classification prompt using 3-layer taxonomy."""
    body, title = extract_ad_copy(ad)
    metrics = format_metrics_block(insights)

    media_note = "Analyse the attached creative to inform your classification." if has_media else ""

    return f"""Classify this Meta ad using Soar Group's 3-layer persona taxonomy. {media_note}

## AD METADATA
- Ad Name: {ad.get('name', 'Unknown')}
- Ad Copy: {body or 'N/A'}
- Headline: {title or 'N/A'}

{metrics}
{SOAR_FRAMEWORKS_BLOCK}
{context_block}

Respond in EXACTLY this format:

**Product:** [product name extracted from ad name/copy]
**Macro Persona:** [headline persona label, e.g. "Sceptical Steven", "Health-Conscious Hannah"]
**Micro Persona:** [specific motivator label] — Desire: [what they want], Fear: [what they fear], Belief: [what they currently believe]
**Angle:** [one of: Objection Handling / Education / Comparison / Social Proof / Routine / B&A Transformation / Founder POV / Myth Busting]
**Emotional ID:** [one of: Achievement / Autonomy / Belonging / Empowerment]
**Awareness Level:** [one of: Problem-Unaware / Problem-Aware / Solution-Aware]
**Story Framework:** [one of: StoryBrand / PAS / AIDA / Pixar / Before & After / None]
**Creative Format:** [UGC / Branded / Hybrid / Static / Educational / Testimonial]
**Hook Type:** [1 sentence describing the hook strategy]
**Key Message:** [1 sentence: core value proposition]
**Before State:** [the problem / pain point this creative addresses]
**New State:** [the transformation the creative promises]
**Audience Signals:** [what in the creative tells you who this is for]"""


def build_correlation_prompt(ad, has_media, insights, batch_avgs, context_block=""):
    """Performance-creative correlation prompt with Soar frameworks."""
    body, title = extract_ad_copy(ad)
    metrics = format_metrics_block(insights, batch_avgs)

    media_note = "Analyse the attached creative file." if has_media else "No media available — analyse copy and metrics."

    return f"""You're analysing the relationship between creative elements and performance
using Soar Group's frameworks. {media_note}

## AD METADATA
- Ad Name: {ad.get('name', 'Unknown')}
- Ad Copy: {body or 'N/A'}
- Headline: {title or 'N/A'}

{metrics}
{SOAR_FRAMEWORKS_BLOCK}
{context_block}

Provide:

1. **Classification**
   - Format: UGC / Branded / Hybrid / Static
   - Production: Lo-fi / Mid / High
   - Content type: Testimonial / Demo / Educational / Problem-solution / Lifestyle
   - Emotional ID: Achievement / Autonomy / Belonging / Empowerment
   - Story Framework: StoryBrand / PAS / AIDA / Pixar / B&A / None
   - Awareness Level: Problem-Unaware / Problem-Aware / Solution-Aware
   - Angle: [one of the 8-angle taxonomy]

2. **Hook Analysis**
   - Hook type and first 3 seconds description
   - Thumbstop potential (1-10) with reasoning

3. **Engagement Drivers**
   - What keeps someone watching past 3s?
   - Pattern interrupts used
   - Information density: sparse / moderate / dense

4. **CTA Strength** (1-10 with reasoning)

5. **RAG Metric Scoring**
   Score each metric against Soar benchmarks (🟢🟡🔴):
   - CTR: {insights.get("ctr", "N/A")}% → [🟢/🟡/🔴]
   Flag any 🔴 metrics with likely creative cause.

6. **Performance Verdict**
   - This ad's CPC is {"above" if float(insights.get("cpc", 0) or 0) > float(batch_avgs.get("avg_cpc", 0) or 0) else "below"} batch average
   - This ad's CTR is {"above" if float(insights.get("ctr", 0) or 0) > float(batch_avgs.get("avg_ctr", 0) or 0) else "below"} batch average
   - Which creative elements are driving this? Be specific.
   - Attribution note: if conversions are heavily view-through, note lower confidence.

7. **Ad Lifecycle**: Testing / Scaling / Retire / Retest — with reasoning.

8. **One Key Takeaway** for the creative team"""


def build_custom_prompt(ad, has_media, insights, custom_prompt, batch_avgs=None, context_block=""):
    """Custom analysis with user-defined focus + Soar frameworks."""
    body, title = extract_ad_copy(ad)
    metrics = format_metrics_block(insights, batch_avgs)

    media_note = "Analyse the attached creative file to inform your response." if has_media else ""

    return f"""Analyse this Meta ad with the following focus. Use Soar's creative strategy
frameworks where relevant. {media_note}

## USER'S ANALYSIS FOCUS
{custom_prompt}

## AD METADATA
- Ad Name: {ad.get('name', 'Unknown')}
- Ad Copy: {body or 'N/A'}
- Headline: {title or 'N/A'}

{metrics}
{SOAR_FRAMEWORKS_BLOCK}
{context_block}

Provide a focused, concise analysis addressing the user's specific questions above.
Where relevant, include: Emotional ID, Story Framework, Awareness Level, Angle classification,
RAG-scored metrics, and Ad Lifecycle classification."""


def build_persona_synthesis_prompt(all_results, batch_avgs):
    """Cross-ad persona synthesis prompt with 3-layer taxonomy + ICE recommendations."""
    # Build COMPACT data table — parse structured fields from per-ad analysis
    rows = []
    for r in all_results:
        analysis = r.get("analysis", "")
        parsed = {}
        for line in analysis.split("\n"):
            line = line.strip()
            for field in ["Product:", "Macro Persona:", "Micro Persona:",
                          "Angle:", "Emotional ID:", "Awareness Level:",
                          "Story Framework:", "Creative Format:", "Hook Type:",
                          "Key Message:", "Before State:", "New State:",
                          "Audience Signals:"]:
                if field in line:
                    val = line.split(field, 1)[-1].strip().strip("*").strip()
                    parsed[field.replace(":", "").strip()] = val

        rows.append({
            "ad_name": r.get("ad_name", "")[:60],
            "spend": r.get("insights", {}).get("spend", "0"),
            "impressions": r.get("insights", {}).get("impressions", "0"),
            "clicks": r.get("insights", {}).get("clicks", "0"),
            "cpc": r.get("insights", {}).get("cpc", "0"),
            "ctr": r.get("insights", {}).get("ctr", "0"),
            "product": parsed.get("Product", "Unknown"),
            "macro_persona": parsed.get("Macro Persona", "Unknown"),
            "micro_persona": parsed.get("Micro Persona", ""),
            "angle": parsed.get("Angle", "Unknown"),
            "emotional_id": parsed.get("Emotional ID", "Unknown"),
            "awareness_level": parsed.get("Awareness Level", "Unknown"),
            "story_framework": parsed.get("Story Framework", "Unknown"),
            "creative_format": parsed.get("Creative Format", "Unknown"),
            "hook_type": parsed.get("Hook Type", "Unknown"),
            "key_message": parsed.get("Key Message", ""),
            "before_state": parsed.get("Before State", ""),
            "new_state": parsed.get("New State", ""),
        })

    data_str = json.dumps(rows, indent=2)

    return f"""You are a creative strategist at Soar Group analysing a portfolio of {len(all_results)} Meta ads.
Below is each ad's persona classification (using 3-layer taxonomy) and performance data.

Your task: synthesise across ALL ads to identify patterns, gaps, and strategic opportunities.

## ALL ADS DATA
{data_str}

## BATCH AVERAGES
- Avg CPC: ${batch_avgs.get('avg_cpc', 'N/A')}
- Avg CPM: ${batch_avgs.get('avg_cpm', 'N/A')}
- Avg CTR: {batch_avgs.get('avg_ctr', 'N/A')}%
- Total Spend: ${batch_avgs.get('total_spend', 'N/A')}

## SOAR KPI BENCHMARKS FOR RAG SCORING
- TSR: 🟢 >30% | 🟡 20-30% | 🔴 <20%
- Hold Rate (15s): 🟢 >45% | 🟡 30-45% | 🔴 <30%
- CTR: 🟢 >1% | 🟡 0.5-1% | 🔴 <0.5%
- Frequency: 🟢 <2.5 | 🟡 2.5-3.5 | 🔴 >3.5

## PROVIDE ALL OF THE FOLLOWING:

### 1. Persona Spend Allocation Table
Group ads by Macro Persona → Micro Persona. For each:
| Persona (Macro → Micro) | # Ads | Total Spend | % of Total | Avg CPC | Avg CTR | Dominant Angle | Dominant Emotion | Products |

### 2. Awareness Level Distribution
| Awareness Level | # Ads | % Spend | Dominant Formats |
Flag if ANY level has 0% coverage — this is a critical strategic gap.

### 3. Story Framework Distribution
Which frameworks are in use? Which are completely untested? Flag untested frameworks as opportunities.

### 4. Angle Coverage Matrix
Which of the 8 angles are in use across the portfolio? Which are missing entirely?
| Angle | # Ads | % Spend | Performance vs Avg |

### 5. Spend Balance Assessment
- Which personas get most/least investment?
- Are high-performing segments under-invested?
- Is there awareness level skew (e.g., all BOF, no TOF)?

### 6. Creative Gap Analysis
- Personas with <3 creative variants (fatigue risk)
- Missing angles per persona (which of 8 are untested?)
- Missing creative formats per persona
- Persona x Awareness Level gaps (e.g., no TOF creative for key persona)
- Persona x Product gaps

### 7. Cross-Persona Patterns
- Which angles/emotions/frameworks work across multiple personas?
- Which are persona-specific?
- Winning formats that could be adapted to underserved segments

### 8. ICE-Scored Recommendations
Top 5 strategic recommendations. For EACH:
| # | Recommendation | Rationale | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Total |
Sort by ICE Total descending.

Lead with the spend allocation table. Keep analysis strategic and actionable."""


def build_valence_prompt(ad, has_media, insights, context_block=""):
    """Valence Deep Dive per-ad classification across 3-dimensional psychological matrix."""
    body, title = extract_ad_copy(ad)
    metrics = format_metrics_block(insights)

    media_note = "Analyse the attached creative to inform your classification." if has_media else ""

    return f"""You are an expert creative psychologist at Soar Group. Classify this Meta ad
across a 3-dimensional psychological matrix that measures strategic distinctness —
not just surface-level variation but genuine psychological diversity. {media_note}

## AD METADATA
- Ad Name: {ad.get('name', 'Unknown')}
- Ad Copy: {body or 'N/A'}
- Headline: {title or 'N/A'}

{metrics}

## THE 3-DIMENSIONAL PSYCHOLOGICAL MATRIX

### Dimension 1: Valence Zone (Emotional Charge)
Map this ad to one of 4 quadrants based on its emotional charge:

| Zone | Valence | Arousal | Examples |
|------|---------|---------|----------|
| Zone 1: High Valence / Positive | Positive | High | Excitement, joy, triumph, surprise delight, celebration |
| Zone 2: Low Valence / Positive | Positive | Low | Calm confidence, contentment, gentle reassurance, warmth, trust |
| Zone 3: Low Valence / Negative | Negative | Low | Subtle worry, quiet dissatisfaction, FOMO, nagging doubt |
| Zone 4: High Valence / Negative | Negative | High | Fear, urgency, shock, frustration, anger, "you're doing it wrong" |

Most brands over-index on Zone 4. Identify what specific creative elements (visuals,
audio, copy, pacing, colour) create the emotional charge.

### Dimension 2: Self-Concept Anchor (Identity Layer)
Which version of the customer does this ad speak to?

- **Actual Self** — Who they are right now. Mechanism: problem recognition, current pain awareness.
  Signal: copy that describes their current state, struggles, or daily reality.
- **Ideal Self** — Who they want to become. Mechanism: aspiration, future vision.
  Signal: copy that paints transformation, envisions a better future, uses "imagine" language.
- **Ought Self** — Who they feel they should be. Mechanism: duty, responsibility, determination.
  Signal: copy that invokes obligation to others, guilt-to-action shift, "do it for them" framing.

### Dimension 3: Language Intensity (Cognitive Friction)
Rate the cognitive friction level of the ad's copy and presentation:

- **Low Intensity** (1-3) — Subtle, conversational, organic-feeling, doesn't announce itself as an ad.
  Creates "Trust Equity" — viewer doesn't trigger ad-defense mechanisms.
- **Mid Intensity** (4-6) — Balanced, clear value statements with moderate assertiveness.
  Feels like a recommendation from a friend.
- **High Intensity** (7-10) — Assertive, superlative-heavy, urgency-stacking, exclamation points,
  all-caps declarations. Spends Trust Equity — viewer knows they're being sold to.

{SOAR_FRAMEWORKS_BLOCK}
{context_block}

Respond in EXACTLY this format:

**Product:** [product name extracted from ad name/copy]
**Valence Zone:** [Zone 1 / Zone 2 / Zone 3 / Zone 4] — [High/Low Valence] / [Positive/Negative]
**Valence Reasoning:** [2-3 sentences: what specific creative elements create this emotional charge?]
**Self-Concept:** [Actual Self / Ideal Self / Ought Self]
**Self-Concept Reasoning:** [2-3 sentences with specific copy/visual evidence. Quote the language.]
**Language Intensity:** [Low / Mid / High] — Intensity Score: [1-10]
**Intensity Reasoning:** [2-3 sentences: what specific copy elements drive this rating?]
**Matrix Position:** [Zone X] × [Self-Concept] × [Intensity Level]
**Trust Equity:** [Build / Spend / Neutral] — [1 sentence explanation]
**Emotional ID:** [Achievement / Autonomy / Belonging / Empowerment]
**Awareness Level:** [Problem-Unaware / Problem-Aware / Solution-Aware]
**Story Framework:** [StoryBrand / PAS / AIDA / Pixar / Before & After / None]
**Creative Format:** [UGC / Branded / Hybrid / Static / Educational / Testimonial]
**Hook Type:** [1 sentence describing the hook strategy]
**Key Message:** [1 sentence: core value proposition for this psychological position]"""


def build_valence_synthesis_prompt(all_results, batch_avgs):
    """Cross-ad valence synthesis — maps the psychological landscape and finds diversity gaps."""
    rows = []
    for r in all_results:
        analysis = r.get("analysis", "")
        parsed = {}
        for line in analysis.split("\n"):
            line = line.strip()
            for field in ["Product:", "Valence Zone:", "Valence Reasoning:",
                          "Self-Concept:", "Self-Concept Reasoning:",
                          "Language Intensity:", "Intensity Reasoning:",
                          "Matrix Position:", "Trust Equity:",
                          "Emotional ID:", "Awareness Level:",
                          "Story Framework:", "Creative Format:", "Hook Type:",
                          "Key Message:"]:
                if field in line:
                    val = line.split(field, 1)[-1].strip().strip("*").strip()
                    parsed[field.replace(":", "").strip()] = val

        rows.append({
            "ad_name": r.get("ad_name", "")[:60],
            "spend": r.get("insights", {}).get("spend", "0"),
            "impressions": r.get("insights", {}).get("impressions", "0"),
            "clicks": r.get("insights", {}).get("clicks", "0"),
            "cpc": r.get("insights", {}).get("cpc", "0"),
            "ctr": r.get("insights", {}).get("ctr", "0"),
            "product": parsed.get("Product", "Unknown"),
            "valence_zone": parsed.get("Valence Zone", "Unknown"),
            "valence_reasoning": parsed.get("Valence Reasoning", ""),
            "self_concept": parsed.get("Self-Concept", "Unknown"),
            "self_concept_reasoning": parsed.get("Self-Concept Reasoning", ""),
            "language_intensity": parsed.get("Language Intensity", "Unknown"),
            "intensity_reasoning": parsed.get("Intensity Reasoning", ""),
            "matrix_position": parsed.get("Matrix Position", "Unknown"),
            "trust_equity": parsed.get("Trust Equity", "Unknown"),
            "emotional_id": parsed.get("Emotional ID", "Unknown"),
            "awareness_level": parsed.get("Awareness Level", "Unknown"),
            "story_framework": parsed.get("Story Framework", "Unknown"),
            "creative_format": parsed.get("Creative Format", "Unknown"),
        })

    data_str = json.dumps(rows, indent=2)

    return f"""You are a creative psychologist at Soar Group analysing a portfolio of {len(all_results)} Meta ads.
Each ad has been classified across a 3-dimensional psychological matrix: Valence Zone,
Self-Concept Anchor, and Language Intensity.

Your task: synthesise across ALL ads to map the psychological landscape, identify which
zones are saturated, which are unmapped, and where the biggest strategic diversity gaps exist.

## ALL ADS DATA
{data_str}

## BATCH AVERAGES
- Avg CPC: ${batch_avgs.get('avg_cpc', 'N/A')}
- Avg CPM: ${batch_avgs.get('avg_cpm', 'N/A')}
- Avg CTR: {batch_avgs.get('avg_ctr', 'N/A')}%
- Total Spend: ${batch_avgs.get('total_spend', 'N/A')}

## SOAR KPI BENCHMARKS FOR RAG SCORING
- CTR: 🟢 >1% | 🟡 0.5-1% | 🔴 <0.5%
- TSR: 🟢 >30% | 🟡 20-30% | 🔴 <20%

## PROVIDE ALL OF THE FOLLOWING:

### 1. Psychological Matrix Heatmap
Create a matrix showing ad distribution across all 12 cells (4 zones × 3 self-concepts).
For each cell show: # of ads, total spend, and performance indicator.

| | Actual Self | Ideal Self | Ought Self |
|---|---|---|---|
| **Zone 1** (High+) | [X ads / $Y] | ... | ... |
| **Zone 2** (Low+) | ... | ... | ... |
| **Zone 3** (Low-) | ... | ... | ... |
| **Zone 4** (High-) | ... | ... | ... |

Mark cells with 0 ads as **⚠️ UNMAPPED** — these are the biggest strategic opportunities.
Mark cells with 5+ ads as **🔄 SATURATED** — diminishing returns territory.

### 2. Psychological Diversity Score
Count how many of the 12 matrix cells have at least 1 ad. Score:
- 10-12 cells = 🟢 Exceptional psychological diversity
- 7-9 cells = 🟡 Good diversity with notable gaps
- 4-6 cells = 🟠 Moderate — significant blind spots
- 1-3 cells = 🔴 Poor — operating in a narrow psychological lane

### 3. Valence Zone Distribution
| Zone | # Ads | % Spend | Avg CPC | Avg CTR | Dominant Self-Concept | Dominant Intensity |
Flag which zones are over/under-represented.

### 4. Self-Concept Distribution
| Self-Concept | # Ads | % Spend | Avg CPC | Avg CTR | Dominant Zone |
Flag if >60% of ads target Actual Self (the typical 75% imbalance).

### 5. Language Intensity Distribution
| Intensity | # Ads | % Spend | Avg CPC | Avg CTR | Avg Score |
Flag if >50% of ads are High Intensity (audience fatigue risk).

### 6. Trust Equity Balance
- Count: how many ads Build vs Spend vs Neutral on Trust Equity?
- Is the portfolio net-positive or net-negative on Trust Equity?
- Flag if >70% Spend Trust Equity — this is unsustainable.

### 7. Biggest Opportunity Zones
For each UNMAPPED or under-served matrix cell (top 3-5 priorities), describe:
- The matrix position (e.g., Zone 2 × Ideal Self × Low Intensity)
- What a creative brief for this zone would look like (tone, copy style, visual approach)
- Which existing ad in the portfolio is closest and could be adapted
- Why this zone matters for this brand's audience

### 8. Cross-Zone Performance Patterns
- Which matrix positions have the best/worst performance metrics?
- Is there a correlation between Valence Zone and funnel performance?
- Do certain Self-Concept × Intensity combinations stand out?
- Which zones show signs of fatigue vs fresh opportunity?

### 9. ICE-Scored Recommendations
Top 5 strategic recommendations for improving psychological diversity.
For EACH:
| # | Recommendation | Matrix Gap Addressed | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Total |
Sort by ICE Total descending.

Lead with the Psychological Matrix Heatmap and Diversity Score — that's the headline
finding. Then zone distributions. Then opportunity zones with specific creative brief
suggestions. Close with ICE recommendations. This report should reshape how the team
thinks about creative production — not just what ads to make, but what psychological
territory to explore."""


def build_framework_audit_prompt(ad, has_media, insights, context_block=""):
    """Selective framework audit — extracts only Emotional ID, Story Framework,
    Awareness Level, Angle, Hook, and Key Messaging. Used in Growth Strategy Audit."""
    body, title = extract_ad_copy(ad)
    metrics = format_metrics_block(insights)

    media_note = "Analyse the attached creative to inform your classification." if has_media else ""

    return f"""You are a creative strategist at Soar Group. Extract the key framework
classifications and messaging analysis for this Meta ad. {media_note}

## AD METADATA
- Ad Name: {ad.get('name', 'Unknown')}
- Ad Copy: {body or 'N/A'}
- Headline: {title or 'N/A'}

{metrics}
{SOAR_FRAMEWORKS_BLOCK}
{context_block}

Respond in EXACTLY this format:

**Product:** [product name extracted from ad name/copy]
**Emotional ID (Primary):** [Achievement / Autonomy / Belonging / Empowerment]
**Emotional ID (Secondary):** [one of 4 or None]
**Story Framework:** [StoryBrand / PAS / AIDA / Pixar / Before & After / None] — [1-sentence explanation]
**Awareness Level:** [Problem-Unaware / Problem-Aware / Solution-Aware] — [1-sentence evidence]
**Angle:** [Objection Handling / Education / Comparison / Social Proof / Routine / B&A Transformation / Founder POV / Myth Busting]
**Hook (Voiced):** [transcription of first audio hook, or N/A if image]
**Hook (Visual):** [1-sentence description of visual hook]
**Key Message:** [1 sentence: core value proposition]
**Stand-Out Messaging:** [2-3 notable phrases, stats, or USPs]"""


def build_opportunity_synthesis_prompt(all_results, batch_avgs, portfolio_health,
                                       valence_synthesis, persona_synthesis):
    """Growth Strategy Audit capstone — combines all analysis passes into categorised opportunities."""
    # Build compact per-ad data from all 4 passes
    rows = []
    for r in all_results:
        row = {
            "ad_name": r.get("ad_name", "")[:60],
            "spend": r.get("insights", {}).get("spend", "0"),
            "cpc": r.get("insights", {}).get("cpc", "0"),
            "ctr": r.get("insights", {}).get("ctr", "0"),
            "cpm": r.get("insights", {}).get("cpm", "0"),
            "is_top_performer": r.get("is_top_performer", False),
            "frequency": r.get("insights", {}).get("frequency", "N/A"),
        }

        # Parse structured fields from each analysis pass
        for pass_key, fields in [
            ("correlation_analysis", ["Format:", "Production:", "Hook type:", "Thumbstop potential:",
                                      "Ad Lifecycle:", "One Key Takeaway:"]),
            ("valence_analysis", ["Valence Zone:", "Self-Concept:", "Language Intensity:",
                                  "Matrix Position:", "Trust Equity:"]),
            ("persona_analysis", ["Macro Persona:", "Micro Persona:", "Angle:",
                                  "Awareness Level:", "Before State:", "New State:"]),
            ("framework_analysis", ["Emotional ID (Primary):", "Story Framework:",
                                    "Hook (Voiced):", "Hook (Visual):", "Key Message:",
                                    "Stand-Out Messaging:"]),
        ]:
            analysis_text = r.get(pass_key, "") or ""
            for field in fields:
                for line in analysis_text.split("\n"):
                    line = line.strip()
                    if field in line:
                        val = line.split(field, 1)[-1].strip().strip("*").strip()
                        clean_key = field.replace(":", "").replace("(", "").replace(")", "").strip().replace(" ", "_").lower()
                        row[f"{pass_key.split('_')[0]}_{clean_key}"] = val
                        break

        rows.append(row)

    data_str = json.dumps(rows, indent=2)

    return f"""You are a senior growth strategist at Soar Group producing the strategic capstone
of a Growth Strategy Creative Audit. You have data from FOUR analysis passes across
{len(all_results)} Meta ads, plus synthesis reports for valence and persona dimensions.

Your task: Combine ALL findings into a categorised list of strategic opportunities that
sets the user up for Reddit deep-dive research.

## PORTFOLIO HEALTH CHECK
{json.dumps(portfolio_health, indent=2)}

## ALL ADS DATA (4-pass analysis)
{data_str}

## BATCH AVERAGES
- Avg CPC: ${batch_avgs.get('avg_cpc', 'N/A')}
- Avg CPM: ${batch_avgs.get('avg_cpm', 'N/A')}
- Avg CTR: {batch_avgs.get('avg_ctr', 'N/A')}%
- Total Spend: ${batch_avgs.get('total_spend', 'N/A')}

## VALENCE SYNTHESIS (from valence pass)
{valence_synthesis or 'Not available'}

## PERSONA SYNTHESIS (from persona pass)
{persona_synthesis or 'Not available'}

## SOAR KPI BENCHMARKS
- TSR: 🟢 >30% | 🟡 20-30% | 🔴 <20%
- CTR: 🟢 >1% | 🟡 0.5-1% | 🔴 <0.5%
- Frequency: 🟢 <2.5 | 🟡 2.5-3.5 | 🔴 >3.5

## PROVIDE ALL OF THE FOLLOWING:

### 1. Executive Summary
Write 2-3 paragraphs summarising:
- Portfolio size, spend, top performer ratio
- Headline finding from each dimension (correlation, valence, persona, framework)
- The single most important strategic insight

### 2. Categorised Opportunity List
For EVERY opportunity identified across all analysis passes, create an entry:

| # | Category | Opportunity | Evidence | Impact (1-10) | Confidence (1-10) | Ease (1-10) | ICE Total | Reddit Research Prompt |
|---|----------|-------------|----------|---------------|-------------------|-------------|-----------|----------------------|

Categories to use:
- **Valence Gap** — Unmapped psychological zones
- **Persona Gap** — Under-served or missing personas
- **Creative Diversity** — Format/style/production variety gaps
- **Framework Gap** — Untested story frameworks, awareness levels, or angles
- **Messaging Gap** — Missing hooks, value props, or language styles
- **Fatigue Signal** — High frequency with declining performance
- **Performance Correlation** — Creative elements strongly linked to metrics

For the Reddit Research Prompt column, write a specific search query like:
"Search r/[relevant_subreddit] for [topic] to understand [what we need to learn]
for [how it informs the creative brief]."

Aim for 10-20 opportunities total. Sort by ICE Total descending.

### 3. Priority Matrix
Group the top 5 as "Priority Opportunities" and the rest as "Secondary Opportunities."
For each priority opportunity, expand with a 2-3 sentence creative brief direction.

### 4. Next Steps
Write 3-4 bullet points telling the strategist what to do next:
- Review and filter opportunities
- Select 3-5 priorities for Reddit deep-dive
- Use Reddit Research Prompts to mine audience language
- Use findings to write creative briefs

Lead with the Executive Summary. The opportunity table is the CORE DELIVERABLE.
This report should directly set up the next phase: Reddit research and creative brief writing."""


def classify_top_performers(ads, method="roas_top_20", roas_target=None):
    """Classify ads as top performers based on the chosen method."""
    for ad in ads:
        ins = ad.get("insights", {}).get("data", [{}])[0]
        # Extract ROAS from actions
        roas = 0.0
        spend = float(ins.get("spend", 0) or 0)
        for action in (ins.get("actions") or []):
            if action.get("action_type") == "offsite_conversion.fb_pixel_purchase":
                try:
                    purchase_value = float(action.get("value", 0))
                    if spend > 0:
                        roas = purchase_value / spend
                except (ValueError, TypeError):
                    pass
        # Also check cost_per_action for purchase value
        if roas == 0 and spend > 0:
            for action in (ins.get("actions") or []):
                if "purchase" in action.get("action_type", ""):
                    try:
                        roas = float(action.get("value", 0)) / spend if spend > 0 else 0
                    except (ValueError, TypeError):
                        pass
        ad["_roas"] = roas
        ad["_spend"] = spend

    if method == "roas_top_20":
        roas_values = sorted([a["_roas"] for a in ads], reverse=True)
        cutoff_idx = max(1, len(roas_values) // 5)
        cutoff = roas_values[cutoff_idx - 1] if cutoff_idx <= len(roas_values) else 0
        for ad in ads:
            ad["_is_top_performer"] = ad["_roas"] >= cutoff and ad["_roas"] > 0

    elif method == "spend_positive_roas":
        spend_sorted = sorted(ads, key=lambda a: a["_spend"], reverse=True)
        cutoff_idx = max(1, len(spend_sorted) // 5)
        top_spenders = spend_sorted[:cutoff_idx]
        top_ids = {a.get("id") for a in top_spenders if a["_roas"] > 1.0}
        for ad in ads:
            ad["_is_top_performer"] = ad.get("id") in top_ids

    elif method == "roas_above_target" and roas_target is not None:
        for ad in ads:
            ad["_is_top_performer"] = ad["_roas"] >= roas_target

    else:  # fallback to roas_top_20
        roas_values = sorted([a["_roas"] for a in ads], reverse=True)
        cutoff_idx = max(1, len(roas_values) // 5)
        cutoff = roas_values[cutoff_idx - 1] if cutoff_idx <= len(roas_values) else 0
        for ad in ads:
            ad["_is_top_performer"] = ad["_roas"] >= cutoff and ad["_roas"] > 0

    top_count = sum(1 for a in ads if a.get("_is_top_performer"))
    log(f"Top performers: {top_count}/{len(ads)} (method: {method})")
    return ads


def compute_portfolio_health(ads):
    """Compute portfolio health metrics for Growth Strategy Audit."""
    total = len(ads)
    top_performers = [a for a in ads if a.get("_is_top_performer")]
    non_top = [a for a in ads if not a.get("_is_top_performer")]

    def avg_metric(ad_list, metric):
        vals = []
        for a in ad_list:
            ins = a.get("insights", {}).get("data", [{}])[0]
            try:
                v = float(ins.get(metric, 0) or 0)
                if v > 0:
                    vals.append(v)
            except (ValueError, TypeError):
                pass
        return sum(vals) / len(vals) if vals else 0

    # Frequency might not be in standard insights — compute from impressions/reach if available
    def avg_frequency(ad_list):
        vals = []
        for a in ad_list:
            ins = a.get("insights", {}).get("data", [{}])[0]
            try:
                impressions = float(ins.get("impressions", 0) or 0)
                reach = float(ins.get("reach", 0) or 0)
                if reach > 0:
                    vals.append(impressions / reach)
            except (ValueError, TypeError):
                pass
        return sum(vals) / len(vals) if vals else 0

    health = {
        "total_active_creatives": total,
        "total_top_performers": len(top_performers),
        "top_performer_pct": f"{len(top_performers)/total*100:.1f}%" if total > 0 else "0%",
        "avg_frequency_top": f"{avg_frequency(top_performers):.2f}",
        "avg_frequency_non_top": f"{avg_frequency(non_top):.2f}",
        "frequency_delta": f"{avg_frequency(non_top) - avg_frequency(top_performers):.2f}",
        "avg_roas_top": f"{sum(a['_roas'] for a in top_performers)/len(top_performers):.2f}" if top_performers else "N/A",
        "avg_roas_non_top": f"{sum(a['_roas'] for a in non_top)/len(non_top):.2f}" if non_top else "N/A",
        "avg_cpm_top": f"{avg_metric(top_performers, 'cpm'):.2f}",
        "avg_cpm_non_top": f"{avg_metric(non_top, 'cpm'):.2f}",
        "creative_fatigue_signal": avg_frequency(non_top) > avg_frequency(top_performers) + 1.0,
    }
    return health


# ── Step 5b: Analyse with Gemini ────────────────────────────────────────────

def call_gemini(prompt, gemini_file_info=None, max_tokens=4096):
    """Send prompt (optionally with media) to Gemini."""
    parts = []

    if gemini_file_info and gemini_file_info.get("uri"):
        parts.append({
            "file_data": {
                "file_uri": gemini_file_info["uri"],
                "mime_type": gemini_file_info.get("mimeType", "video/mp4"),
            }
        })

    parts.append({"text": prompt})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": max_tokens,
        }
    }

    try:
        resp = requests.post(url, json=body, timeout=300)
        if resp.status_code != 200:
            log(f"    Gemini error {resp.status_code}: {resp.text[:300]}", "ERROR")
            return None

        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return parts[0].get("text", "")

        log(f"    No text in Gemini response", "WARN")
        return None

    except Exception as e:
        log(f"    Gemini error: {e}", "ERROR")
        return None


# ── Step 6: Compute batch averages ──────────────────────────────────────────

def compute_batch_averages(ads):
    """Compute average metrics across all ads for comparison."""
    total_spend = 0
    total_cpc = []
    total_cpm = []
    total_ctr = []

    for ad in ads:
        ins = ad.get("insights", {}).get("data", [{}])[0]
        try:
            total_spend += float(ins.get("spend", 0) or 0)
        except (ValueError, TypeError):
            pass
        try:
            cpc = float(ins.get("cpc", 0) or 0)
            if cpc > 0:
                total_cpc.append(cpc)
        except (ValueError, TypeError):
            pass
        try:
            cpm = float(ins.get("cpm", 0) or 0)
            if cpm > 0:
                total_cpm.append(cpm)
        except (ValueError, TypeError):
            pass
        try:
            ctr = float(ins.get("ctr", 0) or 0)
            if ctr > 0:
                total_ctr.append(ctr)
        except (ValueError, TypeError):
            pass

    return {
        "total_spend": f"{total_spend:.2f}",
        "avg_cpc": f"{sum(total_cpc) / len(total_cpc):.2f}" if total_cpc else "N/A",
        "avg_cpm": f"{sum(total_cpm) / len(total_cpm):.2f}" if total_cpm else "N/A",
        "avg_ctr": f"{sum(total_ctr) / len(total_ctr):.2f}" if total_ctr else "N/A",
    }


# ── Step 7: Generate reports ────────────────────────────────────────────────

def generate_report(results, output_dir, analysis_type, batch_avgs, persona_synthesis=None,
                    valence_synthesis=None, opportunity_synthesis=None, portfolio_health=None):
    """Generate markdown report and raw JSON with RAG scoring."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    type_labels = {
        "audit": "End-to-End Creative Audit",
        "persona": "Persona & Spend Gap Analysis",
        "valence": "Valence Deep Dive",
        "correlation": "Performance-Creative Correlation",
        "custom": "Custom Analysis",
    }

    md = []
    md.append(f"# Meta Creative Analysis Report")
    md.append(f"")
    md.append(f"**Generated**: {timestamp}")
    md.append(f"**Analysis Type**: {type_labels.get(analysis_type, analysis_type)}")
    md.append(f"**Ad Account**: {AD_ACCOUNT_ID}")
    md.append(f"**Ads Analysed**: {len(results)}")
    md.append(f"**Total Spend**: ${batch_avgs.get('total_spend', 'N/A')}")
    md.append(f"**Avg CPC**: ${batch_avgs.get('avg_cpc', 'N/A')} | **Avg CPM**: ${batch_avgs.get('avg_cpm', 'N/A')} | **Avg CTR**: {batch_avgs.get('avg_ctr', 'N/A')}%")
    md.append(f"")
    md.append(f"**Frameworks**: Emotional ID · Story Frameworks · Awareness Levels · 8-Angle Taxonomy · RAG Benchmarks · Ad Lifecycle · ICE Scoring")
    md.append(f"")
    md.append(f"---")
    md.append(f"")

    # Portfolio Health (Growth Strategy only)
    if portfolio_health:
        md.append(f"## Portfolio Health Check")
        md.append(f"")
        md.append(f"| Metric | Value |")
        md.append(f"|--------|-------|")
        md.append(f"| Total Active Creatives | {portfolio_health['total_active_creatives']} |")
        md.append(f"| Total Top Performers | {portfolio_health['total_top_performers']} ({portfolio_health['top_performer_pct']}) |")
        md.append(f"| Avg Frequency (Top) | {portfolio_health['avg_frequency_top']} |")
        md.append(f"| Avg Frequency (Non-Top) | {portfolio_health['avg_frequency_non_top']} |")
        md.append(f"| Frequency Delta | {portfolio_health['frequency_delta']} |")
        md.append(f"| Avg ROAS (Top) | {portfolio_health['avg_roas_top']} |")
        md.append(f"| Avg ROAS (Non-Top) | {portfolio_health['avg_roas_non_top']} |")
        md.append(f"| Avg CPM (Top) | ${portfolio_health['avg_cpm_top']} |")
        md.append(f"| Avg CPM (Non-Top) | ${portfolio_health['avg_cpm_non_top']} |")
        md.append(f"| Creative Fatigue Signal | {'⚠️ YES' if portfolio_health['creative_fatigue_signal'] else '✅ No'} |")
        md.append(f"")
        md.append(f"---")
        md.append(f"")

    # RAG-scored metrics table
    md.append(f"## Performance Summary (RAG-Scored)")
    md.append(f"")
    md.append(f"| # | Ad Name | Spend | CTR | CTR RAG | CPC | CPM | Media | Lifecycle |")
    md.append(f"|---|---------|-------|-----|---------|-----|-----|-------|-----------|")

    for i, r in enumerate(results):
        ins = r.get("insights", {})
        name = r.get("ad_name", "Unknown")[:35]
        media = "✅" if r.get("gemini_uploaded") else "❌"
        ctr_val = ins.get('ctr', 'N/A')
        ctr_rag = rag_score(ctr_val, 1.0, 0.5, higher_is_better=True)

        # Extract lifecycle from analysis text
        lifecycle = "—"
        analysis_text = r.get("analysis", "")
        for state in ["Testing", "Scaling", "Retire", "Retest"]:
            if f"**{state}**" in analysis_text or f"Lifecycle**: {state}" in analysis_text or f"Lifecycle: {state}" in analysis_text:
                lifecycle = state
                break

        md.append(
            f"| {i+1} | {name} | ${ins.get('spend', 'N/A')} | "
            f"{ctr_val}% | {ctr_rag} | ${ins.get('cpc', 'N/A')} | "
            f"${ins.get('cpm', 'N/A')} | {media} | {lifecycle} |"
        )

    md.append(f"")
    md.append(f"**Soar Benchmarks**: CTR 🟢>1% 🟡0.5-1% 🔴<0.5% · TSR 🟢>30% 🟡20-30% 🔴<20% · Hold Rate (15s) 🟢>45% 🟡30-45% 🔴<30%")
    md.append(f"")
    md.append(f"---")
    md.append(f"")

    # Persona synthesis (if applicable)
    if persona_synthesis:
        md.append(f"## Persona & Spend Gap Synthesis")
        md.append(f"")
        md.append(persona_synthesis)
        md.append(f"")
        md.append(f"---")
        md.append(f"")

    # Valence synthesis (if applicable)
    if valence_synthesis:
        md.append(f"## Valence Deep Dive — Psychological Diversity Matrix")
        md.append(f"")
        md.append(valence_synthesis)
        md.append(f"")
        md.append(f"---")
        md.append(f"")

    # Opportunity synthesis (Growth Strategy only)
    if opportunity_synthesis:
        md.append(f"## Strategic Opportunities")
        md.append(f"")
        md.append(opportunity_synthesis)
        md.append(f"")
        md.append(f"---")
        md.append(f"")

    # Per-ad analysis
    md.append(f"## Individual Ad Analysis")
    md.append(f"")

    for i, r in enumerate(results):
        md.append(f"### Ad #{i+1}: {r.get('ad_name', 'Unknown')}")
        md.append(f"")
        media_label = f"{r['asset_type']} ({'multimodal' if r.get('gemini_uploaded') else 'metadata-only'})" if r.get("asset_type") else "metadata-only"
        md.append(f"**Analysis basis**: {media_label} | **Spend**: ${r.get('insights', {}).get('spend', 'N/A')}")
        md.append(f"")

        if r.get("analysis"):
            md.append(r["analysis"])
        else:
            md.append("*Analysis unavailable.*")

        md.append(f"")
        md.append(f"---")
        md.append(f"")

    md_content = "\n".join(md)

    # Write files
    md_path = os.path.join(output_dir, "creative_analysis.md")
    with open(md_path, 'w') as f:
        f.write(md_content)
    log(f"Report → {md_path}")

    json_path = os.path.join(output_dir, "analysis_raw.json")
    with open(json_path, 'w') as f:
        json.dump({
            "metadata": {
                "timestamp": timestamp,
                "analysis_type": analysis_type,
                "ad_account": AD_ACCOUNT_ID,
                "ads_analysed": len(results),
                "batch_averages": batch_avgs,
                "frameworks": ["emotional_id", "story_frameworks", "awareness_levels",
                               "angle_taxonomy", "rag_benchmarks", "ad_lifecycle", "ice_scoring",
                               "valence_zones", "self_concept", "language_intensity"],
            },
            "ads": results,
            "persona_synthesis": persona_synthesis,
            "valence_synthesis": valence_synthesis,
            "opportunity_synthesis": opportunity_synthesis,
            "portfolio_health": portfolio_health,
        }, f, indent=2, default=str)
    log(f"JSON  → {json_path}")

    if persona_synthesis:
        synth_path = os.path.join(output_dir, "persona_synthesis.md")
        with open(synth_path, 'w') as f:
            f.write(f"# Persona & Spend Gap Synthesis\n\n{persona_synthesis}")
        log(f"Persona synthesis → {synth_path}")

    if valence_synthesis:
        valence_path = os.path.join(output_dir, "valence_synthesis.md")
        with open(valence_path, 'w') as f:
            f.write(f"# Valence Deep Dive — Psychological Diversity Matrix\n\n{valence_synthesis}")
        log(f"Valence synthesis → {valence_path}")

    if opportunity_synthesis:
        opp_path = os.path.join(output_dir, "opportunity_synthesis.md")
        with open(opp_path, 'w') as f:
            f.write(f"# Strategic Opportunities — Growth Strategy Creative Audit\n\n{opportunity_synthesis}")
        log(f"Opportunity synthesis → {opp_path}")

    if portfolio_health:
        health_path = os.path.join(output_dir, "portfolio_health.json")
        with open(health_path, 'w') as f:
            json.dump(portfolio_health, f, indent=2)
        log(f"Portfolio health → {health_path}")

    return md_path, json_path


# ── Main pipeline ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Meta Creative Analysis Pipeline")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--date-preset", default="last_7d")
    parser.add_argument("--analysis-type", default="audit", choices=["audit", "persona", "valence", "correlation", "growth-strategy", "custom"])
    parser.add_argument("--metrics-enriched", action="store_true", default=False)
    parser.add_argument("--product-filter", default="")
    parser.add_argument("--custom-prompt", default="")
    parser.add_argument("--context-file", default="")
    parser.add_argument("--output", default="./creative_analysis")
    parser.add_argument("--top-performer-method", default="roas_top_20",
                        choices=["roas_top_20", "spend_positive_roas", "roas_above_target", "custom"])
    parser.add_argument("--roas-target", type=float, default=None)
    parser.add_argument("--meta-token", default="")
    parser.add_argument("--ad-account", default="")
    parser.add_argument("--gemini-key", default="")
    parser.add_argument("--gemini-model", default="")
    parser.add_argument("--meta-api-version", default="")
    args = parser.parse_args()

    # Override globals
    global META_ACCESS_TOKEN, AD_ACCOUNT_ID, GEMINI_API_KEY, GEMINI_MODEL, META_API_VERSION, META_BASE_URL
    if args.meta_token: META_ACCESS_TOKEN = args.meta_token
    if args.ad_account: AD_ACCOUNT_ID = args.ad_account
    if args.gemini_key: GEMINI_API_KEY = args.gemini_key
    if args.gemini_model: GEMINI_MODEL = args.gemini_model
    if args.meta_api_version:
        META_API_VERSION = args.meta_api_version
        META_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"

    # Validate
    for var, name in [(META_ACCESS_TOKEN, "Meta access token"), (AD_ACCOUNT_ID, "Ad account ID"), (GEMINI_API_KEY, "Gemini API key")]:
        if not var:
            log(f"ERROR: {name} not provided", "ERROR")
            sys.exit(1)

    if args.analysis_type == "custom" and not args.custom_prompt:
        log("ERROR: --custom-prompt required for custom analysis type", "ERROR")
        sys.exit(1)

    # Force metrics-enriched for correlation mode
    metrics_enriched = args.metrics_enriched or args.analysis_type == "correlation"

    # Load optional client context
    client_context = load_context_file(args.context_file)
    context_block = build_context_block(client_context)
    has_context = bool(context_block)

    output_dir = args.output
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    type_labels = {"audit": "End-to-End Audit", "persona": "Persona Gap Analysis",
                   "valence": "Valence Deep Dive", "correlation": "Performance Correlation",
                   "growth-strategy": "Growth Strategy Creative Audit",
                   "custom": "Custom Analysis"}

    log("=" * 60)
    log("META CREATIVE ANALYSIS PIPELINE")
    log("=" * 60)
    log(f"Analysis Type: {type_labels.get(args.analysis_type)}")
    log(f"Ad Account: {AD_ACCOUNT_ID}")
    log(f"Date Preset: {args.date_preset}")
    log(f"Limit: {args.limit}")
    log(f"Metrics-Enriched: {'yes' if metrics_enriched else 'no'}")
    log(f"Client Context: {'yes' if has_context else 'no'}")
    log(f"Product Filter: {args.product_filter or 'none'}")
    log(f"Output: {output_dir}")
    log(f"Frameworks: Emotional ID · Story Frameworks · Awareness Levels · 8-Angle · RAG · Lifecycle · ICE")
    log("")

    # ── Time estimate ──
    # Based on real-world benchmarks: ~20s per image ad, ~45s per video ad
    # Most accounts are ~70% video, so weighted average ~38s per ad
    est_seconds = args.limit * 38
    est_min = est_seconds / 60
    if est_min < 2:
        time_str = f"~{int(est_seconds)}s"
    else:
        time_str = f"~{est_min:.0f} minutes"
    log(f"⏱  ESTIMATED TIME: {time_str} for {args.limit} ads (varies by video count)")
    log(f"   Image ads ~20s each, Video ads ~45s each (download + upload + Gemini analysis)")
    log("")

    pipeline_start = time.time()

    # ── STEP 1: Fetch ads ──
    log("━" * 40)
    log("STEP 1/6: Fetching top ads by spend")
    log("━" * 40)
    ads = fetch_top_ads(limit=args.limit, date_preset=args.date_preset)

    if not ads:
        log("No ads found! Exiting.", "ERROR")
        sys.exit(1)

    # Product filter
    if args.product_filter:
        filtered = [a for a in ads if args.product_filter.lower() in a.get("name", "").lower()]
        if filtered:
            ads = filtered
            log(f"Product filter '{args.product_filter}' → {len(ads)} ads")
        else:
            log(f"Product filter matched 0 ads, using all {len(ads)}", "WARN")

    # ── Compute batch averages ──
    batch_avgs = compute_batch_averages(ads)
    log(f"Batch averages: CPC=${batch_avgs['avg_cpc']}, CPM=${batch_avgs['avg_cpm']}, CTR={batch_avgs['avg_ctr']}%")

    # ── Growth Strategy: classify top performers ──
    portfolio_health = None
    if args.analysis_type == "growth-strategy":
        ads = classify_top_performers(ads, method=args.top_performer_method,
                                       roas_target=args.roas_target)
        portfolio_health = compute_portfolio_health(ads)
        log(f"Portfolio Health: {portfolio_health['total_top_performers']}/{portfolio_health['total_active_creatives']} top performers")
        if portfolio_health['creative_fatigue_signal']:
            log("⚠️  CREATIVE FATIGUE SIGNAL DETECTED", "WARN")

    # ── Refined time estimate after fetching ──
    video_count = 0
    image_count = 0
    for a in ads:
        creative = a.get("creative", {})
        oss = creative.get("object_story_spec", {})
        if oss.get("video_data", {}).get("video_id"):
            video_count += 1
        else:
            image_count += 1
    time_multiplier = 4 if args.analysis_type == "growth-strategy" else 1
    refined_est = ((video_count * 45) + (image_count * 20)) * time_multiplier
    refined_min = refined_est / 60
    if refined_min < 2:
        ref_str = f"~{int(refined_est)}s"
    else:
        ref_str = f"~{refined_min:.0f} minutes"
    log(f"⏱  REFINED ESTIMATE: {ref_str} ({video_count} videos × 45s + {image_count} images × 20s)")
    log("")

    # ── PROCESS EACH AD ──
    results = []
    total = len(ads)

    for idx, ad in enumerate(ads):
        ad_name = ad.get("name", f"Ad_{idx}")
        insights_data = ad.get("insights", {}).get("data", [{}])[0]
        ad_start = time.time()

        elapsed = time.time() - pipeline_start
        elapsed_str = f"{int(elapsed//60)}m{int(elapsed%60)}s" if elapsed >= 60 else f"{int(elapsed)}s"

        log("")
        log("━" * 40)
        log(f"AD {idx+1}/{total}: {ad_name[:60]}  [{elapsed_str} elapsed]")
        log("━" * 40)

        result = {
            "ad_id": ad.get("id", ""),
            "ad_name": ad_name,
            "status": ad.get("effective_status", ad.get("status", "")),
            "insights": insights_data,
            "asset_type": None,
            "asset_file": None,
            "gemini_uploaded": False,
            "analysis": None,
        }

        # STEP 2: Resolve assets
        log("  Resolving assets...")
        assets = resolve_asset_urls(ad)
        gemini_file_info = None

        if assets:
            asset = assets[0]
            result["asset_type"] = asset["type"]

            # STEP 3: Download
            log("  Downloading...")
            downloaded = download_asset(asset, assets_dir)

            if downloaded and asset.get("local_path"):
                result["asset_file"] = asset["filename"]

                # STEP 4: Upload to Gemini
                log("  Uploading to Gemini...")
                gemini_file_info = upload_to_gemini(asset["local_path"])
                if gemini_file_info:
                    result["gemini_uploaded"] = True
                    result["gemini_uri"] = gemini_file_info.get("uri", "")
                    log("    ✓ Uploaded")
        else:
            log("  No media assets found", "WARN")

        # STEP 5: Analyse
        log("  Analysing with Soar frameworks...")
        has_media = gemini_file_info is not None and gemini_file_info.get("uri")
        ba = batch_avgs if metrics_enriched else None

        if args.analysis_type == "growth-strategy":
            # Multi-pass analysis: 4 Gemini calls per ad
            result["is_top_performer"] = ad.get("_is_top_performer", False)

            log("    Pass 1/4: Correlation...")
            corr_prompt = build_correlation_prompt(ad, has_media, insights_data, batch_avgs, context_block)
            result["correlation_analysis"] = call_gemini(corr_prompt, gemini_file_info, max_tokens=4096) or ""

            log("    Pass 2/4: Valence...")
            val_prompt = build_valence_prompt(ad, has_media, insights_data, context_block)
            result["valence_analysis"] = call_gemini(val_prompt, gemini_file_info, max_tokens=3072) or ""

            log("    Pass 3/4: Persona...")
            per_prompt = build_persona_prompt(ad, has_media, insights_data, context_block)
            result["persona_analysis"] = call_gemini(per_prompt, gemini_file_info, max_tokens=3072) or ""

            log("    Pass 4/4: Framework...")
            fw_prompt = build_framework_audit_prompt(ad, has_media, insights_data, context_block)
            result["framework_analysis"] = call_gemini(fw_prompt, gemini_file_info, max_tokens=2048) or ""

            # Combine into a single analysis field for the report
            result["analysis"] = (
                f"### Correlation Analysis\n{result['correlation_analysis']}\n\n"
                f"### Valence Classification\n{result['valence_analysis']}\n\n"
                f"### Persona Classification\n{result['persona_analysis']}\n\n"
                f"### Framework Audit\n{result['framework_analysis']}"
            )
        else:
            if args.analysis_type == "audit":
                prompt = build_audit_prompt(ad, has_media, insights_data, ba, context_block)
            elif args.analysis_type == "persona":
                prompt = build_persona_prompt(ad, has_media, insights_data, context_block)
            elif args.analysis_type == "valence":
                prompt = build_valence_prompt(ad, has_media, insights_data, context_block)
            elif args.analysis_type == "correlation":
                prompt = build_correlation_prompt(ad, has_media, insights_data, batch_avgs, context_block)
            elif args.analysis_type == "custom":
                prompt = build_custom_prompt(ad, has_media, insights_data, args.custom_prompt, ba, context_block)

            # Increase max_tokens based on analysis mode
            if args.analysis_type == "audit":
                max_tok = 6144
            elif args.analysis_type in ("persona", "valence"):
                max_tok = 3072
            else:
                max_tok = 4096

            analysis = call_gemini(prompt, gemini_file_info, max_tokens=max_tok)
            result["analysis"] = analysis or "*Analysis unavailable.*"

        results.append(result)

        ad_elapsed = time.time() - ad_start
        total_elapsed = time.time() - pipeline_start
        remaining_ads = total - (idx + 1)
        avg_per_ad = total_elapsed / (idx + 1)
        eta_seconds = remaining_ads * avg_per_ad
        eta_str = f"{int(eta_seconds//60)}m{int(eta_seconds%60)}s" if eta_seconds >= 60 else f"{int(eta_seconds)}s"

        log(f"  ✓ Done ({len(result['analysis'])} chars, {ad_elapsed:.0f}s) — ETA remaining: {eta_str}")

        # Checkpoint save every 10 ads to prevent data loss on timeout
        if (idx + 1) % 10 == 0 and idx + 1 < total:
            checkpoint_path = os.path.join(output_dir, "checkpoint_results.json")
            try:
                with open(checkpoint_path, "w") as f:
                    json.dump({"completed": len(results), "total": total, "results": results}, f, indent=2)
                log(f"  💾 Checkpoint saved: {len(results)}/{total} ads → {checkpoint_path}")
            except Exception as e:
                log(f"  Checkpoint save failed: {e}", "WARN")

    # ── PERSONA SYNTHESIS (if persona mode) ──
    persona_synthesis = None
    if args.analysis_type == "persona" and len(results) > 1:
        log("")
        log("━" * 40)
        log("PERSONA SYNTHESIS: Cross-ad analysis with 3-layer taxonomy")
        log("━" * 40)
        synth_prompt = build_persona_synthesis_prompt(results, batch_avgs)
        persona_synthesis = call_gemini(synth_prompt, max_tokens=16384)
        if persona_synthesis:
            log(f"  ✓ Synthesis complete ({len(persona_synthesis)} chars)")
        else:
            log("  Synthesis failed", "ERROR")

    # ── VALENCE SYNTHESIS (if valence mode) ──
    valence_synthesis = None
    if args.analysis_type == "valence" and len(results) > 1:
        log("")
        log("━" * 40)
        log("VALENCE SYNTHESIS: Psychological diversity matrix mapping")
        log("━" * 40)
        synth_prompt = build_valence_synthesis_prompt(results, batch_avgs)
        valence_synthesis = call_gemini(synth_prompt, max_tokens=16384)
        if valence_synthesis:
            log(f"  ✓ Valence synthesis complete ({len(valence_synthesis)} chars)")
        else:
            log("  Valence synthesis failed", "ERROR")

    # ── GROWTH STRATEGY: Run all 3 synthesis passes ──
    opportunity_synthesis = None
    if args.analysis_type == "growth-strategy":
        # Run valence synthesis
        if len(results) > 1:
            log("")
            log("━" * 40)
            log("GROWTH STRATEGY SYNTHESIS 1/3: Valence")
            log("━" * 40)
            valence_synth_results = [{"ad_name": r["ad_name"], "analysis": r.get("valence_analysis", ""),
                                      "insights": r.get("insights", {})} for r in results]
            synth_prompt = build_valence_synthesis_prompt(valence_synth_results, batch_avgs)
            valence_synthesis = call_gemini(synth_prompt, max_tokens=16384)
            if valence_synthesis:
                log(f"  ✓ Valence synthesis ({len(valence_synthesis)} chars)")

            log("")
            log("━" * 40)
            log("GROWTH STRATEGY SYNTHESIS 2/3: Persona")
            log("━" * 40)
            persona_synth_results = [{"ad_name": r["ad_name"], "analysis": r.get("persona_analysis", ""),
                                      "insights": r.get("insights", {})} for r in results]
            synth_prompt = build_persona_synthesis_prompt(persona_synth_results, batch_avgs)
            persona_synthesis = call_gemini(synth_prompt, max_tokens=16384)
            if persona_synthesis:
                log(f"  ✓ Persona synthesis ({len(persona_synthesis)} chars)")

            log("")
            log("━" * 40)
            log("GROWTH STRATEGY SYNTHESIS 3/3: Opportunity Synthesis")
            log("━" * 40)
            opp_prompt = build_opportunity_synthesis_prompt(
                results, batch_avgs, portfolio_health,
                valence_synthesis, persona_synthesis
            )
            opportunity_synthesis = call_gemini(opp_prompt, max_tokens=16384)
            if opportunity_synthesis:
                log(f"  ✓ Opportunity synthesis ({len(opportunity_synthesis)} chars)")
            else:
                log("  Opportunity synthesis failed", "ERROR")

    # ── STEP 6: Report ──
    log("")
    log("━" * 40)
    log("STEP 6/6: Generating RAG-scored report")
    log("━" * 40)
    md_path, json_path = generate_report(results, output_dir, args.analysis_type, batch_avgs,
                                         persona_synthesis, valence_synthesis,
                                         opportunity_synthesis, portfolio_health)

    # Clean up checkpoint file if pipeline completed successfully
    checkpoint_path = os.path.join(output_dir, "checkpoint_results.json")
    if os.path.exists(checkpoint_path):
        try:
            os.remove(checkpoint_path)
        except:
            pass

    # Summary
    total_time = time.time() - pipeline_start
    total_str = f"{int(total_time//60)}m{int(total_time%60)}s" if total_time >= 60 else f"{int(total_time)}s"
    avg_str = f"{total_time/len(results):.1f}s" if results else "N/A"

    log("")
    log("=" * 60)
    log("PIPELINE COMPLETE")
    log("=" * 60)
    log(f"Ads analysed:  {len(results)}")
    log(f"With media:    {sum(1 for r in results if r['gemini_uploaded'])}")
    log(f"Metadata only: {sum(1 for r in results if not r['gemini_uploaded'])}")
    log(f"Total time:    {total_str} ({avg_str} per ad)")
    log(f"Frameworks:    Emotional ID · Story · Awareness · Angle · RAG · Lifecycle · ICE")
    log(f"Report:  {md_path}")
    log(f"JSON:    {json_path}")
    log(f"Assets:  {assets_dir}")
    if persona_synthesis:
        log(f"Persona: {os.path.join(output_dir, 'persona_synthesis.md')}")
    if valence_synthesis:
        log(f"Valence: {os.path.join(output_dir, 'valence_synthesis.md')}")
    if opportunity_synthesis:
        log(f"Opportunities: {os.path.join(output_dir, 'opportunity_synthesis.md')}")
    if portfolio_health:
        log(f"Health:  {os.path.join(output_dir, 'portfolio_health.json')}")


if __name__ == "__main__":
    main()
