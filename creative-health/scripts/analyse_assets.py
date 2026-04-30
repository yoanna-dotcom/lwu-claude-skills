#!/usr/bin/env python3
"""
Creative Health — Gemini Asset Analysis (Deep Mode)
Downloads top-spend creative assets, sends to Gemini for hook/headline extraction.
Produces gemini_analysis.json for the report generator.
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import requests

def _load_key(name):
    import pathlib
    kf = pathlib.Path.home() / ".claude" / "api_keys.json"
    if kf.exists():
        with open(kf) as f:
            return json.load(f).get(name, "")
    return ""

META_ACCESS_TOKEN = _load_key("meta_access_token")
GEMINI_API_KEY = _load_key("gemini_api_key")
GEMINI_MODEL = "gemini-2.5-flash"
API_VERSION = "v21.0"
META_BASE = f"https://graph.facebook.com/{API_VERSION}"


def log(msg):
    print(f"  {msg}")


def safe_filename(name):
    return re.sub(r'[^\w\-.]', '_', name)[:60]


# ============================================================
# META API — Asset URL Resolution
# ============================================================

def get_video_source_url(video_id):
    try:
        resp = requests.get(f"{META_BASE}/{video_id}", params={
            "access_token": META_ACCESS_TOKEN, "fields": "source,length"
        }, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("source"), data.get("length", 0)
    except Exception as e:
        log(f"Video {video_id} error: {e}")
    return None, 0


def get_image_url_from_hash(image_hash, account_id):
    try:
        resp = requests.get(f"{META_BASE}/{account_id}/adimages", params={
            "access_token": META_ACCESS_TOKEN, "hashes": json.dumps([image_hash])
        }, timeout=30)
        if resp.status_code == 200:
            for key, val in resp.json().get("data", {}).items():
                url = val.get("url") or val.get("url_128") or val.get("permalink_url")
                if url:
                    return url
    except Exception:
        pass
    return None


def resolve_asset(ad_id, account_id):
    """Get the creative asset URL and type for an ad."""
    resp = requests.get(f"{META_BASE}/{ad_id}", params={
        "access_token": META_ACCESS_TOKEN,
        "fields": "creative{id,image_url,thumbnail_url,object_story_spec,asset_feed_spec}"
    }, timeout=30)

    if resp.status_code != 200:
        return None

    creative = resp.json().get("creative", {})
    oss = creative.get("object_story_spec", {})

    # Try video first
    video_data = oss.get("video_data", {})
    video_id = video_data.get("video_id")
    if video_id:
        source_url, length = get_video_source_url(video_id)
        if source_url:
            return {"type": "video", "url": source_url, "video_id": video_id, "duration": length}

    # Try link_data video
    link_data = oss.get("link_data", {})
    for child in link_data.get("child_attachments", []):
        vid = child.get("video_id")
        if vid:
            source_url, length = get_video_source_url(vid)
            if source_url:
                return {"type": "video", "url": source_url, "video_id": vid, "duration": length}

    # Try image
    image_url = creative.get("image_url") or creative.get("thumbnail_url")
    if not image_url and link_data:
        image_url = link_data.get("picture")
    if image_url:
        return {"type": "image", "url": image_url, "duration": 0}

    # Try asset_feed_spec
    afs = creative.get("asset_feed_spec", {})
    for vid_item in afs.get("videos", []):
        vid = vid_item.get("video_id")
        if vid:
            source_url, length = get_video_source_url(vid)
            if source_url:
                return {"type": "video", "url": source_url, "video_id": vid, "duration": length}
    for img_item in afs.get("images", []):
        img_hash = img_item.get("hash")
        if img_hash:
            img_url = get_image_url_from_hash(img_hash, account_id)
            if img_url:
                return {"type": "image", "url": img_url, "duration": 0}

    # Last resort: thumbnail
    thumb = creative.get("thumbnail_url")
    if thumb:
        return {"type": "image", "url": thumb, "duration": 0}

    return None


def download_asset(url, filepath):
    """Download a file from URL."""
    try:
        resp = requests.get(url, timeout=120, stream=True, allow_redirects=True)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            size_kb = os.path.getsize(filepath) / 1024
            return True
        return False
    except Exception:
        return False


# ============================================================
# GEMINI — Upload + Analyse
# ============================================================

def upload_to_gemini(filepath):
    """Upload file to Gemini Files API."""
    ext = os.path.splitext(filepath)[1].lower()
    mime_map = {
        ".mp4": "video/mp4", ".mov": "video/quicktime",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "application/octet-stream")
    file_size = os.path.getsize(filepath)
    display_name = os.path.basename(filepath)

    # Initiate resumable upload
    init_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={GEMINI_API_KEY}"
    init_headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(file_size),
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json",
    }

    resp = requests.post(init_url, headers=init_headers,
                         json={"file": {"display_name": display_name}}, timeout=60)
    if resp.status_code not in (200, 201):
        log(f"Gemini upload init failed: {resp.status_code}")
        return None

    upload_url = None
    for key, val in resp.headers.items():
        if key.lower() == "x-goog-upload-url":
            upload_url = val
            break
    if not upload_url:
        return None

    # Upload bytes
    with open(filepath, 'rb') as f:
        data = f.read()
    upload_headers = {
        "Content-Length": str(file_size),
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize",
    }
    resp = requests.post(upload_url, headers=upload_headers, data=data, timeout=300)
    if resp.status_code not in (200, 201):
        log(f"Gemini upload failed: {resp.status_code}")
        return None

    file_info = resp.json().get("file", {})

    # Poll for ACTIVE status (videos need processing)
    if "video" in mime_type:
        file_name = file_info.get("name", "")
        for _ in range(24):  # 2 minutes max
            poll_url = f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={GEMINI_API_KEY}"
            poll_resp = requests.get(poll_url, timeout=30)
            if poll_resp.status_code == 200:
                state = poll_resp.json().get("state", "")
                if state == "ACTIVE":
                    file_info = poll_resp.json()
                    break
                elif state == "FAILED":
                    log("Gemini video processing failed")
                    return None
            time.sleep(5)

    return {
        "uri": file_info.get("uri", ""),
        "mimeType": file_info.get("mimeType", mime_type),
        "name": file_info.get("name", ""),
    }


def call_gemini(prompt, file_info=None):
    """Call Gemini with a prompt and optional file."""
    parts = []
    if file_info and file_info.get("uri"):
        parts.append({
            "fileData": {
                "fileUri": file_info["uri"],
                "mimeType": file_info.get("mimeType", "image/jpeg"),
            }
        })
    parts.append({"text": prompt})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.2},
    }

    try:
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code == 200:
            candidates = resp.json().get("candidates", [])
            if candidates:
                return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        else:
            log(f"Gemini API error: {resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        log(f"Gemini request error: {e}")
    return None


GEMINI_PROMPT = """Analyse this ad creative. Focus ONLY on the text and visual elements that appear ON the creative itself (not the ad copy below it).

Return your analysis in this exact JSON format — no markdown, no explanation, just the JSON:

{
  "hook_text": "The exact text visible in the first 3 seconds / top section of the creative. If no text is visible, write 'No text overlay'",
  "headline_text": "Any headline or large text visible on the creative. If same as hook_text, write 'Same as hook'",
  "hook_type": "One of: Question, Bold Claim, Social Proof, Problem Agitation, Testimonial, Demonstration, Offer/Price, Pattern Interrupt, No Hook",
  "visual_description": "One sentence describing what the viewer sees — the setting, the product, the style",
  "asset_type": "One of: Static Image, Video, Carousel, GIF/Animation",
  "estimated_duration_sec": 0
}

For videos: set estimated_duration_sec to the video length in seconds. For images: set to 0.
For the hook_text: transcribe the EXACT text visible on screen, not a description of it. Include text overlays, captions, and any baked-in text. If it's a video, focus on what appears in the first 3 seconds."""


def analyse_ad(ad_id, ad_name, asset_info, assets_dir):
    """Download asset, upload to Gemini, extract hook/headline."""
    # Download
    ext = "mp4" if asset_info["type"] == "video" else "jpg"
    filename = f"{safe_filename(ad_name)}_{ad_id[-6:]}.{ext}"
    filepath = os.path.join(assets_dir, filename)

    if not os.path.exists(filepath) or os.path.getsize(filepath) < 5000:
        success = download_asset(asset_info["url"], filepath)
        if not success:
            log(f"Failed to download {ad_name[:40]}")
            return None

    file_size = os.path.getsize(filepath)
    if file_size < 5000:
        log(f"Asset too small ({file_size} bytes) — likely a thumbnail, skipping")
        return None

    size_mb = file_size / (1024 * 1024)
    log(f"Downloaded {asset_info['type']} ({size_mb:.1f}MB): {ad_name[:50]}")

    # Upload to Gemini
    gemini_file = upload_to_gemini(filepath)
    if not gemini_file:
        log(f"Failed to upload to Gemini: {ad_name[:40]}")
        return None

    # Call Gemini
    response = call_gemini(GEMINI_PROMPT, gemini_file)
    if not response:
        log(f"Gemini returned empty: {ad_name[:40]}")
        return None

    # Parse JSON response
    try:
        # Strip markdown code fences if present
        clean = response.strip()
        if clean.startswith("```"):
            clean = re.sub(r'^```\w*\n?', '', clean)
            clean = re.sub(r'\n?```$', '', clean)
        result = json.loads(clean)
        result["ad_id"] = ad_id
        result["ad_name"] = ad_name
        result["asset_type_detected"] = asset_info["type"]
        result["video_duration_api"] = asset_info.get("duration", 0)
        return result
    except json.JSONDecodeError:
        log(f"Failed to parse Gemini response for {ad_name[:40]}")
        log(f"  Raw: {response[:200]}")
        return None


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Gemini creative asset analysis")
    parser.add_argument("--ads-csv", required=True, help="Path to ads.csv from pull")
    parser.add_argument("--account", required=True, help="Ad account ID (act_XXX)")
    parser.add_argument("--top-n", type=int, default=15, help="Number of top ads to analyse")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()

    # Load ads CSV, get top N by spend
    ads = []
    with open(args.ads_csv, "r") as f:
        for row in csv.DictReader(f):
            spend = float(row.get("spend", 0))
            if spend > 0:
                ads.append(row)
    ads.sort(key=lambda x: -float(x.get("spend", 0)))
    top_ads = ads[:args.top_n]

    print(f"Analysing top {len(top_ads)} ads by spend with Gemini...")

    # Create assets directory
    assets_dir = os.path.join(args.output, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    results = []
    for i, ad in enumerate(top_ads):
        ad_id = ad["ad_id"]
        ad_name = ad["ad_name"]
        spend = float(ad.get("spend", 0))

        print(f"\n[{i+1}/{len(top_ads)}] {ad_name[:60]} (£{spend:.0f})")

        # Resolve asset URL
        asset_info = resolve_asset(ad_id, args.account)
        if not asset_info:
            log("Could not resolve asset URL — skipping")
            continue

        # Analyse
        result = analyse_ad(ad_id, ad_name, asset_info, assets_dir)
        if result:
            # Attach performance metrics
            result["spend"] = spend
            result["purchases"] = int(float(ad.get("purchases", 0)))
            result["cpa"] = round(spend / result["purchases"], 2) if result["purchases"] > 0 else 0
            result["roas"] = float(ad.get("roas", 0))
            result["ctr"] = float(ad.get("ctr", 0))
            result["impressions"] = int(float(ad.get("impressions", 0)))
            results.append(result)
            log(f"✓ Hook: \"{result.get('hook_text', 'N/A')[:60]}\"")
            log(f"  Type: {result.get('hook_type', 'Unknown')} | {result.get('asset_type', 'Unknown')}")

        # Rate limit buffer
        time.sleep(2)

    # Save results
    output_path = os.path.join(args.output, "gemini_analysis.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*50}")
    print(f"Gemini analysis complete: {len(results)}/{len(top_ads)} ads analysed")
    print(f"Results saved to {output_path}")

    # Summary
    hook_types = {}
    for r in results:
        ht = r.get("hook_type", "Unknown")
        hook_types[ht] = hook_types.get(ht, 0) + 1
    print(f"\nHook types found:")
    for ht, count in sorted(hook_types.items(), key=lambda x: -x[1]):
        print(f"  {ht}: {count}")


if __name__ == "__main__":
    main()
