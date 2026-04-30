#!/usr/bin/env python3
"""
Distribution Audit — Meta Marketing API Data Extractor
Pulls account structure, performance metrics, daily trends, attribution windows,
ad identity, landing page data, and technical configuration from Meta's API.

Usage:
    python pull_distribution_data.py <ad_account_id>
    python pull_distribution_data.py act_123456789
    python pull_distribution_data.py act_123456789 --days 60

Outputs structured JSON files for AI analysis.
"""

import argparse
import json
import os
import sys
import time
import datetime
from typing import List, Dict, Any, Optional, Tuple
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

def _load_key(name):
    kf = os.path.join(os.path.expanduser("~"), ".claude", "api_keys.json")
    if os.path.exists(kf):
        with open(kf) as f:
            return json.load(f).get(name, "")
    return ""
META_ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", _load_key("meta_access_token"))
META_API_VERSION = os.environ.get("META_API_VERSION", "v21.0")
META_BASE_URL = f"https://graph.facebook.com/{META_API_VERSION}"


# ============================================================================
# API HELPERS
# ============================================================================

def _flush():
    """Force stdout flush for real-time progress in Cowork/piped contexts."""
    sys.stdout.flush()


def api_get(endpoint: str, params: dict, retries: int = 5) -> dict:
    """Make a GET request to the Meta API with retry logic."""
    url = f"{META_BASE_URL}/{endpoint}"
    params["access_token"] = META_ACCESS_TOKEN

    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=60)
            data = resp.json()

            if "error" in data:
                err = data["error"]
                code = err.get("code", 0)
                msg = err.get("message", "Unknown error")

                # Rate limit — wait and retry (codes: 4=app-level, 17=user-level, 32=page-level)
                if code in (4, 17, 32, 80004):
                    wait = min(60, 10 * (attempt + 1))
                    print(f"  ⏳ Rate limited (code {code}). Waiting {wait}s... (attempt {attempt+1}/{retries})")
                    _flush()
                    time.sleep(wait)
                    continue

                # Transient error — retry
                if code in (1, 2) and attempt < retries - 1:
                    print(f"  ⚠️ Transient error: {msg}. Retrying...")
                    _flush()
                    time.sleep(1)
                    continue

                print(f"  ❌ API Error ({code}): {msg}")
                _flush()
                return {"data": [], "error": msg}

            return data

        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                print(f"  ⏳ Request timeout. Retrying...")
                _flush()
                time.sleep(1)
                continue
            return {"data": [], "error": "Request timeout"}
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(0.5)
                continue
            return {"data": [], "error": str(e)}

    return {"data": [], "error": "Max retries exceeded"}


def paginate_all(endpoint: str, params: dict, max_pages: int = 20) -> List[dict]:
    """Fetch all pages of results from a paginated endpoint."""
    all_data = []

    for page in range(max_pages):
        data = api_get(endpoint, dict(params))  # copy params each time

        if "error" in data and not data.get("data"):
            break

        items = data.get("data", [])
        if not items:
            break

        all_data.extend(items)

        # Check for next page
        paging = data.get("paging", {})
        cursor = paging.get("cursors", {}).get("after")

        if not cursor:
            break

        params["after"] = cursor
        time.sleep(0.15)

    return all_data


# ============================================================================
# SECTION 1: ACCOUNT STRUCTURE
# ============================================================================

def fetch_account_info(account_id: str) -> dict:
    """Fetch ad account metadata."""
    print("📊 Fetching account info...")
    fields = "name,account_id,account_status,currency,timezone_name,timezone_offset_hours_utc,business_name,spend_cap,amount_spent,balance"
    data = api_get(account_id, {"fields": fields})
    return data


def fetch_campaigns(account_id: str) -> List[dict]:
    """Fetch ACTIVE campaigns with structural data."""
    print("📂 Fetching active campaigns...")
    fields = (
        "id,name,status,effective_status,objective,buying_type,"
        "bid_strategy,daily_budget,lifetime_budget,budget_remaining,"
        "special_ad_categories,smart_promotion_type,created_time,updated_time"
    )
    campaigns = paginate_all(
        f"{account_id}/campaigns",
        {
            "fields": fields,
            "effective_status": '["ACTIVE"]',
            "limit": 100
        },
        max_pages=5  # Safety: cap at 500 campaigns
    )
    print(f"  Found {len(campaigns)} active campaigns")
    _flush()
    return campaigns


def fetch_adsets_for_campaigns(account_id: str, campaign_ids: List[str]) -> List[dict]:
    """Fetch ad sets for specific campaigns (those with delivery).

    Broadened status filter: fetches ACTIVE, PAUSED, and CAMPAIGN_PAUSED ad sets
    because a paused ad set in an active campaign with recent delivery is still
    relevant for structural analysis (optimisation goal, targeting, attribution).
    """
    print(f"📋 Fetching ad sets for {len(campaign_ids)} campaigns with delivery...")
    _flush()
    fields = (
        "id,name,campaign_id,status,effective_status,"
        "optimization_goal,billing_event,bid_amount,bid_strategy,"
        "daily_budget,lifetime_budget,budget_remaining,"
        "targeting,promoted_object,attribution_spec,"
        "destination_type,existing_customer_budget_percentage,"
        "created_time,updated_time"
    )
    # Batch campaign IDs in groups of 50 to avoid filter-too-large errors
    all_adsets = []
    batch_size = 50
    for batch_start in range(0, len(campaign_ids), batch_size):
        batch = campaign_ids[batch_start:batch_start + batch_size]
        # Try with broadened status first (ACTIVE + PAUSED + CAMPAIGN_PAUSED)
        adsets = paginate_all(
            f"{account_id}/adsets",
            {
                "fields": fields,
                "effective_status": '["ACTIVE","PAUSED","CAMPAIGN_PAUSED"]',
                "filtering": json.dumps([{"field": "campaign.id", "operator": "IN", "value": batch}]),
                "limit": 200
            },
            max_pages=10
        )
        all_adsets.extend(adsets)
        if batch_start + batch_size < len(campaign_ids):
            time.sleep(1.0)

    # Fallback: if we got 0 results with campaign filtering, try without it
    if not all_adsets and campaign_ids:
        print("  ⚠️ Campaign-filtered fetch returned 0 ad sets. Trying unfiltered fallback...")
        _flush()
        all_adsets = paginate_all(
            f"{account_id}/adsets",
            {
                "fields": fields,
                "effective_status": '["ACTIVE","PAUSED","CAMPAIGN_PAUSED"]',
                "limit": 200
            },
            max_pages=10
        )
        # Filter client-side to delivery campaign IDs
        campaign_id_set = set(campaign_ids)
        all_adsets = [a for a in all_adsets if a.get("campaign_id") in campaign_id_set]

    print(f"  Found {len(all_adsets)} ad sets (in delivery campaigns)")
    _flush()
    return all_adsets


def fetch_ads_for_campaigns(account_id: str, campaign_ids: List[str]) -> List[dict]:
    """Fetch ads for specific campaigns (those with delivery).

    Broadened status filter to capture all ads in delivery campaigns.
    """
    print(f"🎨 Fetching ads for {len(campaign_ids)} campaigns with delivery...")
    _flush()
    fields = (
        "id,name,campaign_id,adset_id,status,effective_status,"
        "creative{id,name,title,body,object_story_spec,url_tags,effective_object_story_id,asset_feed_spec},"
        "tracking_specs,conversion_specs,created_time"
    )
    # Batch campaign IDs in groups of 20 (smaller than adsets because creative fields are large)
    all_ads = []
    batch_size = 20
    for batch_start in range(0, len(campaign_ids), batch_size):
        batch = campaign_ids[batch_start:batch_start + batch_size]
        batch_num = batch_start // batch_size + 1
        total_batches = (len(campaign_ids) + batch_size - 1) // batch_size
        print(f"  Ads batch {batch_num}/{total_batches} ({len(batch)} campaigns)...")
        _flush()
        ads = paginate_all(
            f"{account_id}/ads",
            {
                "fields": fields,
                "effective_status": '["ACTIVE","PAUSED","CAMPAIGN_PAUSED"]',
                "filtering": json.dumps([{"field": "campaign.id", "operator": "IN", "value": batch}]),
                "limit": 100
            },
            max_pages=10
        )
        all_ads.extend(ads)
        if batch_start + batch_size < len(campaign_ids):
            time.sleep(1.0)

    # Fallback if filtered fetch returned 0
    if not all_ads and campaign_ids:
        print("  ⚠️ Campaign-filtered fetch returned 0 ads. Trying unfiltered fallback...")
        _flush()
        all_ads = paginate_all(
            f"{account_id}/ads",
            {
                "fields": fields,
                "effective_status": '["ACTIVE","PAUSED","CAMPAIGN_PAUSED"]',
                "limit": 200
            },
            max_pages=10
        )
        campaign_id_set = set(campaign_ids)
        all_ads = [a for a in all_ads if a.get("campaign_id") in campaign_id_set]

    print(f"  Found {len(all_ads)} ads (in delivery campaigns)")
    _flush()
    return all_ads


# ============================================================================
# SECTION 2: PERFORMANCE METRICS
# ============================================================================

# Core fields we pull at every level
INSIGHTS_FIELDS = (
    "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,"
    "spend,impressions,reach,frequency,cpm,cpc,ctr,"
    "unique_clicks,unique_ctr,cost_per_unique_click,"
    "actions,action_values,cost_per_action_type,"
    "purchase_roas,conversions,cost_per_conversion,"
    "outbound_clicks,outbound_clicks_ctr,cost_per_outbound_click,"
    "unique_outbound_clicks,unique_outbound_clicks_ctr,cost_per_unique_outbound_click,"
    "website_purchase_roas"
)

# Attribution windows to compare
ATTRIBUTION_WINDOWS = [
    "7d_click",
    "7d_click_1d_view",
    "1d_view"
]


def fetch_campaign_insights(account_id: str, time_range: dict) -> List[dict]:
    """Fetch aggregate campaign-level metrics."""
    print(f"  📈 Campaign insights ({time_range['since']} → {time_range['until']})...")
    insights = paginate_all(
        f"{account_id}/insights",
        {
            "fields": INSIGHTS_FIELDS,
            "level": "campaign",
            "time_range": json.dumps(time_range),
            "limit": 500
        }
    )
    print(f"    Got {len(insights)} campaign rows")
    return insights


def fetch_adset_insights(account_id: str, time_range: dict, campaigns: List[dict] = None) -> List[dict]:
    """Fetch aggregate ad-set-level metrics. Batches by campaign to avoid data-too-large errors."""
    print(f"  📈 Ad set insights ({time_range['since']} → {time_range['until']})...")

    # If we have campaigns, fetch per-campaign to stay within API limits
    if campaigns:
        all_insights = []
        for i, c in enumerate(campaigns):
            cid = c.get("id")
            if i > 0:
                time.sleep(0.25)  # Light rate limit buffer
            rows = paginate_all(
                f"{account_id}/insights",
                {
                    "fields": INSIGHTS_FIELDS,
                    "level": "adset",
                    "time_range": json.dumps(time_range),
                    "filtering": json.dumps([{"field": "campaign.id", "operator": "IN", "value": [cid]}]),
                    "limit": 100
                },
                max_pages=5
            )
            all_insights.extend(rows)
        print(f"    Got {len(all_insights)} ad set rows (batched by {len(campaigns)} campaigns)")
        _flush()
        return all_insights

    # Fallback: single request with small page size
    insights = paginate_all(
        f"{account_id}/insights",
        {
            "fields": INSIGHTS_FIELDS,
            "level": "adset",
            "time_range": json.dumps(time_range),
            "limit": 50
        }
    )
    print(f"    Got {len(insights)} ad set rows")
    return insights


def fetch_ad_insights(account_id: str, time_range: dict, campaigns: List[dict] = None) -> List[dict]:
    """Fetch aggregate ad-level metrics. Batches by campaign to avoid data-too-large errors."""
    print(f"  📈 Ad insights ({time_range['since']} → {time_range['until']})...")

    # If we have campaigns, fetch per-campaign to stay within API limits
    if campaigns:
        all_insights = []
        for i, c in enumerate(campaigns):
            cid = c.get("id")
            if i > 0:
                time.sleep(0.25)  # Light rate limit buffer
            rows = paginate_all(
                f"{account_id}/insights",
                {
                    "fields": INSIGHTS_FIELDS,
                    "level": "ad",
                    "time_range": json.dumps(time_range),
                    "filtering": json.dumps([{"field": "campaign.id", "operator": "IN", "value": [cid]}]),
                    "limit": 100
                },
                max_pages=10
            )
            all_insights.extend(rows)
        print(f"    Got {len(all_insights)} ad rows (batched by {len(campaigns)} campaigns)")
        _flush()
        return all_insights

    # Fallback: single request with small page size
    insights = paginate_all(
        f"{account_id}/insights",
        {
            "fields": INSIGHTS_FIELDS,
            "level": "ad",
            "time_range": json.dumps(time_range),
            "limit": 50
        }
    )
    print(f"    Got {len(insights)} ad rows")
    return insights


# ============================================================================
# SECTION 3: DAILY TRENDS (30-DAY)
# ============================================================================

def fetch_daily_trends(account_id: str, time_range_30d: dict, campaigns: List[dict] = None) -> List[dict]:
    """Fetch daily metrics for 30-day trend analysis. Batches by campaign to avoid data limits."""
    print("📅 Fetching 30-day daily trends...")

    daily_fields = (
        "campaign_id,campaign_name,spend,impressions,reach,frequency,"
        "cpm,cpc,ctr,actions,action_values,cost_per_action_type,"
        "purchase_roas,unique_outbound_clicks,unique_outbound_clicks_ctr,"
        "cost_per_unique_outbound_click"
    )

    # Batch campaigns in groups of 10 for daily breakdown to avoid data-too-large errors
    if campaigns:
        all_trends = []
        batch_size = 10
        campaign_ids = [c.get("id") for c in campaigns]
        total_batches = (len(campaign_ids) + batch_size - 1) // batch_size
        for batch_start in range(0, len(campaign_ids), batch_size):
            batch = campaign_ids[batch_start:batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            print(f"  Daily trends batch {batch_num}/{total_batches}...")
            _flush()
            if batch_start > 0:
                time.sleep(0.3)
            rows = paginate_all(
                f"{account_id}/insights",
                {
                    "fields": daily_fields,
                    "level": "campaign",
                    "time_range": json.dumps(time_range_30d),
                    "time_increment": 1,
                    "filtering": json.dumps([{"field": "campaign.id", "operator": "IN", "value": batch}]),
                    "limit": 200
                },
                max_pages=10
            )
            all_trends.extend(rows)
        print(f"  Got {len(all_trends)} daily data points ({total_batches} batches)")
        return all_trends

    trends = paginate_all(
        f"{account_id}/insights",
        {
            "fields": daily_fields,
            "level": "campaign",
            "time_range": json.dumps(time_range_30d),
            "time_increment": 1,
            "limit": 100
        },
        max_pages=20
    )
    print(f"  Got {len(trends)} daily data points")
    return trends


def fetch_daily_account_trends(account_id: str, time_range_30d: dict) -> List[dict]:
    """Fetch daily account-level totals for overall trend."""
    print("📅 Fetching daily account totals...")

    daily_fields = (
        "spend,impressions,reach,frequency,cpm,cpc,ctr,"
        "actions,action_values,cost_per_action_type,purchase_roas"
    )

    trends = paginate_all(
        f"{account_id}/insights",
        {
            "fields": daily_fields,
            "level": "account",
            "time_range": json.dumps(time_range_30d),
            "time_increment": 1,
            "limit": 100
        }
    )
    print(f"  Got {len(trends)} account daily rows")
    return trends


# ============================================================================
# SECTION 4: ATTRIBUTION WINDOW COMPARISON
# ============================================================================

def fetch_attribution_comparison(account_id: str, time_range_30d: dict) -> dict:
    """
    Fetch performance under different attribution windows.
    Compares 7d_click vs 7d_click+1d_view vs 1d_view to inform optimal window.
    """
    print("🎯 Fetching attribution window comparison...")

    results = {}

    for window in ATTRIBUTION_WINDOWS:
        print(f"  📊 Window: {window}...")

        attr_fields = (
            "campaign_id,campaign_name,spend,impressions,reach,"
            "actions,action_values,cost_per_action_type,purchase_roas,conversions"
        )

        params = {
            "fields": attr_fields,
            "level": "campaign",
            "time_range": json.dumps(time_range_30d),
            "limit": 500
        }

        # Set the attribution window
        if window == "7d_click":
            params["action_attribution_windows"] = '["7d_click"]'
        elif window == "7d_click_1d_view":
            params["action_attribution_windows"] = '["7d_click","1d_view"]'
        elif window == "1d_view":
            params["action_attribution_windows"] = '["1d_view"]'

        data = paginate_all(f"{account_id}/insights", params)
        results[window] = data
        print(f"    Got {len(data)} rows")
        time.sleep(0.5)

    return results


# ============================================================================
# SECTION 5: LANDING PAGE EXTRACTION
# ============================================================================

def extract_landing_pages(ads: List[dict], ad_insights: List[dict]) -> Tuple[List[dict], List[dict]]:
    """
    Extract landing page URLs from ad creatives and match with performance data.
    """
    print("🔗 Extracting landing page URLs...")

    # Build insights lookup by ad_id
    insights_by_ad = {}
    for row in ad_insights:
        ad_id = row.get("ad_id")
        if ad_id:
            insights_by_ad[ad_id] = row

    lp_data = []
    lp_aggregated = {}  # Group by URL

    for ad in ads:
        ad_id = ad.get("id")
        creative = ad.get("creative", {})

        # Extract URL from object_story_spec
        url = None
        oss = creative.get("object_story_spec", {})

        # Check link_data (most common for link ads)
        link_data = oss.get("link_data", {})
        if link_data:
            url = link_data.get("link")
            # Also check call_to_action for the URL
            cta = link_data.get("call_to_action", {})
            if not url and cta:
                url = cta.get("value", {}).get("link")

        # Check video_data
        video_data = oss.get("video_data", {})
        if not url and video_data:
            cta = video_data.get("call_to_action", {})
            if cta:
                url = cta.get("value", {}).get("link")

        # Check asset_feed_spec for dynamic creative
        afs = creative.get("asset_feed_spec", {})
        if not url and afs:
            link_urls = afs.get("link_urls", [])
            if link_urls:
                url = link_urls[0].get("website_url")

        # Extract URL tags
        url_tags = creative.get("url_tags", "")

        # Get performance data for this ad
        perf = insights_by_ad.get(ad_id, {})

        entry = {
            "ad_id": ad_id,
            "ad_name": ad.get("name", ""),
            "campaign_id": ad.get("campaign_id", ""),
            "landing_page_url": url or "Unknown",
            "url_tags": url_tags,
            "spend": float(perf.get("spend", 0)),
            "impressions": int(perf.get("impressions", 0)),
            "reach": int(perf.get("reach", 0)),
            "cpm": float(perf.get("cpm", 0)),
            "unique_outbound_ctr": float(perf.get("unique_outbound_clicks_ctr", [{}])[0].get("value", 0)) if isinstance(perf.get("unique_outbound_clicks_ctr"), list) else float(perf.get("unique_outbound_clicks_ctr", 0)),
            "purchase_roas": _extract_roas(perf),
            "purchases": _extract_action_count(perf, "omni_purchase"),
            "cost_per_purchase": _extract_cost_per_action(perf, "omni_purchase"),
        }
        lp_data.append(entry)

        # Aggregate by URL
        if url:
            base_url = url.split("?")[0]  # Strip query params for grouping
            if base_url not in lp_aggregated:
                lp_aggregated[base_url] = {
                    "url": url,
                    "base_url": base_url,
                    "ad_count": 0,
                    "total_spend": 0.0,
                    "total_impressions": 0,
                    "total_reach": 0,
                    "total_purchases": 0,
                    "ad_ids": []
                }
            agg = lp_aggregated[base_url]
            agg["ad_count"] += 1
            agg["total_spend"] += entry["spend"]
            agg["total_impressions"] += entry["impressions"]
            agg["total_reach"] += entry["reach"]
            agg["total_purchases"] += entry["purchases"]
            agg["ad_ids"].append(ad_id)

    # Calculate derived metrics for aggregated LPs
    for url, agg in lp_aggregated.items():
        if agg["total_impressions"] > 0:
            agg["blended_cpm"] = (agg["total_spend"] / agg["total_impressions"]) * 1000
        if agg["total_purchases"] > 0:
            agg["cost_per_purchase"] = agg["total_spend"] / agg["total_purchases"]
        if agg["total_spend"] > 0:
            agg["spend_share_pct"] = 0  # Will be calculated later

    # Calculate spend share
    total_spend = sum(a["total_spend"] for a in lp_aggregated.values())
    if total_spend > 0:
        for agg in lp_aggregated.values():
            agg["spend_share_pct"] = round((agg["total_spend"] / total_spend) * 100, 2)

    print(f"  Extracted {len(lp_data)} ad→LP mappings across {len(lp_aggregated)} unique URLs")

    return lp_data, list(lp_aggregated.values())


# ============================================================================
# SECTION 6: AD IDENTITY ANALYSIS (EXPANDED 5-TYPE TAXONOMY)
# ============================================================================

def fetch_page_names(page_ids: List[str]) -> Dict[str, dict]:
    """Fetch Facebook Page names and metadata for identity classification."""
    print(f"🆔 Fetching page names for {len(page_ids)} unique pages...")
    _flush()
    page_info = {}
    for pid in page_ids:
        if not pid:
            continue
        data = api_get(pid, {"fields": "name,category,fan_count,is_published,username"})
        if "error" not in data:
            page_info[pid] = {
                "name": data.get("name", ""),
                "category": data.get("category", ""),
                "fan_count": data.get("fan_count", 0),
                "is_published": data.get("is_published", True),
                "username": data.get("username", ""),
            }
        else:
            page_info[pid] = {"name": f"Page {pid}", "category": "", "fan_count": 0, "is_published": True, "username": ""}
        time.sleep(0.1)
    print(f"  Retrieved names for {len(page_info)} pages")
    _flush()
    return page_info


def fetch_instagram_actor_names(actor_ids: List[str]) -> Dict[str, dict]:
    """Fetch Instagram actor names for identity classification."""
    print(f"🆔 Fetching Instagram actor names for {len(actor_ids)} unique actors...")
    _flush()
    actor_info = {}
    for aid in actor_ids:
        if not aid:
            continue
        data = api_get(aid, {"fields": "name,username,profile_picture_uri"})
        if "error" not in data:
            actor_info[aid] = {
                "name": data.get("name", ""),
                "username": data.get("username", ""),
            }
        else:
            actor_info[aid] = {"name": f"Actor {aid}", "username": ""}
        time.sleep(0.1)
    print(f"  Retrieved names for {len(actor_info)} Instagram actors")
    _flush()
    return actor_info


def extract_ad_identities(ads: List[dict], page_info: Dict[str, dict], actor_info: Dict[str, dict]) -> Tuple[List[dict], dict]:
    """
    Analyse which identity each ad runs under.
    Classifies into 5 types: brand_page, founder, customer_persona, third_party_positioning, creator_partnership.
    Includes page/actor names for AI-level classification refinement.
    """
    print("🆔 Classifying ad identities (5-type taxonomy)...")

    identities = []
    page_ids_seen = {}

    for ad in ads:
        creative = ad.get("creative", {})
        oss = creative.get("object_story_spec", {})

        # The page_id in object_story_spec tells us which Page identity the ad uses
        page_id = oss.get("page_id", "")

        # effective_object_story_id format: "{page_id}_{post_id}"
        effective_story = creative.get("effective_object_story_id", "")
        story_page_id = effective_story.split("_")[0] if effective_story else ""

        # instagram_actor_id tells us the Instagram identity
        instagram_actor = oss.get("instagram_actor_id", "")

        identity_page = page_id or story_page_id

        if identity_page:
            page_ids_seen.setdefault(identity_page, []).append(ad.get("id"))

        # Get the page/actor name for this ad
        page_name = page_info.get(identity_page, {}).get("name", "") if identity_page else ""
        page_category = page_info.get(identity_page, {}).get("category", "") if identity_page else ""
        actor_name = actor_info.get(instagram_actor, {}).get("name", "") if instagram_actor else ""
        actor_username = actor_info.get(instagram_actor, {}).get("username", "") if instagram_actor else ""

        identities.append({
            "ad_id": ad.get("id"),
            "ad_name": ad.get("name", ""),
            "campaign_id": ad.get("campaign_id", ""),
            "adset_id": ad.get("adset_id", ""),
            "page_id": identity_page,
            "page_name": page_name,
            "page_category": page_category,
            "instagram_actor_id": instagram_actor,
            "instagram_actor_name": actor_name,
            "instagram_actor_username": actor_username,
            "effective_object_story_id": effective_story,
        })

    # Determine which page is the "primary" brand page (most ads)
    primary_page = max(page_ids_seen.items(), key=lambda x: len(x[1]))[0] if page_ids_seen else None
    primary_page_name = page_info.get(primary_page, {}).get("name", "") if primary_page else ""

    # Initial classification: brand_page vs non-brand
    # The AI analysis step will refine non-brand into the 4 sub-types
    for entry in identities:
        pid = entry["page_id"]
        if not pid:
            entry["identity_type"] = "unknown"
        elif pid == primary_page:
            entry["identity_type"] = "brand_page"
        else:
            # Non-brand page — provide raw data for AI to classify further
            entry["identity_type"] = "non_brand"

    # Build unique page inventory with names (for AI classification)
    page_inventory = []
    for pid, ad_ids in page_ids_seen.items():
        pinfo = page_info.get(pid, {})
        page_inventory.append({
            "page_id": pid,
            "page_name": pinfo.get("name", ""),
            "page_category": pinfo.get("category", ""),
            "fan_count": pinfo.get("fan_count", 0),
            "username": pinfo.get("username", ""),
            "is_primary": pid == primary_page,
            "ad_count": len(ad_ids),
        })

    # Unique Instagram actors
    unique_actors = {}
    for entry in identities:
        aid = entry["instagram_actor_id"]
        if aid and aid not in unique_actors:
            ainfo = actor_info.get(aid, {})
            unique_actors[aid] = {
                "actor_id": aid,
                "name": ainfo.get("name", ""),
                "username": ainfo.get("username", ""),
            }

    # Summary
    identity_summary = {
        "primary_brand_page_id": primary_page,
        "primary_brand_page_name": primary_page_name,
        "total_ads_analysed": len(identities),
        "brand_page_ads": sum(1 for i in identities if i["identity_type"] == "brand_page"),
        "non_brand_ads": sum(1 for i in identities if i["identity_type"] == "non_brand"),
        "unknown_ads": sum(1 for i in identities if i["identity_type"] == "unknown"),
        "page_inventory": page_inventory,
        "unique_instagram_actors": list(unique_actors.values()),
        "identity_type_taxonomy": [
            "brand_page: Primary brand Facebook/Instagram page",
            "founder: Founder or key person's page (origin story, personal brand)",
            "customer_persona: Brand-owned pages targeting specific audience segments",
            "third_party_positioning: Review sites, niche authorities, advertorial publishers",
            "creator_partnership: Creator/influencer pages via Meta Partnership Ads"
        ],
        "classification_note": "Initial classification is brand_page vs non_brand. The AI analysis step should refine non_brand entries into founder, customer_persona, third_party_positioning, or creator_partnership based on page names, categories, and context."
    }

    print(f"  Brand page ads: {identity_summary['brand_page_ads']}, "
          f"Non-brand: {identity_summary['non_brand_ads']}, "
          f"Unknown: {identity_summary['unknown_ads']}")
    print(f"  Unique pages: {len(page_inventory)}, "
          f"Unique Instagram actors: {len(unique_actors)}")

    return identities, identity_summary


def aggregate_identity_performance(ad_identities: List[dict], ad_insights: List[dict]) -> List[dict]:
    """Aggregate performance metrics by identity (page_id).

    Groups ad-level insights by their page_id to show spend, ROAS, CPP etc per identity.
    """
    print("📊 Aggregating performance by identity...")

    # Build insights lookup by ad_id
    insights_by_ad = {}
    for row in ad_insights:
        ad_id = row.get("ad_id")
        if ad_id:
            insights_by_ad[ad_id] = row

    # Group by page_id
    by_page = {}
    for identity in ad_identities:
        pid = identity.get("page_id", "unknown")
        if not pid:
            pid = "unknown"
        if pid not in by_page:
            by_page[pid] = {
                "page_id": pid,
                "page_name": identity.get("page_name", ""),
                "identity_type": identity.get("identity_type", "unknown"),
                "ad_count": 0,
                "total_spend": 0.0,
                "total_impressions": 0,
                "total_reach": 0,
                "total_purchases": 0,
                "total_revenue": 0.0,
                "total_atc": 0,
            }
        entry = by_page[pid]
        entry["ad_count"] += 1

        perf = insights_by_ad.get(identity["ad_id"], {})
        entry["total_spend"] += float(perf.get("spend", 0))
        entry["total_impressions"] += int(perf.get("impressions", 0))
        entry["total_reach"] += int(perf.get("reach", 0))
        entry["total_purchases"] += _extract_action_count(perf, "omni_purchase")
        entry["total_revenue"] += _extract_action_value(perf, "omni_purchase")
        entry["total_atc"] += _extract_action_count(perf, "omni_add_to_cart")

    # Calculate derived metrics
    total_spend_all = sum(p["total_spend"] for p in by_page.values())
    result = []
    for pid, data in by_page.items():
        spend = data["total_spend"]
        data["spend_share_pct"] = round((spend / total_spend_all * 100) if total_spend_all else 0, 2)
        data["cpm"] = round((spend / data["total_impressions"] * 1000) if data["total_impressions"] else 0, 2)
        data["frequency"] = round((data["total_impressions"] / data["total_reach"]) if data["total_reach"] else 0, 2)
        data["cost_per_purchase"] = round((spend / data["total_purchases"]) if data["total_purchases"] else 0, 2)
        data["roas"] = round((data["total_revenue"] / spend) if spend else 0, 2)
        result.append(data)

    # Sort by spend descending
    result.sort(key=lambda x: x["total_spend"], reverse=True)
    print(f"  Aggregated performance for {len(result)} unique identities")
    return result


# ============================================================================
# SECTION 7: MARKET-LEVEL AGGREGATION (from ad set geo targeting)
# ============================================================================

def extract_market_data(adsets: List[dict], adset_insights: List[dict]) -> List[dict]:
    """Extract market/geo data from ad set targeting and aggregate performance by market."""
    print("🌍 Extracting market-level data from ad set targeting...")

    # Build insights lookup by adset_id
    insights_by_adset = {}
    for row in adset_insights:
        adset_id = row.get("adset_id")
        if adset_id:
            insights_by_adset[adset_id] = row

    # Extract geo targeting from each adset
    by_market = {}
    adsets_without_geo = 0

    for adset in adsets:
        adset_id = adset.get("id", "")
        targeting = adset.get("targeting", {})
        geo_locations = targeting.get("geo_locations", {})

        # Extract countries
        countries = geo_locations.get("countries", [])
        # Extract regions/cities if present
        regions = geo_locations.get("regions", [])
        cities = geo_locations.get("cities", [])

        # Build a market key from geo targeting
        if countries:
            market_key = ",".join(sorted(countries))
        elif regions:
            market_key = ",".join(sorted(r.get("key", "") for r in regions))
        elif cities:
            market_key = ",".join(sorted(c.get("key", "") for c in cities))
        else:
            market_key = "No Geo / Broad"
            adsets_without_geo += 1

        if market_key not in by_market:
            by_market[market_key] = {
                "market": market_key,
                "countries": countries if countries else [],
                "adset_count": 0,
                "campaign_ids": set(),
                "total_spend": 0.0,
                "total_impressions": 0,
                "total_reach": 0,
                "total_purchases": 0,
                "total_revenue": 0.0,
            }

        entry = by_market[market_key]
        entry["adset_count"] += 1
        entry["campaign_ids"].add(adset.get("campaign_id", ""))

        perf = insights_by_adset.get(adset_id, {})
        entry["total_spend"] += float(perf.get("spend", 0))
        entry["total_impressions"] += int(perf.get("impressions", 0))
        entry["total_reach"] += int(perf.get("reach", 0))
        entry["total_purchases"] += _extract_action_count(perf, "omni_purchase")
        entry["total_revenue"] += _extract_action_value(perf, "omni_purchase")

    # Calculate derived metrics
    total_spend_all = sum(m["total_spend"] for m in by_market.values())
    result = []
    for key, data in by_market.items():
        spend = data["total_spend"]
        data["campaign_ids"] = list(data["campaign_ids"])  # Convert set to list for JSON
        data["campaign_count"] = len(data["campaign_ids"])
        data["spend_share_pct"] = round((spend / total_spend_all * 100) if total_spend_all else 0, 2)
        data["cpm"] = round((spend / data["total_impressions"] * 1000) if data["total_impressions"] else 0, 2)
        data["frequency"] = round((data["total_impressions"] / data["total_reach"]) if data["total_reach"] else 0, 2)
        data["cost_per_purchase"] = round((spend / data["total_purchases"]) if data["total_purchases"] else 0, 2)
        data["roas"] = round((data["total_revenue"] / spend) if spend else 0, 2)
        result.append(data)

    result.sort(key=lambda x: x["total_spend"], reverse=True)
    print(f"  Found {len(result)} distinct markets ({adsets_without_geo} ad sets without geo targeting)")
    return result


# ============================================================================
# SECTION 8: OPTIMISATION OBJECTIVE ANALYSIS
# ============================================================================

def analyse_optimisation_objectives(adsets: List[dict], adset_insights: List[dict]) -> dict:
    """Analyse optimisation objectives across ad sets and calculate spend per objective."""
    print("🎯 Analysing optimisation objectives at ad set level...")

    # Build insights lookup by adset_id
    insights_by_adset = {}
    for row in adset_insights:
        adset_id = row.get("adset_id")
        if adset_id:
            insights_by_adset[adset_id] = row

    by_objective = {}
    for adset in adsets:
        adset_id = adset.get("id", "")
        opt_goal = adset.get("optimization_goal", "UNKNOWN")
        campaign_id = adset.get("campaign_id", "")

        if opt_goal not in by_objective:
            by_objective[opt_goal] = {
                "optimization_goal": opt_goal,
                "adset_count": 0,
                "campaign_ids": set(),
                "adset_details": [],
                "total_spend": 0.0,
                "total_impressions": 0,
                "total_purchases": 0,
                "total_revenue": 0.0,
            }

        entry = by_objective[opt_goal]
        entry["adset_count"] += 1
        entry["campaign_ids"].add(campaign_id)

        perf = insights_by_adset.get(adset_id, {})
        spend = float(perf.get("spend", 0))
        entry["total_spend"] += spend
        entry["total_impressions"] += int(perf.get("impressions", 0))
        entry["total_purchases"] += _extract_action_count(perf, "omni_purchase")
        entry["total_revenue"] += _extract_action_value(perf, "omni_purchase")

        entry["adset_details"].append({
            "adset_id": adset_id,
            "adset_name": adset.get("name", ""),
            "campaign_id": campaign_id,
            "optimization_goal": opt_goal,
            "spend": spend,
        })

    # Calculate derived metrics
    total_spend_all = sum(o["total_spend"] for o in by_objective.values())
    result = []
    for goal, data in by_objective.items():
        spend = data["total_spend"]
        data["campaign_ids"] = list(data["campaign_ids"])
        data["spend_share_pct"] = round((spend / total_spend_all * 100) if total_spend_all else 0, 2)
        data["cost_per_purchase"] = round((spend / data["total_purchases"]) if data["total_purchases"] else 0, 2)
        data["roas"] = round((data["total_revenue"] / spend) if spend else 0, 2)
        result.append(data)

    result.sort(key=lambda x: x["total_spend"], reverse=True)

    # Flag non-purchase objectives
    non_purchase_spend = sum(o["total_spend"] for o in result if o["optimization_goal"] not in ("OFFSITE_CONVERSIONS", "VALUE", "PURCHASE"))
    non_purchase_pct = round((non_purchase_spend / total_spend_all * 100) if total_spend_all else 0, 1)

    summary = {
        "objectives": result,
        "total_spend": round(total_spend_all, 2),
        "non_purchase_spend": round(non_purchase_spend, 2),
        "non_purchase_pct": non_purchase_pct,
        "assessment_note": "Per Soar Ad Account Structure Framework: Purchase optimisation should be primary for small brands (<£100k/mo). Mid-funnel (ATC/VC) only justified at £100-500k/mo+. Non-conversion objectives (LINK_CLICKS, POST_ENGAGEMENT, REACH) require justification."
    }

    print(f"  Found {len(result)} distinct optimisation objectives")
    if non_purchase_spend > 0:
        print(f"  ⚠️ {non_purchase_pct}% of spend ({total_spend_all:.0f} currency) on non-purchase objectives")
    return summary


# ============================================================================
# SECTION 9b: AUDIENCE SEGMENTS (New / Engaged / Existing)
# ============================================================================

def fetch_audience_segments(account_id: str, date_range: dict) -> dict:
    """Fetch audience segment breakdown (New / Engaged / Existing customers).

    Uses the user_persona_id and user_persona_name breakdowns which correspond
    to Meta's Audience Segments feature. This requires the advertiser to have
    configured their Engaged Audience and Existing Customer definitions in
    Ads Manager → Account Settings → Audience Segments.

    If not configured, data will return with zero values.
    """
    print("👥 Fetching audience segment breakdowns (New/Engaged/Existing)...")
    _flush()

    # Fetch campaign-level with user_persona_name breakdown
    params = {
        "fields": "campaign_id,campaign_name,spend,impressions,reach,actions,action_values,purchase_roas",
        "time_range": json.dumps(date_range),
        "breakdowns": "user_persona_name",
        "level": "campaign",
        "limit": 500,
    }
    data = paginate_all(f"{account_id}/insights", params, max_pages=5)

    # Process results
    segments = []
    has_data = False
    for row in data:
        spend = float(row.get("spend", 0))
        persona = row.get("user_persona_name", "Unknown")
        if spend > 0:
            has_data = True
        segments.append({
            "campaign_id": row.get("campaign_id", ""),
            "campaign_name": row.get("campaign_name", ""),
            "audience_segment": persona,
            "spend": spend,
            "impressions": int(row.get("impressions", 0)),
            "reach": int(row.get("reach", 0)),
            "purchases": _extract_action_count(row, "omni_purchase"),
            "purchase_value": _extract_action_value(row, "omni_purchase"),
            "roas": _extract_roas(row),
        })

    # Aggregate by segment type
    segment_totals = {}
    for s in segments:
        seg = s["audience_segment"]
        if seg not in segment_totals:
            segment_totals[seg] = {"spend": 0, "impressions": 0, "reach": 0, "purchases": 0, "purchase_value": 0}
        segment_totals[seg]["spend"] += s["spend"]
        segment_totals[seg]["impressions"] += s["impressions"]
        segment_totals[seg]["reach"] += s["reach"]
        segment_totals[seg]["purchases"] += s["purchases"]
        segment_totals[seg]["purchase_value"] += s["purchase_value"]

    result = {
        "has_audience_segments_configured": has_data,
        "note": (
            "Audience segments are active and returning data."
            if has_data
            else "Audience Segments not configured. The advertiser must define "
                 "Engaged Audience and Existing Customer definitions in Ads Manager "
                 "→ Account Settings → Audience Segments for this data to populate. "
                 "Flag for manual verification."
        ),
        "segment_totals": {
            k: {sk: round(sv, 2) if isinstance(sv, float) else sv for sk, sv in v.items()}
            for k, v in segment_totals.items()
        },
        "by_campaign": segments,
    }

    if has_data:
        print(f"  ✅ Audience segments configured — found {len(segment_totals)} segments")
    else:
        print("  ⚠️  Audience Segments not configured (all zero values). Flag for manual setup.")
    _flush()
    return result


# ============================================================================
# SECTION 9: NON-CONVERSION CAMPAIGN FLAGGING
# ============================================================================

def flag_non_conversion_campaigns(campaigns: List[dict], campaign_insights: List[dict]) -> dict:
    """Identify and flag campaigns with non-conversion objectives and calculate their spend."""
    print("🚩 Flagging non-conversion objective campaigns...")

    # Build insights lookup
    insights_by_campaign = {}
    for row in campaign_insights:
        cid = row.get("campaign_id")
        if cid:
            insights_by_campaign[cid] = row

    conversion_objectives = {
        "OUTCOME_SALES", "CONVERSIONS", "PRODUCT_CATALOG_SALES",
        "OUTCOME_APP_PROMOTION", "APP_INSTALLS"
    }

    non_conversion = []
    boosted_posts = []
    total_non_conv_spend = 0.0
    total_boosted_spend = 0.0

    for c in campaigns:
        objective = c.get("objective", "")
        spt = c.get("smart_promotion_type", "")
        cid = c.get("id", "")
        perf = insights_by_campaign.get(cid, {})
        spend = float(perf.get("spend", 0))

        # Check for boosted posts
        if spt in ("GUIDED_CREATION", "SMART_PROMOTION") or objective in ("POST_ENGAGEMENT", "LINK_CLICKS"):
            if spt in ("GUIDED_CREATION", "SMART_PROMOTION"):
                boosted_posts.append({
                    "campaign_id": cid,
                    "campaign_name": c.get("name", ""),
                    "objective": objective,
                    "smart_promotion_type": spt,
                    "spend": spend,
                })
                total_boosted_spend += spend

        # Check for non-conversion objectives
        if objective and objective not in conversion_objectives:
            non_conversion.append({
                "campaign_id": cid,
                "campaign_name": c.get("name", ""),
                "objective": objective,
                "smart_promotion_type": spt,
                "spend": spend,
            })
            total_non_conv_spend += spend

    total_spend = sum(float(insights_by_campaign.get(c.get("id"), {}).get("spend", 0)) for c in campaigns)

    summary = {
        "non_conversion_campaigns": non_conversion,
        "non_conversion_count": len(non_conversion),
        "non_conversion_spend": round(total_non_conv_spend, 2),
        "non_conversion_spend_pct": round((total_non_conv_spend / total_spend * 100) if total_spend else 0, 1),
        "boosted_posts": boosted_posts,
        "boosted_post_count": len(boosted_posts),
        "boosted_post_spend": round(total_boosted_spend, 2),
    }

    if non_conversion:
        print(f"  Found {len(non_conversion)} non-conversion campaigns ({summary['non_conversion_spend_pct']}% of spend)")
    if boosted_posts:
        print(f"  Found {len(boosted_posts)} boosted posts")
    return summary


# ============================================================================
# HELPER: ACTION EXTRACTION
# ============================================================================

def _extract_action_count(row: dict, action_type: str) -> int:
    """Extract a specific action count from insights row."""
    for action in row.get("actions", []):
        if action.get("action_type") == action_type:
            return int(action.get("value", 0))
    # Try alternate action types
    alt_types = {
        "omni_purchase": ["purchase", "offsite_conversion.fb_pixel_purchase"],
        "omni_add_to_cart": ["add_to_cart", "offsite_conversion.fb_pixel_add_to_cart"],
        "omni_initiated_checkout": ["initiate_checkout", "offsite_conversion.fb_pixel_initiate_checkout"],
    }
    for alt in alt_types.get(action_type, []):
        for action in row.get("actions", []):
            if action.get("action_type") == alt:
                return int(action.get("value", 0))
    return 0


def _extract_cost_per_action(row: dict, action_type: str) -> float:
    """Extract cost per specific action."""
    for cpa in row.get("cost_per_action_type", []):
        if cpa.get("action_type") == action_type:
            return float(cpa.get("value", 0))
    alt_types = {
        "omni_purchase": ["purchase", "offsite_conversion.fb_pixel_purchase"],
        "omni_add_to_cart": ["add_to_cart", "offsite_conversion.fb_pixel_add_to_cart"],
        "omni_initiated_checkout": ["initiate_checkout", "offsite_conversion.fb_pixel_initiate_checkout"],
    }
    for alt in alt_types.get(action_type, []):
        for cpa in row.get("cost_per_action_type", []):
            if cpa.get("action_type") == alt:
                return float(cpa.get("value", 0))
    return 0.0


def _extract_roas(row: dict) -> float:
    """Extract ROAS value."""
    roas = row.get("purchase_roas") or row.get("website_purchase_roas")
    if isinstance(roas, list) and roas:
        return float(roas[0].get("value", 0))
    if isinstance(roas, (int, float)):
        return float(roas)
    return 0.0


def _extract_action_value(row: dict, action_type: str) -> float:
    """Extract revenue/value for a specific action."""
    for av in row.get("action_values", []):
        if av.get("action_type") == action_type:
            return float(av.get("value", 0))
    alt_types = {
        "omni_purchase": ["purchase", "offsite_conversion.fb_pixel_purchase"],
    }
    for alt in alt_types.get(action_type, []):
        for av in row.get("action_values", []):
            if av.get("action_type") == alt:
                return float(av.get("value", 0))
    return 0.0


# ============================================================================
# ACTIVITY LOG (CHANGE LOG)
# ============================================================================

def fetch_activity_log(account_id: str, date_range: dict) -> dict:
    """
    Fetch the account activity log (change history) from the Meta Marketing API.
    Returns a pre-computed summary with daily breakdowns, category counts,
    day-of-week distribution, and raw events for deeper analysis.
    """
    from datetime import datetime as dt_cls
    from collections import defaultdict

    print(f"📋 Fetching account activity log ({date_range['since']} → {date_range['until']})...")
    _flush()

    # Convert dates to unix timestamps for the activities endpoint
    since_ts = int(dt_cls.strptime(date_range["since"], "%Y-%m-%d").timestamp())
    until_ts = int(dt_cls.strptime(date_range["until"], "%Y-%m-%d").timestamp()) + 86400  # include end day

    all_activities = []
    url = f"{META_BASE_URL}/{account_id}/activities"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "limit": 500,
        "since": since_ts,
        "until": until_ts,
    }

    page = 0
    while url:
        page += 1
        try:
            if page == 1:
                resp = requests.get(url, params=params, timeout=60)
            else:
                resp = requests.get(url, timeout=60)

            data = resp.json()

            if "error" in data:
                err = data["error"]
                print(f"  ⚠️ Activity log API error: {err.get('message', 'Unknown')}")
                _flush()
                break

            activities = data.get("data", [])
            all_activities.extend(activities)

            paging = data.get("paging", {})
            url = paging.get("next")

            if page % 5 == 0:
                print(f"  Fetched {len(all_activities)} activities so far (page {page})...")
                _flush()

        except Exception as e:
            print(f"  ⚠️ Activity log fetch error: {e}")
            _flush()
            break

    print(f"  ✅ Retrieved {len(all_activities)} total activities")
    _flush()

    if not all_activities:
        return {
            "total_activities": 0,
            "active_days": 0,
            "total_calendar_days": 0,
            "avg_changes_per_active_day": 0,
            "event_type_breakdown": {},
            "category_breakdown": {},
            "daily_activity": [],
            "day_of_week_distribution": {},
            "raw_events": [],
            "note": "No activity log data returned. The API token may lack the required permissions.",
        }

    # ── Parse and aggregate ──
    def parse_ts(ts_val):
        if isinstance(ts_val, (int, float)):
            return dt_cls.fromtimestamp(ts_val)
        try:
            return dt_cls.strptime(ts_val, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
        except Exception:
            try:
                return dt_cls.fromtimestamp(int(ts_val))
            except Exception:
                return None

    # Category mapping
    CATEGORIES = {
        "Ad Status Changes (on/off)": [
            "update_ad_run_status", "update_ad_set_run_status",
            "update_campaign_run_status", "update_ad_run_status_to_be_set_after_review",
        ],
        "Budget Adjustments": [
            "update_ad_set_budget", "update_campaign_budget",
            "update_campaign_budget_scheduling_state",
        ],
        "Creative Changes": ["edit_images", "add_images"],
        "New Ads/Sets/Campaigns": ["create_ad", "create_ad_set", "create_campaign_group"],
        "Targeting Changes": ["update_ad_set_target_spec"],
        "Bid/Optimisation Changes": [
            "update_ad_set_bid_strategy", "update_ad_set_optimization_goal",
        ],
        "Naming/Admin": ["update_ad_friendly_name"],
        "System Events": ["first_delivery_event", "ad_account_billing_charge"],
    }

    # Invert for lookup
    event_to_category = {}
    for cat, events in CATEGORIES.items():
        for evt in events:
            event_to_category[evt] = cat

    daily_changes = defaultdict(lambda: defaultdict(int))
    daily_total = defaultdict(int)
    event_type_counts = defaultdict(int)
    category_counts = defaultdict(int)
    dow_counts = defaultdict(int)

    for a in all_activities:
        ts = a.get("event_time")
        event_type = a.get("event_type", "unknown")
        event_type_counts[event_type] += 1
        cat = event_to_category.get(event_type, "Other")
        category_counts[cat] += 1

        if ts:
            parsed = parse_ts(ts)
            if parsed:
                day = parsed.strftime("%Y-%m-%d")
                daily_changes[day][event_type] += 1
                daily_total[day] += 1
                dow = parsed.strftime("%A")
                dow_counts[dow] += 1

    # Build daily activity summary
    sorted_days = sorted(daily_total.keys())
    daily_activity = []
    for day in sorted_days:
        changes = daily_total[day]
        day_events = dict(daily_changes[day])

        status_changes = sum(
            day_events.get(e, 0)
            for e in CATEGORIES["Ad Status Changes (on/off)"]
        )
        budget_changes = sum(
            day_events.get(e, 0)
            for e in CATEGORIES["Budget Adjustments"]
        )
        creative_changes = sum(
            day_events.get(e, 0)
            for e in CATEGORIES["Creative Changes"]
        )
        new_entities = sum(
            day_events.get(e, 0)
            for e in CATEGORIES["New Ads/Sets/Campaigns"]
        )
        targeting_changes = sum(
            day_events.get(e, 0)
            for e in CATEGORIES["Targeting Changes"]
        )

        daily_activity.append({
            "date": day,
            "total_changes": changes,
            "status_changes": status_changes,
            "budget_changes": budget_changes,
            "creative_changes": creative_changes,
            "new_entities": new_entities,
            "targeting_changes": targeting_changes,
            "event_detail": day_events,
        })

    total_activities = len(all_activities)
    active_days = len([d for d in sorted_days if daily_total[d] > 0])
    total_calendar_days = (
        (dt_cls.strptime(date_range["until"], "%Y-%m-%d") -
         dt_cls.strptime(date_range["since"], "%Y-%m-%d")).days + 1
    )

    # Identify gaps (consecutive days with no changes)
    gaps = []
    if sorted_days:
        all_dates = []
        start = dt_cls.strptime(date_range["since"], "%Y-%m-%d")
        end = dt_cls.strptime(date_range["until"], "%Y-%m-%d")
        current = start
        while current <= end:
            all_dates.append(current.strftime("%Y-%m-%d"))
            current += datetime.timedelta(days=1)

        gap_start = None
        for d in all_dates:
            if daily_total.get(d, 0) == 0:
                if gap_start is None:
                    gap_start = d
            else:
                if gap_start is not None:
                    gap_length = (dt_cls.strptime(d, "%Y-%m-%d") -
                                  dt_cls.strptime(gap_start, "%Y-%m-%d")).days
                    if gap_length >= 3:  # Only flag gaps of 3+ days
                        gaps.append({
                            "start": gap_start,
                            "end": (dt_cls.strptime(d, "%Y-%m-%d") -
                                    datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                            "days": gap_length,
                        })
                    gap_start = None

    # Day of week in order
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_distribution = {d: dow_counts.get(d, 0) for d in dow_order}

    print(f"  📊 {active_days} active days out of {total_calendar_days} calendar days")
    if gaps:
        longest_gap = max(gaps, key=lambda g: g["days"])
        print(f"  ⚠️ Longest management gap: {longest_gap['days']} days ({longest_gap['start']} → {longest_gap['end']})")
    _flush()

    return {
        "total_activities": total_activities,
        "active_days": active_days,
        "total_calendar_days": total_calendar_days,
        "avg_changes_per_active_day": round(total_activities / active_days, 1) if active_days else 0,
        "event_type_breakdown": dict(event_type_counts),
        "category_breakdown": dict(category_counts),
        "daily_activity": daily_activity,
        "day_of_week_distribution": dow_distribution,
        "management_gaps": gaps,
        "raw_events": all_activities,
        "note": (
            "Activity log pulled from Meta Marketing API. Only event_type and event_time are "
            "reliably returned — object IDs, names, and old/new values depend on token permissions. "
            "Pair daily_activity with daily_account_trends.json for performance correlation."
        ),
    }


# ============================================================================
# COMPUTE DERIVED METRICS
# ============================================================================

def compute_account_summary(
    account_info: dict,
    campaigns_with_delivery: List[dict],
    all_campaigns: List[dict],
    adsets: List[dict],
    ads: List[dict],
    campaign_insights_30d: List[dict],
    campaign_insights_90d: List[dict]
) -> dict:
    """Build the account structure summary anchored on campaigns with delivery."""

    # Use campaigns_with_delivery as the primary dataset
    active_adsets = [a for a in adsets if a.get("effective_status") == "ACTIVE"]
    active_ads = [a for a in ads if a.get("effective_status") == "ACTIVE"]

    # Classify campaigns (delivery campaigns only)
    # ──────────────────────────────────────────────────────────────────────
    # IMPORTANT: Meta deprecated AUTOMATED_SHOPPING_ADS in 2025.
    # All new Sales campaigns now return smart_promotion_type=GUIDED_CREATION.
    # The old "ASC" concept has been replaced by "Advantage+ Sales" which is
    # now the DEFAULT for all conversion campaigns.
    #
    # Detection strategy (multi-signal, backwards-compatible):
    #   1. Legacy: smart_promotion_type == AUTOMATED_SHOPPING_ADS (pre-2025)
    #   2. Modern: OUTCOME_SALES + GUIDED_CREATION + campaign-level budget +
    #      Advantage+ audience enabled on ad sets = Advantage+ Sales (new ASC)
    #   3. Fallback: budget structure (campaign budget = CBO, ad set budget = ABO)
    # ──────────────────────────────────────────────────────────────────────

    # Pre-compute which campaigns have Advantage+ audience at ad set level
    campaigns_with_advantage_audience = set()
    for a in adsets:
        targeting = a.get("targeting", {})
        ta = targeting.get("targeting_automation", {})
        if ta.get("advantage_audience") == 1:
            campaigns_with_advantage_audience.add(a.get("campaign_id", ""))

    # Pre-compute which campaigns have VALUE optimisation (catalogue/DPA signal)
    campaigns_with_value_opt = set()
    for a in adsets:
        if a.get("optimization_goal") == "VALUE":
            campaigns_with_value_opt.add(a.get("campaign_id", ""))

    asc_campaigns = []  # Advantage+ Sales / legacy ASC
    catalogue_campaigns = []  # DPA / Catalogue campaigns
    abo_campaigns = []
    cbo_campaigns = []

    # Catalogue/DPA name patterns (case-insensitive)
    catalogue_patterns = ["catalogue", "catalog", "dpa", "dynamic product"]

    for c in campaigns_with_delivery:
        cid = c.get("id", "")
        spt = c.get("smart_promotion_type", "")
        objective = c.get("objective", "")
        name_lower = c.get("name", "").lower()
        has_campaign_budget = bool(c.get("daily_budget") or c.get("lifetime_budget"))
        has_advantage_audience = cid in campaigns_with_advantage_audience
        has_value_opt = cid in campaigns_with_value_opt
        is_catalogue = (
            any(p in name_lower for p in catalogue_patterns)
            or has_value_opt
        )

        # Signal 1: Legacy ASC detection (pre-2025 campaigns)
        if spt == "AUTOMATED_SHOPPING_ADS":
            asc_campaigns.append(c)

        # Signal 2: Catalogue / DPA campaign (separate from standard ASC)
        elif is_catalogue:
            catalogue_campaigns.append(c)

        # Signal 3: Modern Advantage+ Sales detection
        # OUTCOME_SALES + GUIDED_CREATION + campaign-level budget + Advantage+ audience
        elif (objective == "OUTCOME_SALES"
              and spt == "GUIDED_CREATION"
              and has_campaign_budget
              and has_advantage_audience):
            asc_campaigns.append(c)

        # Signal 4: Regular CBO (has campaign budget but doesn't qualify as ASC)
        elif has_campaign_budget:
            cbo_campaigns.append(c)

        # Signal 5: ABO (budget at ad set level)
        else:
            abo_campaigns.append(c)

    # Spend distribution by campaign (30d) — only delivery campaigns
    total_spend_30d = sum(float(i.get("spend", 0)) for i in campaign_insights_30d)
    campaign_spend = []
    for insight in campaign_insights_30d:
        spend = float(insight.get("spend", 0))
        if spend <= 0:
            continue  # Skip zero-spend campaigns from the performance view
        campaign_spend.append({
            "campaign_id": insight.get("campaign_id"),
            "campaign_name": insight.get("campaign_name"),
            "spend": spend,
            "spend_pct": round((spend / total_spend_30d * 100) if total_spend_30d else 0, 2),
            "impressions": int(insight.get("impressions", 0)),
            "reach": int(insight.get("reach", 0)),
            "frequency": float(insight.get("frequency", 0)),
            "cpm": float(insight.get("cpm", 0)),
            "purchase_roas": _extract_roas(insight),
            "purchases": _extract_action_count(insight, "omni_purchase"),
            "cost_per_purchase": _extract_cost_per_action(insight, "omni_purchase"),
            "add_to_carts": _extract_action_count(insight, "omni_add_to_cart"),
            "cost_per_atc": _extract_cost_per_action(insight, "omni_add_to_cart"),
            "initiated_checkouts": _extract_action_count(insight, "omni_initiated_checkout"),
            "cost_per_ic": _extract_cost_per_action(insight, "omni_initiated_checkout"),
            "unique_outbound_ctr": float(insight.get("unique_outbound_clicks_ctr", [{}])[0].get("value", 0)) if isinstance(insight.get("unique_outbound_clicks_ctr"), list) else float(insight.get("unique_outbound_clicks_ctr", 0)),
            "unique_outbound_cpc": float(insight.get("cost_per_unique_outbound_click", [{}])[0].get("value", 0)) if isinstance(insight.get("cost_per_unique_outbound_click"), list) else float(insight.get("cost_per_unique_outbound_click", 0)),
        })

    # Sort by spend descending
    campaign_spend.sort(key=lambda x: x["spend"], reverse=True)

    # Cross-reference campaign type with spend
    # Use the classified campaign lists for consistent typing
    asc_ids = {c.get("id") for c in asc_campaigns}
    catalogue_ids = {c.get("id") for c in catalogue_campaigns}
    cbo_ids = {c.get("id") for c in cbo_campaigns}
    abo_ids = {c.get("id") for c in abo_campaigns}

    for cs in campaign_spend:
        cid = cs["campaign_id"]
        if cid in asc_ids:
            cs["campaign_type"] = "ASC"
        elif cid in catalogue_ids:
            cs["campaign_type"] = "Catalogue"
        elif cid in cbo_ids:
            cs["campaign_type"] = "CBO"
        elif cid in abo_ids:
            cs["campaign_type"] = "ABO"
        else:
            cs["campaign_type"] = "Unknown"
        for c in campaigns_with_delivery:
            if c.get("id") == cid:
                cs["objective"] = c.get("objective", "")
                cs["bid_strategy"] = c.get("bid_strategy", "")
                cs["smart_promotion_type"] = c.get("smart_promotion_type", "")
                cs["has_advantage_audience"] = cid in campaigns_with_advantage_audience
                break

    # Testing vs Scaling vs Catalogue spend
    testing_spend = sum(cs["spend"] for cs in campaign_spend if cs.get("campaign_type") == "ABO")
    scaling_spend = sum(cs["spend"] for cs in campaign_spend if cs.get("campaign_type") in ("ASC", "CBO"))
    catalogue_spend = sum(cs["spend"] for cs in campaign_spend if cs.get("campaign_type") == "Catalogue")

    # 90-day reach and frequency
    total_reach_90d = sum(int(i.get("reach", 0)) for i in campaign_insights_90d)
    total_impressions_90d = sum(int(i.get("impressions", 0)) for i in campaign_insights_90d)
    total_spend_90d = sum(float(i.get("spend", 0)) for i in campaign_insights_90d)
    blended_frequency_90d = (total_impressions_90d / total_reach_90d) if total_reach_90d else 0
    blended_cpm_90d = (total_spend_90d / total_impressions_90d * 1000) if total_impressions_90d else 0

    # Existing customer budget caps from ad sets
    existing_customer_caps = []
    for a in adsets:
        cap = a.get("existing_customer_budget_percentage")
        if cap is not None:
            existing_customer_caps.append({
                "adset_id": a.get("id"),
                "adset_name": a.get("name"),
                "campaign_id": a.get("campaign_id"),
                "existing_customer_budget_pct": cap
            })

    # ── EXCLUSION DETECTION ──
    # Extract excluded_custom_audiences from ad set targeting
    exclusion_summary = []
    adsets_with_exclusions = 0
    adsets_without_exclusions = 0
    all_excluded_audiences = {}  # Deduplicated map of audience_id -> name

    for a in adsets:
        targeting = a.get("targeting", {})
        excluded_cas = targeting.get("excluded_custom_audiences", [])
        adset_id = a.get("id", "")
        adset_name = a.get("name", "")
        campaign_id = a.get("campaign_id", "")

        if excluded_cas:
            adsets_with_exclusions += 1
            excl_names = []
            for ca in excluded_cas:
                ca_id = ca.get("id", "")
                ca_name = ca.get("name", "Unknown")
                all_excluded_audiences[ca_id] = ca_name
                excl_names.append({"id": ca_id, "name": ca_name})
            exclusion_summary.append({
                "adset_id": adset_id,
                "adset_name": adset_name,
                "campaign_id": campaign_id,
                "exclusion_count": len(excluded_cas),
                "excluded_audiences": excl_names,
            })
        else:
            adsets_without_exclusions += 1
            exclusion_summary.append({
                "adset_id": adset_id,
                "adset_name": adset_name,
                "campaign_id": campaign_id,
                "exclusion_count": 0,
                "excluded_audiences": [],
            })

    # Attribution specs from ad sets
    attribution_specs = {}
    for a in adsets:
        attr = a.get("attribution_spec", [])
        key = json.dumps(attr, sort_keys=True) if attr else "none"
        if key not in attribution_specs:
            attribution_specs[key] = {"spec": attr, "count": 0, "adset_ids": []}
        attribution_specs[key]["count"] += 1
        attribution_specs[key]["adset_ids"].append(a.get("id"))

    # Brand size classification based on monthly Meta spend
    monthly_spend = total_spend_30d  # Use 30d as proxy for monthly
    if monthly_spend < 100000:
        brand_size = "Small"
        brand_size_description = "Under £100k/mo Meta spend"
    elif monthly_spend < 500000:
        brand_size = "Mid-Market"
        brand_size_description = "£100k-500k/mo Meta spend"
    else:
        brand_size = "Large"
        brand_size_description = "Over £500k/mo Meta spend"

    # Dormant campaign count
    dormant_count = len(all_campaigns) - len(campaigns_with_delivery)

    return {
        "account": {
            "name": account_info.get("name", ""),
            "id": account_info.get("account_id", ""),
            "currency": account_info.get("currency", ""),
            "timezone": account_info.get("timezone_name", ""),
            "status": account_info.get("account_status", ""),
        },
        "brand_size": {
            "tier": brand_size,
            "description": brand_size_description,
            "monthly_meta_spend": round(monthly_spend, 2),
            "benchmarks": {
                "Small": {"ASC_Core": "70-90%", "ABO_Testing": "10-30%", "Mid_Funnel": "None", "Upper_Funnel": "None"},
                "Mid-Market": {"ASC_Core": "60-75%", "ABO_Testing": "10-25%", "Mid_Funnel": "10-20%", "Upper_Funnel": "None"},
                "Large": {"ASC_Core": "40-60%", "ABO_Testing": "5-20%", "Mid_Funnel": "15-25%", "Upper_Funnel": "5-15%"},
            }
        },
        "structure": {
            "campaigns_with_delivery": len(campaigns_with_delivery),
            "dormant_active_campaigns": dormant_count,
            "total_adsets": len(adsets),
            "active_adsets": len(active_adsets),
            "total_ads": len(ads),
            "active_ads": len(active_ads),
            "asc_campaigns": len(asc_campaigns),
            "catalogue_campaigns": len(catalogue_campaigns),
            "abo_campaigns": len(abo_campaigns),
            "cbo_campaigns": len(cbo_campaigns),
            "campaign_types_breakdown": {
                "ASC": [c.get("id") for c in asc_campaigns],
                "Catalogue": [c.get("id") for c in catalogue_campaigns],
                "ABO": [c.get("id") for c in abo_campaigns],
                "CBO": [c.get("id") for c in cbo_campaigns],
            },
            "asc_detection_note": (
                "ASC detection uses multi-signal approach: legacy AUTOMATED_SHOPPING_ADS "
                "OR (OUTCOME_SALES + GUIDED_CREATION + campaign-level budget + Advantage+ audience). "
                "Catalogue/DPA campaigns detected via naming patterns and VALUE optimisation goal."
            ),
            "structure_note": f"Analysis based on {len(campaigns_with_delivery)} campaigns with delivery in the last 90 days. {dormant_count} additional active campaigns had no delivery and should be reviewed for archival."
        },
        "spend_distribution_30d": {
            "total_spend": round(total_spend_30d, 2),
            "testing_spend_abo": round(testing_spend, 2),
            "scaling_spend_asc_cbo": round(scaling_spend, 2),
            "catalogue_spend": round(catalogue_spend, 2),
            "testing_pct": round((testing_spend / total_spend_30d * 100) if total_spend_30d else 0, 1),
            "scaling_pct": round((scaling_spend / total_spend_30d * 100) if total_spend_30d else 0, 1),
            "catalogue_pct": round((catalogue_spend / total_spend_30d * 100) if total_spend_30d else 0, 1),
            "by_campaign": campaign_spend,
        },
        "reach_health_90d": {
            "total_reach": total_reach_90d,
            "total_impressions": total_impressions_90d,
            "blended_frequency": round(blended_frequency_90d, 2),
            "blended_cpm": round(blended_cpm_90d, 2),
            "cpMr": round(blended_cpm_90d * blended_frequency_90d, 2),
            "total_spend": round(total_spend_90d, 2),
        },
        "existing_customer_caps": existing_customer_caps,
        "exclusions": {
            "adsets_with_exclusions": adsets_with_exclusions,
            "adsets_without_exclusions": adsets_without_exclusions,
            "total_adsets": len(adsets),
            "exclusion_coverage_pct": round(
                (adsets_with_exclusions / len(adsets) * 100) if adsets else 0, 1
            ),
            "unique_excluded_audiences": [
                {"id": aid, "name": aname}
                for aid, aname in all_excluded_audiences.items()
            ],
            "per_adset": exclusion_summary,
        },
        "attribution_specs": list(attribution_specs.values()),
    }


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Distribution Audit — Meta API Data Extractor")
    parser.add_argument("ad_account_id", help="Meta Ad Account ID (e.g. act_123456789)")
    parser.add_argument("--output-dir", default=".", help="Directory for output JSON files")
    parser.add_argument("--days", type=int, default=30, help="Performance analysis window in days (default: 30)")
    args = parser.parse_args()

    account_id = args.ad_account_id
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Configurable date ranges
    TODAY = datetime.date.today()
    PERF_DAYS = args.days
    LOOKBACK_DAYS = 90  # Always 90 days for delivery filter and reach health
    PERF_START = TODAY - datetime.timedelta(days=PERF_DAYS)
    LOOKBACK_START = TODAY - datetime.timedelta(days=LOOKBACK_DAYS)

    DATE_PERF = {"since": PERF_START.isoformat(), "until": TODAY.isoformat()}
    DATE_LOOKBACK = {"since": LOOKBACK_START.isoformat(), "until": TODAY.isoformat()}

    print(f"\n{'='*60}")
    print(f"🌐 DISTRIBUTION AUDIT — META API DATA EXTRACTION")
    print(f"{'='*60}")
    print(f"Account: {account_id}")
    print(f"Performance window: {PERF_START} → {TODAY} ({PERF_DAYS}d)")
    print(f"Lookback window: {LOOKBACK_START} → {TODAY} ({LOOKBACK_DAYS}d)")
    print(f"Output: {output_dir}")
    print(f"{'='*60}\n")
    _flush()

    # ── 1. Account Structure ─────────────────────────────────
    print("\n── PHASE 1: ACCOUNT STRUCTURE ──")
    _flush()
    account_info = fetch_account_info(account_id)

    # Early exit if we don't have permission
    if "error" in account_info and not account_info.get("name"):
        err_msg = account_info.get("error", "Unknown error")
        print(f"\n❌ CANNOT ACCESS ACCOUNT: {err_msg}")
        print("Please check that:")
        print("  1. The ad account ID is correct (format: act_123456789)")
        print("  2. The Meta API token has ads_read permission for this account")
        print("  3. The token has not expired")
        _flush()
        return 1

    # Fetch ALL active campaigns for structural overview
    all_campaigns = fetch_campaigns(account_id)
    print(f"\n  Total active campaigns: {len(all_campaigns)}")
    _flush()

    # ── 1b. DELIVERY FILTER ──────────────────────────────────
    print("\n── PHASE 1b: IDENTIFYING CAMPAIGNS WITH DELIVERY (90d) ──")
    _flush()
    campaign_insights_90d = fetch_campaign_insights(account_id, DATE_LOOKBACK)

    # Extract campaign IDs that had any spend in the last 90 days
    all_campaign_ids_with_spend = set()
    for insight in campaign_insights_90d:
        spend = float(insight.get("spend", 0))
        if spend > 0:
            all_campaign_ids_with_spend.add(insight.get("campaign_id"))

    # Filter to only ACTIVE campaigns with delivery
    active_campaign_ids = {c.get("id") for c in all_campaigns}
    delivery_campaign_ids = all_campaign_ids_with_spend & active_campaign_ids
    campaigns_with_delivery = [c for c in all_campaigns if c.get("id") in delivery_campaign_ids]

    paused_with_delivery = all_campaign_ids_with_spend - active_campaign_ids

    print(f"  🎯 {len(campaigns_with_delivery)} of {len(all_campaigns)} active campaigns had delivery in last 90 days")
    if paused_with_delivery:
        print(f"  ℹ️  {len(paused_with_delivery)} additional paused/archived campaigns had delivery in 90d")
    print(f"  ⏭️  Skipping {len(all_campaigns) - len(campaigns_with_delivery)} dormant active campaigns")
    _flush()

    # Fetch adsets and ads for campaigns with delivery
    adsets = fetch_adsets_for_campaigns(account_id, list(delivery_campaign_ids))
    ads = fetch_ads_for_campaigns(account_id, list(delivery_campaign_ids))

    # ── 2. Performance Metrics ───────────────────────────────
    print(f"\n── PHASE 2: PERFORMANCE METRICS ({PERF_DAYS}-day) ──")
    _flush()
    campaign_insights_perf = fetch_campaign_insights(account_id, DATE_PERF)
    adset_insights_perf = fetch_adset_insights(account_id, DATE_PERF, campaigns=campaigns_with_delivery)
    ad_insights_perf = fetch_ad_insights(account_id, DATE_PERF, campaigns=campaigns_with_delivery)

    # ── 3. Daily Trends ──────────────────────────────────────
    print(f"\n── PHASE 3: DAILY TRENDS ({PERF_DAYS}-day) ──")
    _flush()
    daily_campaign_trends = fetch_daily_trends(account_id, DATE_PERF, campaigns=campaigns_with_delivery)
    daily_account_trends = fetch_daily_account_trends(account_id, DATE_PERF)

    # ── 4. Attribution Comparison ────────────────────────────
    print("\n── PHASE 4: ATTRIBUTION WINDOW COMPARISON ──")
    _flush()
    attribution_data = fetch_attribution_comparison(account_id, DATE_PERF)

    # ── 5. Landing Pages ─────────────────────────────────────
    print("\n── PHASE 5: LANDING PAGE EXTRACTION ──")
    _flush()
    lp_by_ad, lp_aggregated = extract_landing_pages(ads, ad_insights_perf)

    # ── 6. Ad Identity (5-type taxonomy) ─────────────────────
    print("\n── PHASE 6: AD IDENTITY ANALYSIS ──")
    _flush()
    # Fetch page and actor names for classification
    unique_page_ids = set()
    unique_actor_ids = set()
    for ad in ads:
        creative = ad.get("creative", {})
        oss = creative.get("object_story_spec", {})
        pid = oss.get("page_id", "")
        effective_story = creative.get("effective_object_story_id", "")
        story_pid = effective_story.split("_")[0] if effective_story else ""
        if pid:
            unique_page_ids.add(pid)
        if story_pid:
            unique_page_ids.add(story_pid)
        actor = oss.get("instagram_actor_id", "")
        if actor:
            unique_actor_ids.add(actor)

    page_info = fetch_page_names(list(unique_page_ids))
    actor_info = fetch_instagram_actor_names(list(unique_actor_ids))

    ad_identities, identity_summary = extract_ad_identities(ads, page_info, actor_info)

    # ── 6b. Identity Performance ─────────────────────────────
    print("\n── PHASE 6b: IDENTITY PERFORMANCE ──")
    _flush()
    identity_performance = aggregate_identity_performance(ad_identities, ad_insights_perf)

    # ── 7. Market-Level Analysis ─────────────────────────────
    print("\n── PHASE 7: MARKET-LEVEL ANALYSIS ──")
    _flush()
    market_data = extract_market_data(adsets, adset_insights_perf)

    # ── 8. Optimisation Objective Analysis ────────────────────
    print("\n── PHASE 8: OPTIMISATION OBJECTIVES ──")
    _flush()
    optimisation_analysis = analyse_optimisation_objectives(adsets, adset_insights_perf)

    # ── 9. Non-Conversion Campaign Flagging ──────────────────
    print("\n── PHASE 9: NON-CONVERSION CAMPAIGNS ──")
    _flush()
    non_conversion_flags = flag_non_conversion_campaigns(campaigns_with_delivery, campaign_insights_perf)

    # ── 9b. Audience Segments (New / Engaged / Existing) ─────
    print("\n── PHASE 9b: AUDIENCE SEGMENTS (New/Engaged/Existing) ──")
    _flush()
    audience_segments = fetch_audience_segments(account_id, DATE_PERF)

    # ── 10. Activity / Change Log ────────────────────────────
    print("\n── PHASE 10: ACCOUNT ACTIVITY LOG (Change Log) ──")
    _flush()
    activity_log = fetch_activity_log(account_id, DATE_PERF)

    # ── 10b. Compute Summary ─────────────────────────────────
    print("\n── PHASE 10b: COMPUTING SUMMARY ──")
    _flush()
    account_summary = compute_account_summary(
        account_info, campaigns_with_delivery, all_campaigns, adsets, ads,
        campaign_insights_perf, campaign_insights_90d
    )

    # Add delivery filter metadata
    account_summary["delivery_filter"] = {
        "total_active_campaigns": len(all_campaigns),
        "campaigns_with_delivery_90d": len(campaigns_with_delivery),
        "dormant_active_campaigns": len(all_campaigns) - len(campaigns_with_delivery),
        "paused_campaigns_with_delivery_90d": len(paused_with_delivery),
    }

    # Add config metadata
    account_summary["config"] = {
        "performance_window_days": PERF_DAYS,
        "lookback_window_days": LOOKBACK_DAYS,
        "performance_date_range": DATE_PERF,
        "lookback_date_range": DATE_LOOKBACK,
        "extraction_date": TODAY.isoformat(),
    }

    # ── OUTPUT ───────────────────────────────────────────────
    print("\n── SAVING OUTPUT FILES ──")
    _flush()

    outputs = {
        "account_summary.json": account_summary,
        "campaigns_with_delivery.json": campaigns_with_delivery,
        "adsets_raw.json": adsets,
        "ads_raw.json": ads,
        "campaign_insights_perf.json": campaign_insights_perf,
        "adset_insights_perf.json": adset_insights_perf,
        "ad_insights_perf.json": ad_insights_perf,
        "campaign_insights_90d.json": campaign_insights_90d,
        "daily_campaign_trends.json": daily_campaign_trends,
        "daily_account_trends.json": daily_account_trends,
        "attribution_comparison.json": attribution_data,
        "landing_pages_by_ad.json": lp_by_ad,
        "landing_pages_aggregated.json": lp_aggregated,
        "ad_identities.json": ad_identities,
        "identity_summary.json": identity_summary,
        "identity_performance.json": identity_performance,
        "market_data.json": market_data,
        "optimisation_analysis.json": optimisation_analysis,
        "non_conversion_flags.json": non_conversion_flags,
        "audience_segments.json": audience_segments,
        "activity_log.json": activity_log,
    }

    for filename, data in outputs.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"  ✅ {filename}")
        _flush()

    # Print quick summary
    print(f"\n{'='*60}")
    print("✅ DATA EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Account: {account_summary['account']['name']} ({account_summary['account']['id']})")
    print(f"  Brand Size: {account_summary['brand_size']['tier']} ({account_summary['brand_size']['description']})")
    print(f"  With Delivery (90d): {len(campaigns_with_delivery)} campaigns, "
          f"{len(adsets)} ad sets, {len(ads)} ads")
    print(f"  Dormant (no delivery): {len(all_campaigns) - len(campaigns_with_delivery)} campaigns (recommend archival)")
    print(f"  {PERF_DAYS}d Spend: {account_summary['account']['currency']} "
          f"{account_summary['spend_distribution_30d']['total_spend']:,.2f}")
    print(f"  Testing (ABO): {account_summary['spend_distribution_30d']['testing_pct']}% | "
          f"Scaling (ASC/CBO): {account_summary['spend_distribution_30d']['scaling_pct']}%")
    print(f"  90d Blended Freq: {account_summary['reach_health_90d']['blended_frequency']}")
    print(f"  90d CPMr: {account_summary['reach_health_90d']['cpMr']}")
    print(f"  Identity: {identity_summary['brand_page_ads']} brand, "
          f"{identity_summary['non_brand_ads']} non-brand")
    print(f"  Landing Pages: {len(lp_aggregated)} unique URLs")
    print(f"  Markets: {len(market_data)} distinct geos")
    if optimisation_analysis['non_purchase_pct'] > 0:
        print(f"  ⚠️ Non-purchase optimisation: {optimisation_analysis['non_purchase_pct']}% of spend")
    if non_conversion_flags['non_conversion_count'] > 0:
        print(f"  ⚠️ Non-conversion campaigns: {non_conversion_flags['non_conversion_count']} ({non_conversion_flags['non_conversion_spend_pct']}% of spend)")
    print(f"  Activity Log: {activity_log['total_activities']} changes over {activity_log['active_days']} active days")
    print(f"  Files saved to: {output_dir}/")
    print(f"{'='*60}\n")
    _flush()

    return 0


if __name__ == "__main__":
    sys.exit(main())
