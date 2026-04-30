#!/usr/bin/env python3
"""
Creative Health — Meta API Data Pull v2
Pulls all ads with spend > 0, including frequency, reach, headlines,
daily account trends, and video durations.
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

def _load_key(name):
    import pathlib
    kf = pathlib.Path.home() / ".claude" / "api_keys.json"
    if kf.exists():
        with open(kf) as f:
            return json.load(f).get(name, "")
    return ""

META_ACCESS_TOKEN = _load_key("meta_access_token")
API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"


def api_get(url, params=None, retries=3):
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
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    print(f"Pulling ad-level insights for {account_id} ({start_date} to {end_date})...")

    all_ads = []
    url = f"{BASE_URL}/{account_id}/insights"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "level": "ad",
        "time_range": json.dumps({"since": start_date, "until": end_date}),
        "fields": ",".join([
            "ad_name", "ad_id", "campaign_name", "adset_name",
            "spend", "impressions", "clicks", "ctr", "cpc", "cpm",
            "reach", "frequency",
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

    while "paging" in data and "next" in data["paging"]:
        data = api_get(data["paging"]["next"])
        if data and "data" in data:
            all_ads.extend(data["data"])
            print(f"  Got {len(all_ads)} ads...")
        else:
            break

    return all_ads, start_date, end_date


def pull_account_frequency(account_id, days):
    """Pull account-level PERIOD frequency (the real number, not daily average)."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    print(f"Pulling account-level period frequency...")

    url = f"{BASE_URL}/{account_id}/insights"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "time_range": json.dumps({"since": start_date, "until": end_date}),
        "fields": "impressions,reach,frequency,spend,clicks,ctr,cpm",
    }
    data = api_get(url, params)
    if data and "data" in data and data["data"]:
        row = data["data"][0]
        result = {
            "impressions": int(float(row.get("impressions", 0))),
            "reach": int(float(row.get("reach", 0))),
            "frequency": round(float(row.get("frequency", 0)), 2),
            "spend": round(float(row.get("spend", 0)), 2),
        }
        print(f"  Period frequency: {result['frequency']} (impressions: {result['impressions']:,}, reach: {result['reach']:,})")
        return result
    print("  Could not pull account-level frequency")
    return {"impressions": 0, "reach": 0, "frequency": 0, "spend": 0}


def pull_daily_frequency(account_id, days):
    """Pull account-level daily frequency for the trend chart."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    print(f"Pulling daily frequency trends...")

    url = f"{BASE_URL}/{account_id}/insights"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "time_range": json.dumps({"since": start_date, "until": end_date}),
        "time_increment": "1",
        "fields": "spend,impressions,reach,frequency,cpm",
        "limit": "100",
    }

    data = api_get(url, params)
    if not data or "data" not in data:
        print("  Could not pull daily frequency")
        return []

    daily = []
    for row in data["data"]:
        daily.append({
            "date": row.get("date_start", ""),
            "spend": round(float(row.get("spend", 0)), 2),
            "impressions": int(float(row.get("impressions", 0))),
            "reach": int(float(row.get("reach", 0))),
            "frequency": round(float(row.get("frequency", 0)), 2),
            "cpm": round(float(row.get("cpm", 0)), 2),
        })

    # Handle pagination
    while "paging" in data and "next" in data["paging"]:
        data = api_get(data["paging"]["next"])
        if data and "data" in data:
            for row in data["data"]:
                daily.append({
                    "date": row.get("date_start", ""),
                    "spend": round(float(row.get("spend", 0)), 2),
                    "impressions": int(float(row.get("impressions", 0))),
                    "reach": int(float(row.get("reach", 0))),
                    "frequency": round(float(row.get("frequency", 0)), 2),
                    "cpm": round(float(row.get("cpm", 0)), 2),
                })
        else:
            break

    print(f"  Got {len(daily)} daily data points")
    return sorted(daily, key=lambda x: x["date"])


def pull_ad_creatives(ad_ids):
    """Pull headline and primary text for each ad via creative ID."""
    print(f"Pulling creative text for {len(ad_ids)} ads...")
    creatives = {}
    batch_size = 50

    for i in range(0, len(ad_ids), batch_size):
        batch = ad_ids[i:i + batch_size]
        for ad_id in batch:
            # Step 1: get the creative ID
            data = api_get(f"{BASE_URL}/{ad_id}", {
                "access_token": META_ACCESS_TOKEN,
                "fields": "creative{id}",
            })
            if not data:
                continue

            creative_id = data.get("creative", {}).get("id")
            if not creative_id:
                continue

            # Step 2: query the creative directly for title and body
            cr_data = api_get(f"{BASE_URL}/{creative_id}", {
                "access_token": META_ACCESS_TOKEN,
                "fields": "title,body",
            })
            if not cr_data:
                continue

            creatives[ad_id] = {
                "headline": cr_data.get("title", "") or "",
                "primary_text": cr_data.get("body", "") or "",
            }

        if i + batch_size < len(ad_ids):
            print(f"  Processed {min(i + batch_size, len(ad_ids))}/{len(ad_ids)} ads...")
            time.sleep(1)

    print(f"  Got creative text for {len(creatives)} ads")
    return creatives


def get_video_durations(ad_ids):
    """Fetch video durations via creative ID → video_id → length."""
    print(f"Fetching video durations for {len(ad_ids)} video ads...")
    durations = {}
    batch_size = 50

    for i in range(0, len(ad_ids), batch_size):
        batch = ad_ids[i:i + batch_size]
        for ad_id in batch:
            # Get creative ID first
            data = api_get(f"{BASE_URL}/{ad_id}", {
                "access_token": META_ACCESS_TOKEN,
                "fields": "creative{id,video_id}",
            })
            if not data:
                continue

            creative = data.get("creative", {})
            video_id = creative.get("video_id")

            # If no video_id on creative, try querying the creative directly
            if not video_id:
                creative_id = creative.get("id")
                if creative_id:
                    cr_data = api_get(f"{BASE_URL}/{creative_id}", {
                        "access_token": META_ACCESS_TOKEN,
                        "fields": "video_id,object_story_spec",
                    })
                    if cr_data:
                        video_id = cr_data.get("video_id")
                        if not video_id:
                            spec = cr_data.get("object_story_spec", {})
                            vd = spec.get("video_data", {})
                            video_id = vd.get("video_id")

            if not video_id:
                continue

            # Get video length
            vid_data = api_get(f"{BASE_URL}/{video_id}", {
                "access_token": META_ACCESS_TOKEN,
                "fields": "length",
            })
            if vid_data and "length" in vid_data:
                durations[ad_id] = float(vid_data["length"])

        if i + batch_size < len(ad_ids):
            print(f"  Processed {min(i + batch_size, len(ad_ids))}/{len(ad_ids)} ads...")
            time.sleep(1)

    print(f"  Found durations for {len(durations)} video ads")
    return durations


def extract_action_value(actions, action_type_contains):
    if not actions:
        return 0
    for action in actions:
        if action_type_contains in action.get("action_type", ""):
            return float(action.get("value", 0))
    return 0


def extract_video_metric(metric_list):
    if not metric_list:
        return 0
    for item in metric_list:
        return float(item.get("value", 0))
    return 0


def process_ads(raw_ads):
    rows = []
    video_ad_ids = []
    all_ad_ids = []

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
        all_ad_ids.append(ad_id)
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
            "reach": int(float(ad.get("reach", 0))),
            "frequency": round(float(ad.get("frequency", 0)), 2),
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
            "headline": "",
            "primary_text": "",
        }
        rows.append(row)

    # Fetch video durations
    if video_ad_ids:
        durations = get_video_durations(video_ad_ids)
        for row in rows:
            if row["ad_id"] in durations:
                row["video_duration_sec"] = round(durations[row["ad_id"]], 1)

    # Fetch headlines and primary text
    if all_ad_ids:
        creatives = pull_ad_creatives(all_ad_ids)
        for row in rows:
            if row["ad_id"] in creatives:
                row["headline"] = creatives[row["ad_id"]]["headline"]
                row["primary_text"] = creatives[row["ad_id"]]["primary_text"]

    return rows


def save_csv(rows, output_path):
    if not rows:
        print("No data to save")
        return

    fieldnames = [
        "ad_name", "ad_id", "campaign_name", "adset_name",
        "spend", "impressions", "clicks", "ctr", "cpc", "cpm",
        "reach", "frequency",
        "purchases", "purchase_value", "roas",
        "video_3sec", "thruplay", "video_p25", "video_p50", "video_p75", "video_p100",
        "video_duration_sec",
        "headline", "primary_text",
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

    account_id = args.account_id
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"

    # Pull ad-level data
    raw_ads, start_date, end_date = pull_insights(account_id, args.days)
    print(f"Total ads with spend: {len(raw_ads)}")

    # Process (includes fetching video durations + headlines)
    rows = process_ads(raw_ads)

    # Pull account-level period frequency (the correct number)
    account_freq = pull_account_frequency(account_id, args.days)

    # Pull daily frequency trends (for the chart)
    daily = pull_daily_frequency(account_id, args.days)

    # Summary
    total_spend = sum(r["spend"] for r in rows)
    total_purchases = sum(r["purchases"] for r in rows)
    video_count = sum(1 for r in rows if r["video_3sec"] > 0 or r["thruplay"] > 0)
    avg_freq = sum(r["frequency"] for r in rows if r["frequency"] > 0) / max(1, sum(1 for r in rows if r["frequency"] > 0))
    headline_count = sum(1 for r in rows if r["headline"])
    print(f"\nSummary:")
    print(f"  Ads: {len(rows)}")
    print(f"  Spend: £{total_spend:,.2f}")
    print(f"  Purchases: {total_purchases}")
    print(f"  Video ads: {video_count}")
    print(f"  Avg frequency: {avg_freq:.2f}")
    print(f"  Ads with headlines: {headline_count}")
    print(f"  Period: {start_date} to {end_date}")

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Save account-level frequency
    acct_freq_path = os.path.join(args.output, "account_frequency.json")
    with open(acct_freq_path, "w") as f:
        json.dump(account_freq, f, indent=2)
    print(f"Account frequency: {acct_freq_path}")

    # Save ad-level CSV
    output_path = os.path.join(args.output, "ads.csv")
    save_csv(rows, output_path)

    # Save daily frequency trends
    daily_path = os.path.join(args.output, "daily_frequency.json")
    with open(daily_path, "w") as f:
        json.dump(daily, f, indent=2)
    print(f"Daily frequency: {daily_path}")

    # Save metadata
    meta = {
        "account_id": account_id,
        "days": args.days,
        "start_date": start_date,
        "end_date": end_date,
        "total_ads": len(rows),
        "total_spend": total_spend,
        "total_purchases": total_purchases,
        "video_ads": video_count,
        "avg_frequency": round(avg_freq, 2),
        "ads_with_headlines": headline_count,
        "pulled_at": datetime.now().isoformat(),
    }
    meta_path = os.path.join(args.output, "pull_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"Metadata: {meta_path}")


if __name__ == "__main__":
    main()
