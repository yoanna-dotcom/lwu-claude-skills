#!/usr/bin/env python3
"""
Creative Health — Meta API Data Pull
Pulls all ads with spend > 0 for a given account and date range.
Includes video metrics and video durations.
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

META_ACCESS_TOKEN = "EAAUeobHyYdsBQZCVPLlEq42kOIGHojQbz8Ag2a007TJb7vQe8TRBfWuZAFcOZBFxd3k0Eqoh6wZBrRW85ZAUsZBxV5gz2cfYQb9wYk3SViWtjk13SGPa9ZAvh1gZB2ZAnjlKg9lq3doCNTHwdFZCDSBMExNAc3LguYBPqH1tIhsYVGoJFruNkJ8NttOGw2iECIHgZDZD"
API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def api_get(url, params=None, retries=3):
    """Make a GET request to Meta API with retry logic."""
    if params:
        url = f"{url}?{urlencode(params)}"
    for attempt in range(retries):
        try:
            req = Request(url)
            with urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            body = e.read().decode() if hasattr(e, 'read') else str(e)
            if e.code == 400 and "rate limit" in body.lower():
                wait = 30 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            if attempt == retries - 1:
                print(f"  API error: {e.code} - {body[:200]}")
                return None
            time.sleep(5)
        except (URLError, Exception) as e:
            if attempt == retries - 1:
                print(f"  Request error: {e}")
                return None
            time.sleep(5)
    return None


def pull_insights(account_id, days):
    """Pull ad-level insights for the account."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    print(f"Pulling insights for {account_id} ({start_date} to {end_date})...")

    all_ads = []
    url = f"{BASE_URL}/{account_id}/insights"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "level": "ad",
        "time_range": json.dumps({"since": start_date, "until": end_date}),
        "fields": ",".join([
            "ad_name", "ad_id", "campaign_name", "adset_name",
            "spend", "impressions", "clicks", "ctr", "cpc", "cpm",
            "actions", "action_values",
            "video_play_actions", "video_thruplay_watched_actions",
            "video_p25_watched_actions", "video_p50_watched_actions",
            "video_p75_watched_actions", "video_p100_watched_actions",
        ]),
        "filtering": json.dumps([{"field": "spend", "operator": "GREATER_THAN", "value": "0"}]),
        "sort": "spend_descending",
        "limit": "500",
    }

    data = api_get(url, params)
    if not data or "data" not in data:
        print("ERROR: No data returned from API")
        sys.exit(1)

    all_ads.extend(data["data"])
    print(f"  Got {len(all_ads)} ads...")

    # Handle pagination
    while "paging" in data and "next" in data["paging"]:
        data = api_get(data["paging"]["next"])
        if data and "data" in data:
            all_ads.extend(data["data"])
            print(f"  Got {len(all_ads)} ads...")
        else:
            break

    return all_ads, start_date, end_date


def extract_action_value(actions, action_type_contains):
    """Extract a value from the actions array."""
    if not actions:
        return 0
    for action in actions:
        if action_type_contains in action.get("action_type", ""):
            return float(action.get("value", 0))
    return 0


def extract_video_metric(metric_list):
    """Extract value from a video metric array."""
    if not metric_list:
        return 0
    for item in metric_list:
        return float(item.get("value", 0))
    return 0


def get_video_durations(ad_ids):
    """Fetch video durations for ads that are videos."""
    print(f"Fetching video durations for up to {len(ad_ids)} ads...")
    durations = {}
    batch_size = 50

    for i in range(0, len(ad_ids), batch_size):
        batch = ad_ids[i:i + batch_size]
        for ad_id in batch:
            # Get creative
            creative_data = api_get(f"{BASE_URL}/{ad_id}", {
                "access_token": META_ACCESS_TOKEN,
                "fields": "creative{video_id}",
            })
            if not creative_data:
                continue

            creative = creative_data.get("creative", {})
            video_id = creative.get("video_id")
            if not video_id:
                continue

            # Get video length
            video_data = api_get(f"{BASE_URL}/{video_id}", {
                "access_token": META_ACCESS_TOKEN,
                "fields": "length",
            })
            if video_data and "length" in video_data:
                durations[ad_id] = float(video_data["length"])

        if i + batch_size < len(ad_ids):
            print(f"  Processed {min(i + batch_size, len(ad_ids))}/{len(ad_ids)} ads...")
            time.sleep(1)  # Rate limit buffer

    print(f"  Found durations for {len(durations)} video ads")
    return durations


def process_ads(raw_ads):
    """Process raw API data into structured rows."""
    rows = []
    video_ad_ids = []

    for ad in raw_ads:
        spend = float(ad.get("spend", 0))
        impressions = float(ad.get("impressions", 0))

        purchases = extract_action_value(ad.get("actions"), "purchase")
        if purchases == 0:
            purchases = extract_action_value(ad.get("actions"), "omni_purchase")
        purchase_value = extract_action_value(ad.get("action_values"), "purchase")
        if purchase_value == 0:
            purchase_value = extract_action_value(ad.get("action_values"), "omni_purchase")

        video_3sec = extract_video_metric(ad.get("video_play_actions"))
        thruplay = extract_video_metric(ad.get("video_thruplay_watched_actions"))
        video_p25 = extract_video_metric(ad.get("video_p25_watched_actions"))
        video_p50 = extract_video_metric(ad.get("video_p50_watched_actions"))
        video_p75 = extract_video_metric(ad.get("video_p75_watched_actions"))
        video_p100 = extract_video_metric(ad.get("video_p100_watched_actions"))

        ad_id = ad.get("ad_id", "")
        if video_3sec > 0 or thruplay > 0 or video_p25 > 0:
            video_ad_ids.append(ad_id)

        row = {
            "ad_name": ad.get("ad_name", ""),
            "ad_id": ad_id,
            "campaign_name": ad.get("campaign_name", ""),
            "adset_name": ad.get("adset_name", ""),
            "spend": round(spend, 2),
            "impressions": int(impressions),
            "clicks": int(float(ad.get("clicks", 0))),
            "ctr": round(float(ad.get("ctr", 0)), 2),
            "cpc": round(float(ad.get("cpc", 0)), 2),
            "cpm": round(float(ad.get("cpm", 0)), 2),
            "purchases": int(purchases),
            "purchase_value": round(purchase_value, 2),
            "roas": round(purchase_value / spend, 2) if spend > 0 else 0,
            "video_3sec": int(video_3sec),
            "thruplay": int(thruplay),
            "video_p25": int(video_p25),
            "video_p50": int(video_p50),
            "video_p75": int(video_p75),
            "video_p100": int(video_p100),
            "video_duration_sec": 0,
        }
        rows.append(row)

    # Fetch video durations
    if video_ad_ids:
        durations = get_video_durations(video_ad_ids)
        for row in rows:
            if row["ad_id"] in durations:
                row["video_duration_sec"] = round(durations[row["ad_id"]], 1)

    return rows


def save_csv(rows, output_path):
    """Save rows to CSV."""
    if not rows:
        print("No data to save")
        return

    fieldnames = [
        "ad_name", "ad_id", "campaign_name", "adset_name",
        "spend", "impressions", "clicks", "ctr", "cpc", "cpm",
        "purchases", "purchase_value", "roas",
        "video_3sec", "thruplay", "video_p25", "video_p50", "video_p75", "video_p100",
        "video_duration_sec",
    ]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} ads to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Pull ad data from Meta Marketing API")
    parser.add_argument("account_id", help="Meta ad account ID (e.g., act_123456789)")
    parser.add_argument("--days", type=int, default=30, help="Number of days to pull (default: 30)")
    parser.add_argument("--output", default="/tmp/creative-health", help="Output directory")
    args = parser.parse_args()

    # Ensure act_ prefix
    account_id = args.account_id
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"

    # Pull data
    raw_ads, start_date, end_date = pull_insights(account_id, args.days)
    print(f"Total ads with spend: {len(raw_ads)}")

    # Process
    rows = process_ads(raw_ads)

    # Summary
    total_spend = sum(r["spend"] for r in rows)
    total_purchases = sum(r["purchases"] for r in rows)
    video_count = sum(1 for r in rows if r["video_3sec"] > 0 or r["thruplay"] > 0)
    print(f"\nSummary:")
    print(f"  Ads: {len(rows)}")
    print(f"  Spend: £{total_spend:,.2f}")
    print(f"  Purchases: {total_purchases}")
    print(f"  Video ads: {video_count}")
    print(f"  Period: {start_date} to {end_date}")

    # Save
    output_path = os.path.join(args.output, "ads.csv")
    save_csv(rows, output_path)

    # Also save metadata
    meta = {
        "account_id": account_id,
        "days": args.days,
        "start_date": start_date,
        "end_date": end_date,
        "total_ads": len(rows),
        "total_spend": total_spend,
        "total_purchases": total_purchases,
        "video_ads": video_count,
        "pulled_at": datetime.now().isoformat(),
    }
    meta_path = os.path.join(args.output, "pull_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Metadata saved to {meta_path}")


if __name__ == "__main__":
    main()
