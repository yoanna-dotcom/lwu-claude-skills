#!/usr/bin/env python3
"""
Creative Library Builder — Foreplay → Gemini → JSON output
Pulls ads from a Foreplay board, classifies each against the 56 LWU frameworks
via Gemini, outputs a JSON plan for Claude to upload to Notion.

Usage:
  python3 build_library.py --board-id <id> --limit 5 --frameworks frameworks.json --output output.json
  python3 build_library.py --test-auth

The script never touches Notion. It only:
  1. Pulls ads from Foreplay
  2. Downloads creative assets
  3. Sends to Gemini for classification
  4. Writes a JSON plan with {ad, classification, asset_path, framework_match}

Claude then reads that JSON and orchestrates Notion uploads via MCP.
"""

import argparse
import json
import os
import re
import sys
import time
import pathlib
import requests


# ============================================================
# CONFIG
# ============================================================

def _load_key(name):
    kf = pathlib.Path.home() / ".claude" / "api_keys.json"
    if kf.exists():
        with open(kf) as f:
            return json.load(f).get(name, "")
    return ""


FOREPLAY_API_KEY = _load_key("foreplay_api_key")
GEMINI_API_KEY = _load_key("gemini_api_key")

FOREPLAY_BASE = "https://public.api.foreplay.co"
GEMINI_MODEL = "gemini-2.5-flash"

# Track credit usage in-process
_credits_used = 0
_credits_remaining = None


def log(msg):
    print(f"  {msg}", flush=True)


def safe_filename(name):
    return re.sub(r'[^\w\-.]', '_', name)[:60]


# ============================================================
# FOREPLAY API
# ============================================================

def foreplay_get(path, params=None):
    """Make a Foreplay API GET call. Tracks credits via response headers."""
    global _credits_used, _credits_remaining
    url = f"{FOREPLAY_BASE}{path}"
    headers = {"Authorization": FOREPLAY_API_KEY}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    except Exception as e:
        log(f"Foreplay request failed: {e}")
        return None

    # Track credits
    cost = resp.headers.get("X-Credit-Cost")
    remaining = resp.headers.get("X-Credits-Remaining")
    if cost:
        try:
            _credits_used += int(cost)
        except ValueError:
            pass
    if remaining:
        try:
            _credits_remaining = int(remaining)
        except ValueError:
            pass

    if resp.status_code == 401:
        log("Foreplay auth failed (401). Check foreplay_api_key in ~/.claude/api_keys.json")
        return None
    if resp.status_code == 402:
        log("Foreplay: insufficient credits (402). Aborting.")
        return None
    if resp.status_code == 429:
        log("Foreplay: rate limited (429). Sleeping 10s...")
        time.sleep(10)
        return foreplay_get(path, params)
    if resp.status_code != 200:
        log(f"Foreplay error {resp.status_code}: {resp.text[:200]}")
        return None
    return resp.json()


def list_boards(limit=10, offset=0):
    return foreplay_get("/api/boards", {"limit": limit, "offset": offset})


def get_board_ads(board_id, limit=10, cursor=None):
    params = {"board_id": board_id, "limit": limit}
    if cursor:
        params["cursor"] = cursor
    return foreplay_get("/api/board/ads", params)


# ============================================================
# ASSET DOWNLOAD
# ============================================================

def download_asset(url, filepath):
    try:
        resp = requests.get(url, timeout=120, stream=True, allow_redirects=True)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
    except Exception as e:
        log(f"Download failed: {e}")
    return False


def pick_asset_url(ad):
    """Prefer image > thumbnail > video > first card asset (for carousel/DCO)."""
    if ad.get("image"):
        return ad["image"], "image"
    if ad.get("thumbnail"):
        return ad["thumbnail"], "image"
    if ad.get("video"):
        return ad["video"], "video"
    # Carousel / DCO / multi-image ads store assets in cards[]
    cards = ad.get("cards") or []
    for c in cards:
        if isinstance(c, dict):
            if c.get("image"):
                return c["image"], "image"
            if c.get("thumbnail"):
                return c["thumbnail"], "image"
            if c.get("video"):
                return c["video"], "video"
    # Last resort: avatar (usually a logo, least useful for classification)
    if ad.get("avatar"):
        return ad["avatar"], "image"
    return None, None


# ============================================================
# GEMINI — Upload + Classify
# ============================================================

def upload_to_gemini(filepath):
    """Upload file to Gemini Files API, poll for ACTIVE if video."""
    ext = os.path.splitext(filepath)[1].lower()
    mime_map = {
        ".mp4": "video/mp4", ".mov": "video/quicktime",
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/jpeg")
    file_size = os.path.getsize(filepath)

    init_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={GEMINI_API_KEY}"
    init_headers = {
        "X-Goog-Upload-Protocol": "resumable",
        "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(file_size),
        "X-Goog-Upload-Header-Content-Type": mime_type,
        "Content-Type": "application/json",
    }
    resp = requests.post(init_url, headers=init_headers,
                         json={"file": {"display_name": os.path.basename(filepath)}}, timeout=60)
    if resp.status_code not in (200, 201):
        log(f"Gemini init failed: {resp.status_code}")
        return None

    upload_url = None
    for k, v in resp.headers.items():
        if k.lower() == "x-goog-upload-url":
            upload_url = v
            break
    if not upload_url:
        return None

    with open(filepath, 'rb') as f:
        data = f.read()
    resp = requests.post(upload_url, headers={
        "Content-Length": str(file_size),
        "X-Goog-Upload-Offset": "0",
        "X-Goog-Upload-Command": "upload, finalize",
    }, data=data, timeout=300)
    if resp.status_code not in (200, 201):
        log(f"Gemini upload failed: {resp.status_code}")
        return None

    file_info = resp.json().get("file", {})
    if "video" in mime_type:
        file_name = file_info.get("name", "")
        for _ in range(24):
            poll = requests.get(f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={GEMINI_API_KEY}", timeout=30)
            if poll.status_code == 200:
                state = poll.json().get("state", "")
                if state == "ACTIVE":
                    file_info = poll.json()
                    break
                elif state == "FAILED":
                    return None
            time.sleep(5)

    return {
        "uri": file_info.get("uri", ""),
        "mimeType": file_info.get("mimeType", mime_type),
    }


def call_gemini(prompt, file_info=None):
    parts = []
    if file_info and file_info.get("uri"):
        parts.append({"fileData": {"fileUri": file_info["uri"], "mimeType": file_info.get("mimeType", "image/jpeg")}})
    parts.append({"text": prompt})
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": parts}], "generationConfig": {"maxOutputTokens": 4096, "temperature": 0.2}}
    try:
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code == 200:
            candidates = resp.json().get("candidates", [])
            if candidates:
                return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        log(f"Gemini error {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log(f"Gemini request error: {e}")
    return None


def build_classification_prompt(frameworks, board_hint=""):
    """Build the Gemini classification prompt with the 56 frameworks inline."""
    framework_list = "\n".join(f'- "{f["name"]}" (category: {f.get("category","")})' for f in frameworks)
    hint_line = f'\nBoard this came from: "{board_hint}" (use as a hint, but override if the creative clearly matches a different framework).\n' if board_hint else ""
    return f"""You are classifying an ad creative for LWU's internal creative library.

Pick the ONE framework from this list that best describes this ad's structural approach:

{framework_list}
{hint_line}
Return ONLY valid JSON with these exact keys. No prose, no markdown fences:

{{
  "framework_match": "exact name from the list above",
  "confidence": "high | medium | low",
  "angle": "Gifting | Social Proof | Superiority | Heritage | Product Feature | Urgency | Fear Removal | Identity | Other",
  "hook_type": "Problem-Solution | Identity | Social Proof | Curiosity | Seasonal | Offer | Other",
  "production_style": "Clean Brand | Lo-fi UGC | Editorial | Overlay-Heavy | Other",
  "summary": "One paragraph (2-3 sentences) describing what the creative shows and why it matches that framework. Be concrete — reference specific visuals or text in the creative."
}}"""


def classify_creative(filepath, frameworks, board_hint=""):
    gemini_file = upload_to_gemini(filepath)
    if not gemini_file:
        return None
    prompt = build_classification_prompt(frameworks, board_hint)
    response = call_gemini(prompt, gemini_file)
    if not response:
        return None
    # Strip markdown fences if present
    clean = response.strip()
    if clean.startswith("```"):
        clean = re.sub(r'^```\w*\n?', '', clean)
        clean = re.sub(r'\n?```$', '', clean)
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        log(f"Gemini returned non-JSON: {response[:200]}")
        return None


# ============================================================
# MAIN
# ============================================================

def cmd_test_auth():
    """Quick sanity check: can we call Foreplay + get remaining credits?"""
    if not FOREPLAY_API_KEY:
        print("❌ No foreplay_api_key in ~/.claude/api_keys.json")
        return 1
    result = list_boards(limit=1)
    if result is None:
        print("❌ Foreplay auth failed")
        return 1
    boards = result.get("data", [])
    print(f"✅ Foreplay auth works")
    print(f"   Credits remaining: {_credits_remaining}")
    print(f"   First board: {boards[0].get('name') if boards else 'none'}")
    return 0


def cmd_list_boards():
    """List all boards user has access to."""
    offset = 0
    all_boards = []
    while True:
        result = list_boards(limit=10, offset=offset)
        if not result:
            break
        data = result.get("data", [])
        if not data:
            break
        all_boards.extend(data)
        offset += len(data)
        if len(data) < 10:
            break
    print(f"\nFound {len(all_boards)} boards. Credits remaining: {_credits_remaining}\n")
    for b in all_boards:
        print(f"  {b.get('id'):<40} {b.get('name')}")
    return 0


def cmd_build(args):
    if not FOREPLAY_API_KEY or not GEMINI_API_KEY:
        print("Missing API keys in ~/.claude/api_keys.json")
        return 1

    # Load frameworks
    if not os.path.exists(args.frameworks):
        print(f"Frameworks file not found: {args.frameworks}")
        print("Run Claude to cache the Notion frameworks first.")
        return 1
    with open(args.frameworks) as f:
        frameworks = json.load(f)
    print(f"Loaded {len(frameworks)} frameworks from {args.frameworks}")

    # Credit cap check
    credit_cap = args.credit_cap
    print(f"Credit cap for this run: {credit_cap}")

    # Fetch board ads
    print(f"\nPulling board {args.board_id} (limit {args.limit})...")
    result = get_board_ads(args.board_id, limit=args.limit)
    if not result:
        print("Failed to pull board")
        return 1
    ads = result.get("data", [])
    board_name = result.get("metadata", {}).get("board_name", "")
    print(f"Got {len(ads)} ads. Credits used so far: {_credits_used}, remaining: {_credits_remaining}")

    # Prepare assets dir
    work_dir = os.path.join("/tmp", "creative-library", safe_filename(args.board_id))
    assets_dir = os.path.join(work_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Process each ad
    output = []
    for i, ad in enumerate(ads):
        if _credits_used >= credit_cap:
            print(f"\n⛔ Credit cap hit ({_credits_used}/{credit_cap}). Stopping.")
            break

        ad_id = ad.get("id") or ad.get("ad_id") or f"unknown_{i}"
        ad_name = (ad.get("headline") or ad.get("name") or ad_id)[:50]
        print(f"\n[{i+1}/{len(ads)}] {ad_name} ({ad_id})")

        asset_url, asset_type = pick_asset_url(ad)
        if not asset_url:
            fmt = ad.get("display_format", "?")
            populated = [k for k in ["image","thumbnail","video","cards","avatar"] if ad.get(k)]
            log(f"No asset URL found (format={fmt}, populated fields: {populated}), skipping")
            continue

        ext = "mp4" if asset_type == "video" else "jpg"
        filename = f"{safe_filename(ad_id)}.{ext}"
        filepath = os.path.join(assets_dir, filename)

        if not os.path.exists(filepath) or os.path.getsize(filepath) < 5000:
            if not download_asset(asset_url, filepath):
                log("Download failed, skipping")
                continue

        size_kb = os.path.getsize(filepath) / 1024
        if size_kb < 5:
            log(f"Asset too small ({size_kb:.0f} KB), likely broken, skipping")
            continue
        log(f"Downloaded {asset_type} ({size_kb:.0f} KB)")

        classification = classify_creative(filepath, frameworks, board_hint=args.board_hint)
        if not classification:
            log("Classification failed, skipping")
            continue

        log(f"✓ Framework: {classification.get('framework_match')}  ({classification.get('confidence')})")

        output.append({
            "ad_id": ad_id,
            "ad_name": ad_name,
            "source_board_id": args.board_id,
            "source_board_hint": args.board_hint,
            "brand": ad.get("brand_id", ""),
            "display_format": ad.get("display_format", ""),
            "asset_type": asset_type,
            "asset_url": asset_url,
            "asset_local_path": filepath,
            "headline": ad.get("headline", ""),
            "description": ad.get("description", ""),
            "cta_title": ad.get("cta_title", ""),
            "link_url": ad.get("link_url", ""),
            "classification": classification,
            "foreplay_ad_url": f"https://app.foreplay.co/ad/{ad_id}" if ad_id else "",
        })

        # Rate-limit buffer
        time.sleep(1)

    # Write output
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump({
            "board_id": args.board_id,
            "board_hint": args.board_hint,
            "ads_processed": len(output),
            "credits_used_foreplay": _credits_used,
            "credits_remaining": _credits_remaining,
            "results": output,
        }, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ Processed {len(output)} creatives")
    print(f"   Output: {args.output}")
    print(f"   Foreplay credits used: {_credits_used}")
    print(f"   Foreplay credits remaining: {_credits_remaining}")
    return 0


def cmd_urls(args):
    """Process a plain urls.txt file — download each, classify with Gemini, write output JSON.
    No Foreplay credits consumed — only Gemini API usage."""
    if not GEMINI_API_KEY:
        print("Missing gemini_api_key in ~/.claude/api_keys.json")
        return 1
    if not os.path.exists(args.frameworks):
        print(f"Frameworks file not found: {args.frameworks}")
        return 1
    with open(args.frameworks) as f:
        frameworks = json.load(f)
    # Filter to only frameworks with a source_page_id (so we only classify into valid targets)
    frameworks = [f for f in frameworks if f.get("source_page_id")]
    print(f"Loaded {len(frameworks)} frameworks (filtered to those with source pages)")

    with open(args.urls_file) as f:
        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    print(f"Loaded {len(urls)} URLs from {args.urls_file}")

    if args.limit and args.limit < len(urls):
        urls = urls[:args.limit]
        print(f"Limited to first {args.limit} URLs")

    work_dir = os.path.join("/tmp", "creative-library", safe_filename(args.source_label))
    assets_dir = os.path.join(work_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    output = []
    for i, url in enumerate(urls):
        print(f"\n[{i+1}/{len(urls)}] {url[:80]}")
        # Derive an ID from the URL
        fname = os.path.basename(url.split("?")[0])
        ad_id = safe_filename(fname.rsplit(".", 1)[0]) or f"url_{i}"
        ext = "jpg"
        # Try to guess extension
        if "." in fname:
            ext = fname.rsplit(".", 1)[1].lower().split("?")[0]
            if ext not in ("jpg", "jpeg", "png", "gif", "webp", "mp4", "mov"):
                ext = "jpg"
        filepath = os.path.join(assets_dir, f"{ad_id}.{ext}")

        if not os.path.exists(filepath) or os.path.getsize(filepath) < 5000:
            if not download_asset(url, filepath):
                log("Download failed, skipping")
                continue

        size_kb = os.path.getsize(filepath) / 1024
        if size_kb < 5:
            log(f"Too small ({size_kb:.0f} KB), skipping")
            continue
        log(f"Downloaded ({size_kb:.0f} KB)")

        classification = classify_creative(filepath, frameworks, board_hint=args.board_hint)
        if not classification:
            log("Classification failed, skipping")
            continue
        log(f"✓ Framework: {classification.get('framework_match')}  ({classification.get('confidence')})")

        output.append({
            "ad_id": ad_id,
            "ad_name": fname,
            "source_board_id": "",
            "source_board_hint": args.source_label,
            "brand": "",
            "display_format": "image",
            "asset_type": "image",
            "asset_url": url,
            "asset_local_path": filepath,
            "headline": "",
            "description": "",
            "cta_title": "",
            "link_url": "",
            "classification": classification,
            "foreplay_ad_url": "",
        })
        time.sleep(1)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump({
            "source": args.source_label,
            "urls_processed": len(output),
            "results": output,
        }, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ Classified {len(output)}/{len(urls)} creatives")
    print(f"   Output: {args.output}")
    print(f"   Foreplay credits used: 0 (URL list mode)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Foreplay → Gemini classification pipeline")
    parser.add_argument("--test-auth", action="store_true", help="Check Foreplay auth works")
    parser.add_argument("--list-boards", action="store_true", help="List all Foreplay boards")
    parser.add_argument("--board-id", help="Foreplay board ID to import")
    parser.add_argument("--urls-file", help="Path to a plain text file of image URLs (one per line) — alternative to --board-id, no Foreplay credits used")
    parser.add_argument("--source-label", default="Manual", help="Label for the 'Source' field when using --urls-file (e.g. 'Magritte — <collection name>')")
    parser.add_argument("--board-hint", default="", help="Board name/category hint for Gemini (e.g. 'Social Proof')")
    parser.add_argument("--limit", type=int, default=5, help="Max ads to pull from board (default 5)")
    parser.add_argument("--frameworks", default="", help="Path to frameworks.json (name+category list)")
    parser.add_argument("--output", default="", help="Output JSON path")
    parser.add_argument("--credit-cap", type=int, default=1500, help="Hard credit cap (default 1500)")
    args = parser.parse_args()

    if args.test_auth:
        return cmd_test_auth()
    if args.list_boards:
        cmd_test_auth()  # show remaining credits first
        return cmd_list_boards()
    if args.board_id:
        if not args.frameworks or not args.output:
            print("Need --frameworks and --output for build mode")
            return 1
        return cmd_build(args)
    if args.urls_file:
        if not args.frameworks or not args.output:
            print("Need --frameworks and --output for urls-file mode")
            return 1
        return cmd_urls(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
