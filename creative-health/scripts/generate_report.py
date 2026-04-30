#!/usr/bin/env python3
"""
Creative Health — Report Generator v2
Parses naming conventions, scores dimensions, generates HTML report with
interpretation placeholders for Claude to fill.
"""

import argparse
import csv
import json
import math
import os
from collections import defaultdict
from datetime import datetime

# ============================================================
# NORMALISATION MAPS
# ============================================================

ANGLE_ALIASES = {
    "social proof": "Social Proof", "social-proof": "Social Proof",
    "limited-offer-product-drop": "Limited Offer", "limited offer / product drop": "Limited Offer",
    "limited offer _ product drop": "Limited Offer", "limited offer": "Limited Offer",
    "deep-pain-point": "Deep Pain Point", "deep pain point": "Deep Pain Point",
    "superiority": "Superiority",
    "lifestyle-integration": "Lifestyle Integration", "lifestyle integration": "Lifestyle Integration",
    "lifestyle~integration": "Lifestyle Integration",
    "location-based": "Location Based", "location based": "Location Based",
    "founders-story": "Founders Story", "founders story": "Founders Story",
    "brand-story": "Brand Story", "brand story": "Brand Story",
    "humour": "Humour", "humor": "Humour",
    "street~interview": "Street Interview", "street interview": "Street Interview",
    "asmr": "ASMR", "day-specific": "Day Specific", "day specific": "Day Specific",
    "voice over narrative": "Voice Over", "native format": "Native Format",
    "testimonial": "Testimonial",
}

FUNNEL_ALIASES = {
    "problem aware": "TOF", "problem-aware": "TOF", "problem~aware": "TOF",
    "solution aware": "MOF", "solution-aware": "MOF", "solution~aware": "MOF",
    "product aware": "BOF", "product-aware": "BOF", "product~aware": "BOF",
}

KNOWN_MEDIA_TYPES = {"static", "video", "ugc", "carousel", "editonly"}

FUNNEL_COLORS = {"TOF": "#3b82f6", "MOF": "#f59e0b", "BOF": "#10b981", "Unknown": "#94a3b8"}
ANGLE_COLORS = {
    "Social Proof": "#8b5cf6", "Limited Offer": "#f43f5e", "Deep Pain Point": "#ef4444",
    "Superiority": "#3b82f6", "Lifestyle Integration": "#10b981", "Location Based": "#06b6d4",
    "Founders Story": "#f59e0b", "Brand Story": "#d97706", "Humour": "#ec4899",
    "Street Interview": "#6366f1", "ASMR": "#14b8a6", "Voice Over": "#a855f7",
    "Day Specific": "#64748b", "Native Format": "#78716c", "Testimonial": "#0ea5e9",
    "Unknown": "#94a3b8",
}
MEDIA_COLORS = {"Static": "#3b82f6", "Video": "#8b5cf6", "UGC": "#10b981", "Carousel": "#f59e0b", "Unknown": "#94a3b8"}


# ============================================================
# DATA LOADING
# ============================================================

def safe_float(val, default=0.0):
    try:
        return float(val) if val else default
    except (ValueError, TypeError):
        return default


def load_csv(path):
    ads = []
    with open(path, "r") as f:
        for row in csv.DictReader(f):
            ad = {
                "name": row.get("ad_name", ""), "ad_id": row.get("ad_id", ""),
                "campaign": row.get("campaign_name", ""), "adset": row.get("adset_name", ""),
                "spend": safe_float(row.get("spend")), "impressions": safe_float(row.get("impressions")),
                "clicks": safe_float(row.get("clicks")), "ctr": safe_float(row.get("ctr")),
                "cpc": safe_float(row.get("cpc")), "cpm": safe_float(row.get("cpm")),
                "purchases": safe_float(row.get("purchases")),
                "purchase_value": safe_float(row.get("purchase_value")),
                "roas": safe_float(row.get("roas")),
                "video_3sec": safe_float(row.get("video_3sec")),
                "thruplay": safe_float(row.get("thruplay")),
                "video_p25": safe_float(row.get("video_p25")),
                "video_p50": safe_float(row.get("video_p50")),
                "video_p75": safe_float(row.get("video_p75")),
                "video_p100": safe_float(row.get("video_p100")),
                "video_duration": safe_float(row.get("video_duration_sec")),
                "reach": safe_float(row.get("reach")),
                "frequency": safe_float(row.get("frequency")),
                "headline": row.get("headline", ""),
                "primary_text": row.get("primary_text", ""),
            }
            if ad["spend"] > 0:
                ads.append(ad)
    return ads


def load_daily_frequency(path):
    """Load daily frequency JSON if it exists."""
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def load_account_frequency(path):
    """Load account-level period frequency JSON."""
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def load_gemini_analysis(path):
    """Load Gemini deep mode analysis JSON if it exists."""
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


# ============================================================
# NAMING CONVENTION PARSER
# ============================================================

def parse_ad_name(name):
    result = {
        "source": "unknown", "concept_id": "", "funnel": "Unknown",
        "angle": "Unknown", "painpoint": "", "mediatype": "Unknown",
        "product": "Unknown", "identity": "", "parseable": False,
    }
    if name.startswith("LWUBTR"):
        result["source"] = "lwu"
        parts = name.split("_")
        if len(parts) < 4:
            return result
        result["concept_id"] = parts[0]
        funnel_raw = parts[1].strip().lower()
        if funnel_raw in ("v1", "v2", "v3"):
            return result
        result["funnel"] = FUNNEL_ALIASES.get(funnel_raw, "Unknown")
        media_idx = -1
        for i in range(2, min(len(parts), 7)):
            val = parts[i].strip().lower().replace("-", "").replace("~", "")
            if val in KNOWN_MEDIA_TYPES:
                media_idx = i
                break
        if media_idx == -1:
            if len(parts) > 2:
                angle_raw = parts[2].strip().lower().replace("~", " ")
                result["angle"] = ANGLE_ALIASES.get(angle_raw, angle_raw.replace("-", " ").title())
            return result
        media_raw = parts[media_idx].strip().lower().replace("-", "").replace("~", "")
        result["mediatype"] = "UGC" if media_raw == "ugc" else media_raw.title()
        angle_raw = parts[2].strip().lower().replace("~", " ")
        result["angle"] = ANGLE_ALIASES.get(angle_raw, angle_raw.replace("-", " ").title())
        if media_idx > 3:
            result["painpoint"] = parts[3].strip().replace("-", " ").replace("~", " ")
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        if media_idx + 1 < len(parts):
            prod = parts[media_idx + 1].strip().replace("-", " ").replace("~", " ")
            if not any(m in prod.upper() for m in months) and len(prod) > 1:
                result["product"] = prod.title()
        full_upper = name.upper()
        if "THELONDONEREDIT" in full_upper or "LONDONER" in full_upper:
            result["identity"] = "The Londoner Edit"
        elif "WEEKENDFAMILYEATS" in full_upper:
            result["identity"] = "Weekend Family Eats"
        elif "ASPIRATIONAL" in full_upper:
            result["identity"] = "Aspirational"
        result["parseable"] = result["funnel"] != "Unknown" and result["angle"] != "Unknown"
    elif name.startswith("ID_") or name.startswith("img_") or name.startswith("vid_"):
        result["source"] = "inherited"
        if "img" in name[:6].lower():
            result["mediatype"] = "Static"
        elif "vid" in name[:6].lower():
            result["mediatype"] = "Video"
    elif name.startswith("V1_") or name.startswith("V2_") or name.startswith("V3_"):
        result["source"] = "lwu_legacy"
        for p in name.split("_"):
            p_lower = p.strip().lower()
            if p_lower in KNOWN_MEDIA_TYPES:
                result["mediatype"] = "UGC" if p_lower == "ugc" else p_lower.title()
            fm = FUNNEL_ALIASES.get(p_lower)
            if fm: result["funnel"] = fm
            am = ANGLE_ALIASES.get(p_lower)
            if am: result["angle"] = am
    return result


# ============================================================
# ANALYSIS ENGINE
# ============================================================

def calculate_hhi(spend_shares):
    return sum(s * s for s in spend_shares)


def hhi_rating(hhi):
    if hhi < 1500: return "diverse", "#10b981"
    if hhi < 2500: return "moderate", "#f59e0b"
    return "concentrated", "#ef4444"


def analyze_dimension(ads, dim_key, color_map=None):
    groups = defaultdict(lambda: {"spend": 0, "impressions": 0, "purchases": 0, "revenue": 0, "count": 0, "winners": 0})
    for ad in ads:
        val = ad["parsed"][dim_key]
        g = groups[val]
        g["spend"] += ad["spend"]
        g["impressions"] += ad["impressions"]
        g["purchases"] += ad["purchases"]
        g["revenue"] += ad["purchase_value"]
        g["count"] += 1
        if ad.get("tier") == "Winner": g["winners"] += 1
    total = sum(g["spend"] for g in groups.values())
    for val, g in groups.items():
        g["spend_pct"] = (g["spend"] / total * 100) if total > 0 else 0
        g["roas"] = g["revenue"] / g["spend"] if g["spend"] > 0 else 0
        g["cpa"] = g["spend"] / g["purchases"] if g["purchases"] > 0 else 0
        g["color"] = (color_map or {}).get(val, "#94a3b8")
    spend_shares = [g["spend_pct"] for g in groups.values() if total > 0]
    hhi = calculate_hhi(spend_shares)
    rating, rating_color = hhi_rating(hhi)
    return {"groups": sorted(groups.items(), key=lambda x: -x[1]["spend"]), "hhi": hhi, "rating": rating, "rating_color": rating_color, "total_spend": total}


def run_analysis(ads, primary_metric="cpa", metric_target=0):
    total_spend = sum(a["spend"] for a in ads)
    total_purchases = sum(a["purchases"] for a in ads)
    total_revenue = sum(a["purchase_value"] for a in ads)
    overall_roas = total_revenue / total_spend if total_spend > 0 else 0
    overall_cpa = total_spend / total_purchases if total_purchases > 0 else 0

    # Parse all ads
    for ad in ads:
        ad["parsed"] = parse_ad_name(ad["name"])
        ad["is_video"] = ad["video_3sec"] > 0 or ad["thruplay"] > 0 or ad["video_p25"] > 0
        if ad["is_video"] and ad["impressions"] > 0:
            v3s = ad["video_3sec"] if ad["video_3sec"] > 0 else ad["video_p25"]
            ad["thumbstop_rate"] = (v3s / ad["impressions"]) * 100
            ad["hold_rate"] = (ad["thruplay"] / v3s) * 100 if v3s > 0 else 0
        else:
            ad["thumbstop_rate"] = 0
            ad["hold_rate"] = 0
        # Primary metric per ad
        ad["cpa"] = ad["spend"] / ad["purchases"] if ad["purchases"] > 0 else 0

    # Classification threshold — based on media buying logic
    # An ad needs enough spend to have generated 3 purchases at actual CPA
    # OR 5× target CPA — whichever is higher. Below this = insufficient data.
    classification_threshold = max(overall_cpa * 3, metric_target * 5) if metric_target > 0 else overall_cpa * 3
    classification_threshold = max(classification_threshold, 50)  # Absolute floor

    # Classification always uses blended account performance as benchmark
    # Target CPA/ROAS is shown as a reference line, not for classification
    for ad in ads:
        if ad["spend"] < classification_threshold:
            ad["tier"] = "Insufficient Data"
        elif ad["purchases"] == 0:
            ad["tier"] = "Loser"
        elif primary_metric == "cpa":
            if ad["cpa"] <= overall_cpa:
                ad["tier"] = "Winner"
            elif ad["cpa"] <= overall_cpa * 1.5:
                ad["tier"] = "Mid"
            else:
                ad["tier"] = "Loser"
        else:  # ROAS
            if ad["roas"] >= overall_roas:
                ad["tier"] = "Winner"
            elif ad["roas"] >= overall_roas * 0.5:
                ad["tier"] = "Mid"
            else:
                ad["tier"] = "Loser"

    winners = [a for a in ads if a["tier"] == "Winner"]
    mids = [a for a in ads if a["tier"] == "Mid"]
    losers = [a for a in ads if a["tier"] == "Loser"]
    insufficient = [a for a in ads if a["tier"] == "Insufficient Data"]
    classified_ads = [a for a in ads if a["tier"] != "Insufficient Data"]

    # Creative volume — meaningful spend threshold (same as classification)
    spend_threshold = classification_threshold
    ads_above_threshold = classified_ads
    ads_below_threshold = insufficient
    top5_spend = sum(a["spend"] for a in sorted(ads, key=lambda x: -x["spend"])[:5])
    top10_spend = sum(a["spend"] for a in sorted(ads, key=lambda x: -x["spend"])[:10])

    parseable = [a for a in ads if a["parsed"]["parseable"]]
    unparseable = [a for a in ads if not a["parsed"]["parseable"]]
    compliance_rate = (len(parseable) / len(ads) * 100) if ads else 0

    dim_funnel = analyze_dimension(ads, "funnel", FUNNEL_COLORS)
    dim_angle = analyze_dimension([a for a in ads if a["parsed"]["parseable"]], "angle", ANGLE_COLORS)
    dim_media = analyze_dimension(ads, "mediatype", MEDIA_COLORS)

    video_ads = [a for a in ads if a["is_video"]]
    avg_thumbstop = sum(a["thumbstop_rate"] for a in video_ads) / len(video_ads) if video_ads else 0
    avg_hold = sum(a["hold_rate"] for a in video_ads) / len(video_ads) if video_ads else 0
    video_spend = sum(a["spend"] for a in video_ads)
    video_roas = sum(a["purchase_value"] for a in video_ads) / video_spend if video_spend > 0 else 0
    video_cpa = video_spend / sum(a["purchases"] for a in video_ads) if sum(a["purchases"] for a in video_ads) > 0 else 0

    dead_weight = sorted([a for a in ads if a["spend"] > 5 and a["purchases"] == 0], key=lambda x: -x["spend"])
    dead_weight_spend = sum(a["spend"] for a in dead_weight)

    # Frequency analysis
    ads_with_freq = [a for a in ads if a.get("frequency", 0) > 0]
    avg_frequency = sum(a["frequency"] for a in ads_with_freq) / len(ads_with_freq) if ads_with_freq else 0
    # Fatigue flags: high frequency + high spend
    fatigue_threshold = 4.0
    fatigued_ads = sorted([a for a in ads if a.get("frequency", 0) >= fatigue_threshold and a["spend"] >= spend_threshold], key=lambda x: -x["frequency"])

    # Cross-dimensional: Angle x Funnel
    cross_af = defaultdict(lambda: defaultdict(lambda: {"spend": 0, "purchases": 0, "revenue": 0}))
    for ad in parseable:
        c = cross_af[ad["parsed"]["angle"]][ad["parsed"]["funnel"]]
        c["spend"] += ad["spend"]
        c["purchases"] += ad["purchases"]
        c["revenue"] += ad["purchase_value"]

    # Identity analysis
    identity_groups = defaultdict(lambda: {"spend": 0, "purchases": 0, "revenue": 0, "count": 0})
    for ad in ads:
        ident = ad["parsed"].get("identity", "") or "Brand"
        g = identity_groups[ident]
        g["spend"] += ad["spend"]
        g["purchases"] += ad["purchases"]
        g["revenue"] += ad["purchase_value"]
        g["count"] += 1

    # Frequency analysis
    for ad in ads:
        ad["frequency"] = ad["impressions"] / (ad["impressions"] / ad["cpm"] * 1000) if ad["cpm"] > 0 and ad["impressions"] > 0 else 0
        # Simplified: frequency ≈ impressions / reach. We don't have reach directly,
        # so we flag high-frequency based on CPM trends. Will be enhanced when frequency
        # is pulled directly from API.

    # Offer detection — check if ad is offer-based
    offer_keywords = ["offer", "off", "discount", "promo", "sale", "price", "deal", "free"]
    for ad in ads:
        name_lower = ad["name"].lower() + " " + ad["adset"].lower()
        ad["is_offer"] = any(kw in name_lower for kw in offer_keywords)
    offer_ads = [a for a in classified_ads if a["is_offer"]]
    non_offer_ads = [a for a in classified_ads if not a["is_offer"]]
    offer_pct = (len(offer_ads) / len(classified_ads) * 100) if classified_ads else 0

    # Video length buckets
    video_buckets = {"0-15s": [], "15-30s": [], "30-45s": [], "45-60s": [], "1min+": []}
    for ad in video_ads:
        dur = ad["video_duration"]
        if dur <= 0:
            continue
        elif dur <= 15:
            video_buckets["0-15s"].append(ad)
        elif dur <= 30:
            video_buckets["15-30s"].append(ad)
        elif dur <= 45:
            video_buckets["30-45s"].append(ad)
        elif dur <= 60:
            video_buckets["45-60s"].append(ad)
        else:
            video_buckets["1min+"].append(ad)

    # Hit rates — two variants
    # 1. Classified hit rate: winners / (winners + mids + losers) — excludes insufficient data
    # 2. Account hit rate: winners / all ads — includes insufficient data
    hit_rate_classified = (len(winners) / len(classified_ads) * 100) if classified_ads else 0
    hit_rate_account = (len(winners) / len(ads) * 100) if ads else 0

    # ============ SCORING ============
    # Funnel Balance (15%) — penalty starts at 40%
    funnel_shares = [g["spend_pct"] for _, g in dim_funnel["groups"]]
    max_funnel = max(funnel_shares) if funnel_shares else 100
    funnel_score = max(0, min(100, 100 - max(0, (max_funnel - 40)) * 1.67))

    # Angle Diversity (15%) — HHI based
    angle_score = max(0, min(100, 100 - (dim_angle["hhi"] - 500) / 40))

    # Media Type Diversity (10%) — penalty starts at 35%
    media_shares = [g["spend_pct"] for _, g in dim_media["groups"]]
    max_media = max(media_shares) if media_shares else 100
    media_score = max(0, min(100, 100 - max(0, (max_media - 35)) * 1.54))

    # Winner Hit Rate (25%) — logarithmic, uses classified hit rate
    hit_rate_score = min(100, 40 * math.log(1 + hit_rate_classified) / math.log(1 + 8)) if hit_rate_classified > 0 else 0
    hit_rate_score = min(100, hit_rate_score * 2.5)

    # Spend on Winners (20%)
    winner_spend = sum(a["spend"] for a in winners)
    winner_spend_pct = (winner_spend / total_spend * 100) if total_spend > 0 else 0
    spend_winner_score = min(100, (winner_spend_pct / 60) * 100)

    # Creative Volume (10%) — scale by account spend tier
    weeks = 4.3
    monthly_spend = total_spend
    if monthly_spend < 5000: vol_bench = 3
    elif monthly_spend < 15000: vol_bench = 5
    elif monthly_spend < 50000: vol_bench = 8
    else: vol_bench = 12
    volume_score = min(100, (len(classified_ads) / weeks / vol_bench) * 100)

    # Composite (6 sub-scores, 100% total)
    composite = round(
        funnel_score * 0.15 +
        angle_score * 0.15 +
        media_score * 0.10 +
        hit_rate_score * 0.25 +
        spend_winner_score * 0.25 +
        volume_score * 0.10
    )

    return {
        "ads": ads, "total_spend": total_spend, "total_purchases": total_purchases,
        "total_revenue": total_revenue, "overall_roas": overall_roas, "overall_cpa": overall_cpa,
        "primary_metric": primary_metric, "metric_target": metric_target,
        "winners": winners, "mids": mids, "losers": losers, "insufficient": insufficient,
        "classified_ads": classified_ads,
        "classification_threshold": classification_threshold,
        "hit_rate_classified": hit_rate_classified, "hit_rate_account": hit_rate_account,
        "winner_spend": winner_spend, "winner_spend_pct": winner_spend_pct,
        "spend_threshold": spend_threshold,
        "ads_above_threshold": ads_above_threshold, "ads_below_threshold": ads_below_threshold,
        "offer_ads": offer_ads, "non_offer_ads": non_offer_ads, "offer_pct": offer_pct,
        "video_buckets": video_buckets,
        "top5_spend": top5_spend, "top10_spend": top10_spend,
        "parseable": parseable, "unparseable": unparseable, "compliance_rate": compliance_rate,
        "dim_funnel": dim_funnel, "dim_angle": dim_angle, "dim_media": dim_media,
        "video_ads": video_ads, "avg_thumbstop": avg_thumbstop, "avg_hold": avg_hold,
        "video_spend": video_spend, "video_roas": video_roas, "video_cpa": video_cpa,
        "dead_weight": dead_weight, "dead_weight_spend": dead_weight_spend,
        "avg_frequency": avg_frequency, "fatigued_ads": fatigued_ads,
        "cross_af": cross_af, "identity_groups": identity_groups,
        "composite": composite,
        "sub_scores": {
            "funnel_balance": round(funnel_score, 1), "angle_diversity": round(angle_score, 1),
            "media_diversity": round(media_score, 1), "hit_rate": round(hit_rate_score, 1),
            "spend_on_winners": round(spend_winner_score, 1),
            "volume": round(volume_score, 1),
        },
    }


# ============================================================
# HTML GENERATION
# ============================================================

def fmt_money(val):
    return f"£{val:,.0f}" if val >= 1 else f"£{val:.2f}"

def fmt_roas(val):
    return f"{val:.2f}x"

def fmt_cpa(val):
    return f"£{val:.2f}" if val > 0 else "—"

def fmt_metric(ad_or_group, analysis):
    """Format the primary metric for display."""
    m = analysis["primary_metric"]
    t = analysis["metric_target"]
    if m == "cpa":
        val = ad_or_group.get("cpa", ad_or_group.get("spend", 0) / ad_or_group.get("purchases", 1) if ad_or_group.get("purchases", 0) > 0 else 0)
        if val <= 0: return "—"
        color = "#10b981" if (t > 0 and val <= t) else "#ef4444" if (t > 0 and val > t * 1.5) else "#f59e0b" if t > 0 else ""
        style = f' style="color:{color}"' if color else ""
        return f'<span{style}>£{val:.2f}</span>'
    else:
        val = ad_or_group.get("roas", ad_or_group.get("revenue", 0) / ad_or_group.get("spend", 1) if ad_or_group.get("spend", 0) > 0 else 0)
        if val <= 0: return "—"
        color = "#10b981" if (t > 0 and val >= t) else "#ef4444" if (t > 0 and val < t * 0.5) else "#f59e0b" if t > 0 else ""
        style = f' style="color:{color}"' if color else ""
        return f'<span{style}>{val:.2f}x</span>'

def pct(val, total):
    return round(val / total * 100, 1) if total > 0 else 0

def score_color(score):
    if score >= 70: return "#10b981"
    if score >= 45: return "#f59e0b"
    return "#ef4444"

def score_label(score):
    if score >= 70: return "Healthy"
    if score >= 45: return "Moderate"
    return "At Risk"

def tier_badge(tier):
    colors = {"Winner": "#10b981", "Mid": "#f59e0b", "Loser": "#ef4444"}
    return f'<span class="badge" style="background:{colors.get(tier,"#94a3b8")};color:white">{tier}</span>'


def generate_frequency_section(a):
    """Generate frequency & fatigue HTML section with daily chart."""
    daily = a.get("daily_frequency", [])
    fatigued = a.get("fatigued_ads", [])
    avg_f = a.get("avg_frequency", 0)

    freq_color = "#ef4444" if avg_f >= 4 else "#f59e0b" if avg_f >= 2.5 else "#10b981"

    html = f'''<div class="card">
        <div class="card-header"><span class="card-icon">🔄</span><h3>Frequency & Fatigue</h3></div>
        <div class="video-summary">
            <div class="metric-box"><div class="metric-value" style="color:{freq_color}">{avg_f:.2f}</div><div class="metric-label">Avg Account Frequency</div><div class="metric-bench">{"⚠️ High — creative fatigue risk" if avg_f >= 3.5 else "Healthy" if avg_f < 2.5 else "Monitor"}</div></div>
            <div class="metric-box"><div class="metric-value" style="color:{"#ef4444" if len(fatigued) > 0 else "#10b981"}">{len(fatigued)}</div><div class="metric-label">Fatigued Ads</div><div class="metric-bench">Frequency ≥ 4.0 with meaningful spend</div></div>
        </div>'''

    # Daily frequency chart
    if daily:
        labels = json.dumps([d["date"][-5:] for d in daily])  # MM-DD format
        freq_data = json.dumps([d["frequency"] for d in daily])
        cpm_data = json.dumps([d["cpm"] for d in daily])
        html += f'''
        <h4>30-Day Frequency Trend</h4>
        <div style="height:250px;margin-bottom:20px"><canvas id="freqChart"></canvas></div>
        <script>
        new Chart(document.getElementById("freqChart"), {{
            type: "line",
            data: {{
                labels: {labels},
                datasets: [
                    {{ label: "Frequency", data: {freq_data}, borderColor: "#3b82f6", backgroundColor: "rgba(59,130,246,0.1)", fill: true, tension: 0.3, yAxisID: "y" }},
                    {{ label: "CPM (£)", data: {cpm_data}, borderColor: "#f59e0b", borderDash: [5,5], tension: 0.3, yAxisID: "y1" }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ position: "top" }} }},
                scales: {{
                    y: {{ position: "left", title: {{ display: true, text: "Frequency" }}, min: 0 }},
                    y1: {{ position: "right", title: {{ display: true, text: "CPM (£)" }}, grid: {{ drawOnChartArea: false }} }}
                }}
            }}
        }});
        </script>'''

    # Fatigued ads table
    if fatigued:
        html += '<h4>Ads Showing Fatigue Signals</h4><table class="data-table"><thead><tr><th>Ad</th><th>Frequency</th><th>Spend</th><th>CTR</th><th>CPA</th></tr></thead><tbody>'
        for fa in fatigued[:8]:
            ns = fa["name"][:55] + "..." if len(fa["name"]) > 55 else fa["name"]
            cpa = fmt_cpa(fa.get("cpa", 0))
            html += f'<tr><td class="name-cell">{ns}</td><td style="color:#ef4444"><strong>{fa["frequency"]:.1f}</strong></td><td>{fmt_money(fa["spend"])}</td><td>{fa["ctr"]:.2f}%</td><td>{cpa}</td></tr>'
        html += '</tbody></table>'
    elif avg_f < 3:
        html += '<p class="muted">No ads showing fatigue signals. Frequency is healthy across the account.</p>'

    html += '<div class="interpretation" id="interp-frequency"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:frequency --></div></details></div></div>'
    return html


def generate_hooks_section(gemini_data):
    """Generate hooks & headlines performance table from Gemini deep mode data."""
    if not gemini_data:
        return ""

    # Sort by spend descending
    sorted_data = sorted(gemini_data, key=lambda x: -x.get("spend", 0))

    # Hook type colors
    hook_colors = {
        "Question": "#3b82f6", "Bold Claim": "#f59e0b", "Social Proof": "#8b5cf6",
        "Problem Agitation": "#ef4444", "Testimonial": "#10b981", "Demonstration": "#06b6d4",
        "Offer/Price": "#f43f5e", "Pattern Interrupt": "#ec4899", "No Hook": "#6b7280",
    }

    html = f'''<div class="card">
        <div class="card-header"><span class="card-icon">🎯</span><h3>Hooks & Headlines Performance</h3><span class="badge">Deep Mode · {len(sorted_data)} ads analysed</span></div>
        <div class="card-body">'''

    # Hook type summary strip
    hook_counts = {}
    hook_spend = {}
    for item in sorted_data:
        ht = item.get("hook_type", "Unknown")
        hook_counts[ht] = hook_counts.get(ht, 0) + 1
        hook_spend[ht] = hook_spend.get(ht, 0) + item.get("spend", 0)

    total_spend = sum(hook_spend.values()) or 1
    html += '<div class="metric-strip">'
    for ht, count in sorted(hook_counts.items(), key=lambda x: -hook_spend.get(x[0], 0)):
        pct = hook_spend[ht] / total_spend * 100
        color = hook_colors.get(ht, "#6b7280")
        html += f'<div class="metric-box"><div class="metric-value" style="color:{color}">{count}</div><div class="metric-label">{ht}</div><div class="metric-bench">{pct:.0f}% of spend</div></div>'
    html += '</div>'

    # Per-ad hooks table
    html += '<h4>Hook Text × Performance</h4>'
    html += '<table class="data-table"><thead><tr><th>Ad</th><th>Hook Text</th><th>Type</th><th>Spend</th><th>CPA</th><th>CTR</th></tr></thead><tbody>'
    for item in sorted_data:
        name = item.get("ad_name", "")
        name_short = name[:45] + "..." if len(name) > 45 else name
        hook = item.get("hook_text", "N/A")
        hook_short = hook[:60] + "..." if len(hook) > 60 else hook
        ht = item.get("hook_type", "Unknown")
        color = hook_colors.get(ht, "#6b7280")
        spend = fmt_money(item.get("spend", 0))
        cpa = fmt_cpa(item.get("cpa", 0))
        ctr = f'{item.get("ctr", 0):.2f}%'

        html += f'<tr><td class="name-cell" title="{name}">{name_short}</td>'
        html += f'<td title="{hook}"><em>{hook_short}</em></td>'
        html += f'<td><span style="color:{color};font-weight:600">{ht}</span></td>'
        html += f'<td>{spend}</td><td>{cpa}</td><td>{ctr}</td></tr>'
    html += '</tbody></table>'

    # Headlines table (only if any differ from hook text)
    headlines = [item for item in sorted_data if item.get("headline_text", "") not in ("", "Same as hook", "No text overlay")]
    if headlines:
        html += '<h4>Headline Text on Creative</h4>'
        html += '<table class="data-table"><thead><tr><th>Ad</th><th>Headline</th><th>Spend</th><th>CPA</th></tr></thead><tbody>'
        for item in headlines:
            name = item.get("ad_name", "")
            name_short = name[:45] + "..." if len(name) > 45 else name
            headline = item.get("headline_text", "")
            hl_short = headline[:70] + "..." if len(headline) > 70 else headline
            html += f'<tr><td class="name-cell">{name_short}</td><td><em>{hl_short}</em></td><td>{fmt_money(item.get("spend", 0))}</td><td>{fmt_cpa(item.get("cpa", 0))}</td></tr>'
        html += '</tbody></table>'

    html += '<div class="interpretation" id="interp-hooks"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:hooks --></div></details></div>'
    html += '</div></div>'
    return html


def generate_html(analysis, client_name, account_id, days):
    a = analysis
    ads = a["ads"]
    composite = a["composite"]
    ss = a["sub_scores"]
    metric_label = "CPA" if a["primary_metric"] == "cpa" else "ROAS"
    target_str = f"Target: {fmt_cpa(a['metric_target'])}" if a["primary_metric"] == "cpa" and a["metric_target"] > 0 else f"Target: {a['metric_target']:.1f}x" if a["metric_target"] > 0 else ""

    # Score ring
    circ = 2 * 3.14159 * 54
    offset = circ * (1 - composite / 100)
    color = score_color(composite)
    label = score_label(composite)
    score_ring = f'''<div class="score-ring">
        <svg width="160" height="160" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#e5e7eb" stroke-width="10"/>
            <circle cx="60" cy="60" r="54" fill="none" stroke="{color}" stroke-width="10"
                stroke-dasharray="{circ}" stroke-dashoffset="{offset}" stroke-linecap="round" transform="rotate(-90 60 60)"/>
            <text x="60" y="55" text-anchor="middle" font-size="32" font-weight="700" fill="{color}">{composite}</text>
            <text x="60" y="72" text-anchor="middle" font-size="11" fill="#6b7280">/100</text>
        </svg>
        <div class="score-label" style="color:{color}">{label}</div>
    </div>'''

    # Sub-score bars — weights shift when deep mode adds hook diversity
    has_hooks = "hook_diversity" in ss
    sub_items = [
        ("Funnel Balance", ss["funnel_balance"], 12 if has_hooks else 15),
        ("Angle Diversity", ss["angle_diversity"], 13 if has_hooks else 15),
        ("Media Type Diversity", ss["media_diversity"], 10),
        ("Winner Hit Rate", ss["hit_rate"], 25),
        ("Spend on Winners", ss["spend_on_winners"], 25),
        ("Creative Volume", ss["volume"], 5 if has_hooks else 10),
    ]
    if has_hooks:
        sub_items.append(("Hook Type Diversity", ss["hook_diversity"], 10))
    sub_bars = ""
    for lbl, sc, wt in sub_items:
        c = score_color(sc)
        sub_bars += f'''<div class="sub-score">
            <div class="sub-label">{lbl} <span class="weight">({wt}%)</span></div>
            <div class="sub-track"><div class="sub-fill" style="width:{max(2,sc)}%;background:{c}"></div></div>
            <div class="sub-value" style="color:{c}">{sc:.0f}</div>
        </div>'''

    # Dimension card builder
    def dim_card(title, dim, icon, section_id):
        h = f'<div class="card"><div class="card-header"><span class="card-icon">{icon}</span><h3>{title}</h3>'
        h += f'<span class="badge" style="background:{dim["rating_color"]};color:white">{dim["rating"].upper()} (HHI: {dim["hhi"]:.0f})</span></div><div class="dimension-bars">'
        for val, g in dim["groups"][:10]:
            bw = max(2, g["spend_pct"])
            if a["primary_metric"] == "cpa":
                perf = fmt_cpa(g["cpa"]) + " CPA" if g["purchases"] > 0 else "—"
            else:
                perf = fmt_roas(g["roas"]) + " ROAS" if g["purchases"] > 0 else "—"
            ws = f' · {g["winners"]}W' if g["winners"] > 0 else ""
            h += f'''<div class="bar-row">
                <div class="bar-label">{val}</div>
                <div class="bar-track"><div class="bar-fill" style="width:{bw}%;background:{g["color"]}">{g["spend_pct"]:.1f}%</div></div>
                <div class="bar-meta">{fmt_money(g["spend"])} · {g["count"]} ads · {perf}{ws}</div>
            </div>'''
        h += '</div>'
        # Interpretation placeholder
        h += f'<div class="interpretation" id="interp-{section_id}"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:{section_id} --></div></details></div>'
        h += '</div>'
        return h

    # Creative Volume section
    volume_html = f'''<div class="card">
        <div class="card-header"><span class="card-icon">📊</span><h3>Creative Volume</h3></div>
        <div class="volume-grid">
            <div class="metric-box"><div class="metric-value">{len(ads)}</div><div class="metric-label">Total Active Ads</div></div>
            <div class="metric-box"><div class="metric-value">{len(a["ads_above_threshold"])}</div><div class="metric-label">Above {fmt_money(a["spend_threshold"])} Spend</div><div class="metric-bench">Meaningful spend threshold</div></div>
            <div class="metric-box"><div class="metric-value" style="color:var(--muted)">{len(a["ads_below_threshold"])}</div><div class="metric-label">Below Threshold</div><div class="metric-bench">{fmt_money(sum(x["spend"] for x in a["ads_below_threshold"]))} total</div></div>
            <div class="metric-box"><div class="metric-value">{a["offer_pct"]:.0f}%</div><div class="metric-label">Offer Ads</div><div class="metric-bench">{len(a["offer_ads"])} offer / {len(a["non_offer_ads"])} non-offer</div></div>
        </div>
        <h4>Spend Concentration</h4>
        <table class="data-table">
            <thead><tr><th>Metric</th><th>Value</th></tr></thead>
            <tbody>
                <tr><td>% of spend in top 5 ads</td><td><strong>{pct(a["top5_spend"], a["total_spend"])}%</strong></td></tr>
                <tr><td>% of spend in top 10 ads</td><td><strong>{pct(a["top10_spend"], a["total_spend"])}%</strong></td></tr>
                <tr><td>Single ad > 20% of spend?</td><td>{"<strong style=color:#ef4444>Yes</strong> — " + sorted(ads, key=lambda x:-x["spend"])[0]["name"][:50] if sorted(ads, key=lambda x:-x["spend"])[0]["spend"] / a["total_spend"] > 0.2 else "<strong style=color:#10b981>No</strong>"}</td></tr>
                <tr><td>Winners ({len(a["winners"])}) share of spend</td><td><strong>{a["winner_spend_pct"]:.0f}%</strong></td></tr>
            </tbody>
        </table>
        <div class="interpretation" id="interp-volume"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:volume --></div></details></div>
    </div>'''

    # Winner section
    winner_angle = defaultdict(lambda: {"count": 0, "spend": 0})
    for w in a["winners"]:
        winner_angle[w["parsed"]["angle"]]["count"] += 1
        winner_angle[w["parsed"]["angle"]]["spend"] += w["spend"]
    wp = ""
    if winner_angle:
        wp = '<h4>Where do winners cluster?</h4><table class="data-table"><thead><tr><th>Angle</th><th>Winners</th><th>Spend</th></tr></thead><tbody>'
        for angle, d in sorted(winner_angle.items(), key=lambda x: -x[1]["spend"]):
            wp += f'<tr><td>{angle}</td><td>{d["count"]}</td><td>{fmt_money(d["spend"])}</td></tr>'
        wp += '</tbody></table>'

    # Winner classification detail
    if a["primary_metric"] == "cpa":
        win_def = f'CPA ≤ {fmt_cpa(a["overall_cpa"])} (at or below blended)'
        mid_def = f'CPA {fmt_cpa(a["overall_cpa"])}–{fmt_cpa(a["overall_cpa"]*1.5)}'
        lose_def = f'CPA > {fmt_cpa(a["overall_cpa"]*1.5)} or 0 purchases'
    else:
        win_def = f'ROAS ≥ {fmt_roas(a["overall_roas"])} (at or above blended)'
        mid_def = f'ROAS {fmt_roas(a["overall_roas"]*0.5)}–{fmt_roas(a["overall_roas"])}'
        lose_def = f'ROAS < {fmt_roas(a["overall_roas"]*0.5)} or 0 purchases'

    classified_count = len(a["classified_ads"])
    winner_html = f'''<div class="card">
        <div class="card-header"><span class="card-icon">⭐</span><h3>Winner / Mid / Loser Distribution</h3></div>
        <p class="muted" style="margin-bottom:12px">Minimum spend to classify: <strong>{fmt_money(a["classification_threshold"])}</strong> (max of 3× blended CPA, 5× target CPA). Ads below this threshold have insufficient data to judge.</p>
        <div class="winner-grid">
            <div class="metric-box" style="border-left:4px solid #10b981"><div class="metric-value" style="color:#10b981">{len(a["winners"])}</div><div class="metric-label">Winners ({pct(len(a["winners"]),classified_count)}%)</div><div class="metric-bench">{fmt_money(a["winner_spend"])} · {win_def}</div></div>
            <div class="metric-box" style="border-left:4px solid #f59e0b"><div class="metric-value" style="color:#f59e0b">{len(a["mids"])}</div><div class="metric-label">Mid ({pct(len(a["mids"]),classified_count)}%)</div><div class="metric-bench">{fmt_money(sum(x["spend"] for x in a["mids"]))} · {mid_def}</div></div>
            <div class="metric-box" style="border-left:4px solid #ef4444"><div class="metric-value" style="color:#ef4444">{len(a["losers"])}</div><div class="metric-label">Losers ({pct(len(a["losers"]),classified_count)}%)</div><div class="metric-bench">{fmt_money(sum(x["spend"] for x in a["losers"]))} · {lose_def}</div></div>
            <div class="metric-box" style="border-left:4px solid #94a3b8"><div class="metric-value" style="color:#94a3b8">{len(a["insufficient"])}</div><div class="metric-label">Insufficient Data</div><div class="metric-bench">{fmt_money(sum(x["spend"] for x in a["insufficient"]))} · Below {fmt_money(a["classification_threshold"])} spend</div></div>
        </div>
        <h4>Win Rate</h4>
        <table class="data-table" style="max-width:600px">
            <thead><tr><th>Metric</th><th>Value</th><th>Base</th></tr></thead>
            <tbody>
                <tr><td><strong>Classified Win Rate</strong></td><td><strong>{a["hit_rate_classified"]:.1f}%</strong></td><td>{len(a["winners"])} winners / {classified_count} classified ads (excl. insufficient data)</td></tr>
                <tr><td>Account Win Rate</td><td>{a["hit_rate_account"]:.1f}%</td><td>{len(a["winners"])} winners / {len(ads)} total ads (incl. insufficient data)</td></tr>
            </tbody>
        </table>
        {wp}
        <div class="interpretation" id="interp-winners"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:winners --></div></details></div>
    </div>'''

    # Heatmap
    funnel_display = {"TOF": "Problem Aware", "MOF": "Solution Aware", "BOF": "Product Aware"}
    funnels_order = ["TOF", "MOF", "BOF"]
    angles_sorted = sorted(a["cross_af"].keys(), key=lambda x: -sum(a["cross_af"][x][f]["spend"] for f in funnels_order))
    heatmap = '<div class="card"><div class="card-header"><span class="card-icon">🔥</span><h3>Angle × Funnel Heatmap</h3></div>'
    heatmap += '<table class="heatmap"><thead><tr><th>Angle</th>'
    for f in funnels_order: heatmap += f'<th>{funnel_display.get(f, f)}</th>'
    heatmap += f'<th>Total</th></tr></thead><tbody>'
    for angle in angles_sorted[:10]:
        heatmap += f'<tr><td class="angle-cell">{angle}</td>'
        row_total_spend = 0
        row_total_purch = 0
        for funnel in funnels_order:
            cell = a["cross_af"][angle][funnel]
            sp = cell["spend"]; row_total_spend += sp; row_total_purch += cell["purchases"]
            if sp > 0:
                if a["primary_metric"] == "cpa":
                    perf = fmt_cpa(sp / cell["purchases"]) if cell["purchases"] > 0 else "—"
                    perf_color = "#10b981" if cell["purchases"] > 0 and (a["metric_target"] <= 0 or sp/cell["purchases"] <= a["metric_target"]) else "#ef4444"
                else:
                    perf = fmt_roas(cell["revenue"]/sp)
                    perf_color = "#10b981" if cell["revenue"]/sp >= 0.3 else "#ef4444"
                intensity = min(1, sp / 1500)
                bg_a = 0.1 + intensity * 0.35
                heatmap += f'<td style="background:rgba(59,130,246,{bg_a})">{fmt_money(sp)}<br><span style="color:{perf_color};font-size:11px">{perf}</span></td>'
            else:
                heatmap += '<td class="empty-cell">—</td>'
        if a["primary_metric"] == "cpa":
            total_perf = fmt_cpa(row_total_spend / row_total_purch) if row_total_purch > 0 else "—"
        else:
            total_rev = sum(a["cross_af"][angle][f]["revenue"] for f in funnels_order)
            total_perf = fmt_roas(total_rev / row_total_spend) if row_total_spend > 0 else "—"
        heatmap += f'<td class="total-cell">{fmt_money(row_total_spend)}<br><span style="font-size:11px">{total_perf}</span></td></tr>'
    heatmap += '</tbody></table>'
    heatmap += '<div class="interpretation" id="interp-heatmap"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:heatmap --></div></details></div></div>'

    # Video section
    video_html = '<div class="card"><div class="card-header"><span class="card-icon">🎬</span><h3>Video Performance</h3></div>'
    if a["video_ads"]:
        vid_metric = fmt_cpa(a["video_cpa"]) + " CPA" if a["primary_metric"] == "cpa" else fmt_roas(a["video_roas"]) + " ROAS"
        acct_metric = fmt_cpa(a["overall_cpa"]) if a["primary_metric"] == "cpa" else fmt_roas(a["overall_roas"])
        vid_purchases = sum(v["purchases"] for v in a["video_ads"])
        video_html += f'''<div class="video-summary">
            <div class="metric-box"><div class="metric-value">{len(a["video_ads"])}</div><div class="metric-label">Video Ads</div><div class="metric-bench">{pct(a["video_spend"], a["total_spend"])}% of spend</div></div>
            <div class="metric-box"><div class="metric-value">{fmt_money(a["video_spend"])}</div><div class="metric-label">Video Spend</div></div>
            <div class="metric-box"><div class="metric-value">{vid_purchases:.0f}</div><div class="metric-label">Video Purchases</div></div>
            <div class="metric-box"><div class="metric-value">{vid_metric}</div><div class="metric-label">Video {metric_label}</div><div class="metric-bench">vs {acct_metric} account avg</div></div>
        </div>
        <h4>Performance by Video Length</h4>'''
        unknown_dur = [v for v in a["video_ads"] if v["video_duration"] <= 0]
        if unknown_dur:
            video_html += f'<p class="muted" style="margin-bottom:8px">⚠️ {len(unknown_dur)}/{len(a["video_ads"])} video ads have unknown duration (Meta API permission issue). Run in deep mode for Gemini-based duration detection.</p>'
        video_html += f'''<table class="data-table"><thead><tr><th>Duration</th><th>Ads</th><th>Spend</th><th>Purchases</th><th>{metric_label}</th><th>Hold Rate</th></tr></thead><tbody>'''
        for bucket_name in ["0-15s", "15-30s", "30-45s", "45-60s", "1min+"]:
            bads = a["video_buckets"][bucket_name]
            if not bads:
                video_html += f'<tr><td>{bucket_name}</td><td>0</td><td>—</td><td>—</td><td>—</td><td>—</td></tr>'
                continue
            bspend = sum(v["spend"] for v in bads)
            bpurch = sum(v["purchases"] for v in bads)
            bhold = sum(v["hold_rate"] for v in bads) / len(bads)
            if a["primary_metric"] == "cpa":
                bperf = fmt_cpa(bspend / bpurch) if bpurch > 0 else "—"
            else:
                brev = sum(v["purchase_value"] for v in bads)
                bperf = fmt_roas(brev / bspend) if bspend > 0 else "—"
            video_html += f'<tr><td><strong>{bucket_name}</strong></td><td>{len(bads)}</td><td>{fmt_money(bspend)}</td><td>{bpurch:.0f}</td><td>{bperf}</td><td>{bhold:.1f}%</td></tr>'
        video_html += '</tbody></table>'
        video_html += f'''<h4>Top Videos by Spend</h4>
        <table class="data-table"><thead><tr><th>Ad</th><th>Spend</th><th>{metric_label}</th><th>Purchases</th><th>Hold Rate</th><th>Duration</th></tr></thead><tbody>'''
        for v in sorted(a["video_ads"], key=lambda x: -x["spend"])[:10]:
            ns = v["name"][:55] + "..." if len(v["name"]) > 55 else v["name"]
            dur = f'{v["video_duration"]:.0f}s' if v["video_duration"] > 0 else "—"
            if a["primary_metric"] == "cpa":
                perf = fmt_cpa(v["cpa"])
            else:
                perf = fmt_roas(v["roas"])
            video_html += f'<tr><td class="name-cell" title="{v["name"]}">{ns}</td><td>{fmt_money(v["spend"])}</td><td>{perf}</td><td>{v["purchases"]:.0f}</td><td>{v["hold_rate"]:.1f}%</td><td>{dur}</td></tr>'
        video_html += '</tbody></table>'
    else:
        video_html += '<p class="muted">No video ads found in this period.</p>'
    video_html += f'<div class="interpretation" id="interp-video"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:video --></div></details></div></div>'

    # Dead weight
    dead_html = f'''<div class="card"><div class="card-header"><span class="card-icon">💀</span><h3>Dead Weight Ads</h3>
        <span class="badge" style="background:#ef4444;color:white">{fmt_money(a["dead_weight_spend"])} ({pct(a["dead_weight_spend"], a["total_spend"])}%)</span></div>
        <p class="muted" style="margin-bottom:12px">Ads with >£5 spend and 0 purchases.</p>
        <table class="data-table"><thead><tr><th>Ad</th><th>Spend</th><th>Impressions</th><th>CTR</th><th>Funnel</th><th>Angle</th></tr></thead><tbody>'''
    for dw in a["dead_weight"][:12]:
        ns = dw["name"][:55] + "..." if len(dw["name"]) > 55 else dw["name"]
        dead_html += f'<tr><td class="name-cell" title="{dw["name"]}">{ns}</td><td>{fmt_money(dw["spend"])}</td><td>{dw["impressions"]:,.0f}</td><td>{dw["ctr"]:.2f}%</td><td>{dw["parsed"]["funnel"]}</td><td>{dw["parsed"]["angle"]}</td></tr>'
    dead_html += '</tbody></table>'
    dead_html += '<div class="interpretation" id="interp-deadweight"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:deadweight --></div></details></div></div>'

    # Identity
    identity_html = '<div class="card"><div class="card-header"><span class="card-icon">🎭</span><h3>Identity / Third-Party Performance</h3></div>'
    identity_html += f'<table class="data-table"><thead><tr><th>Identity</th><th>Ads</th><th>Spend</th><th>Spend %</th><th>{metric_label}</th></tr></thead><tbody>'
    for ident, g in sorted(a["identity_groups"].items(), key=lambda x: -x[1]["spend"]):
        if a["primary_metric"] == "cpa":
            perf = fmt_cpa(g["spend"] / g["purchases"]) if g["purchases"] > 0 else "—"
        else:
            perf = fmt_roas(g["revenue"] / g["spend"]) if g["spend"] > 0 else "—"
        identity_html += f'<tr><td>{ident}</td><td>{g["count"]}</td><td>{fmt_money(g["spend"])}</td><td>{pct(g["spend"], a["total_spend"])}%</td><td>{perf}</td></tr>'
    identity_html += '</tbody></table></div>'

    # Top 20
    top_html = f'<div class="card"><div class="card-header"><span class="card-icon">🏆</span><h3>Top 20 Ads by Spend</h3></div>'
    top_html += f'<table class="data-table"><thead><tr><th>Ad</th><th>Tier</th><th>Funnel</th><th>Angle</th><th>Media</th><th>Spend</th><th>{metric_label}</th><th>Purchases</th></tr></thead><tbody>'
    for ad in sorted(ads, key=lambda x: -x["spend"])[:20]:
        ns = ad["name"][:45] + "..." if len(ad["name"]) > 45 else ad["name"]
        if a["primary_metric"] == "cpa":
            perf = fmt_cpa(ad["cpa"])
        else:
            perf = fmt_roas(ad["roas"])
        top_html += f'<tr><td class="name-cell" title="{ad["name"]}">{ns}</td><td>{tier_badge(ad["tier"])}</td><td>{ad["parsed"]["funnel"]}</td><td>{ad["parsed"]["angle"]}</td><td>{ad["parsed"]["mediatype"]}</td><td>{fmt_money(ad["spend"])}</td><td>{perf}</td><td>{ad["purchases"]:.0f}</td></tr>'
    top_html += '</tbody></table></div>'

    # Compliance
    comp_html = f'<div class="card"><div class="card-header"><span class="card-icon">📋</span><h3>Naming Compliance</h3></div>'
    comp_html += f'''<div class="compliance-grid">
        <div class="metric-box"><div class="metric-value" style="color:{score_color(a["compliance_rate"])}">{a["compliance_rate"]:.0f}%</div><div class="metric-label">Parseable</div></div>
        <div class="metric-box"><div class="metric-value">{len(a["parseable"])}</div><div class="metric-label">Structured</div></div>
        <div class="metric-box"><div class="metric-value" style="color:#ef4444">{len(a["unparseable"])}</div><div class="metric-label">Unstructured</div></div>
    </div>'''
    if a["unparseable"]:
        comp_html += '<h4>Unstructured Ads</h4><ul class="unstructured-list">'
        for ad in sorted(a["unparseable"], key=lambda x: -x["spend"])[:10]:
            comp_html += f'<li><span class="muted">{fmt_money(ad["spend"])}</span> — {ad["name"][:75]}</li>'
        comp_html += '</ul>'
    comp_html += '</div>'

    # Iterations placeholder
    iterations_html = '''<div class="card" id="iterations-section">
        <div class="card-header"><span class="card-icon">🔄</span><h3>Iteration Scripts</h3></div>
        <p class="muted" style="margin-bottom:12px">Specific scripts based on what the data shows. Each iteration references a live ad and proposes a testable variant.</p>
        <div id="iteration-scripts"><!-- ITERATIONS --></div>
    </div>'''

    # Metric context bar
    if a["primary_metric"] == "cpa":
        metric_kpi = f'<div class="kpi"><div class="kpi-value">{fmt_cpa(a["overall_cpa"])}</div><div class="kpi-label">Blended CPA</div></div>'
        if a["metric_target"] > 0:
            metric_kpi += f'<div class="kpi"><div class="kpi-value">{fmt_cpa(a["metric_target"])}</div><div class="kpi-label">Target CPA</div></div>'
    else:
        metric_kpi = f'<div class="kpi"><div class="kpi-value">{fmt_roas(a["overall_roas"])}</div><div class="kpi-label">Blended ROAS</div></div>'
        if a["metric_target"] > 0:
            metric_kpi += f'<div class="kpi"><div class="kpi-value">{fmt_roas(a["metric_target"])}</div><div class="kpi-label">Target ROAS</div></div>'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Creative Health — {client_name}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root {{ --bg:#fafaf9; --card:#fff; --border:#e7e5e4; --text:#1c1917; --muted:#78716c; --accent:#7c3aed; --accent-light:#f5f3ff; --accent-soft:#ede9fe; --sidebar:#1c1917; --sidebar-text:#d6d3d1; --sidebar-hover:#292524; --sidebar-active:#7c3aed; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ font-family:'Inter',system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; -webkit-font-smoothing:antialiased; }}
.layout {{ display:flex; max-width:1440px; margin:0 auto; }}
.sidebar {{ width:240px; background:var(--sidebar); color:var(--sidebar-text); padding:28px 0; position:sticky; top:0; height:100vh; overflow-y:auto; flex-shrink:0; }}
.sidebar-brand {{ padding:0 22px 20px; border-bottom:1px solid #292524; margin-bottom:16px; }}
.sidebar-brand-title {{ font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:#a8a29e; font-weight:600; }}
.sidebar-brand-name {{ font-size:15px; font-weight:700; color:#fafaf9; margin-top:4px; }}
.sidebar nav {{ display:flex; flex-direction:column; gap:2px; padding:0 12px; }}
.sidebar nav a {{ color:var(--sidebar-text); text-decoration:none; font-size:13px; padding:9px 12px; border-radius:8px; font-weight:500; transition:all .15s ease; display:flex; align-items:center; gap:10px; }}
.sidebar nav a:hover {{ background:var(--sidebar-hover); color:#fafaf9; }}
.sidebar nav a.active {{ background:var(--sidebar-active); color:white; }}
.sidebar nav .nav-dot {{ width:6px; height:6px; border-radius:50%; background:#57534e; flex-shrink:0; }}
.sidebar nav a:hover .nav-dot {{ background:#a8a29e; }}
.sidebar nav a.active .nav-dot {{ background:white; }}
.sidebar-score {{ margin-top:24px; padding:16px 22px; border-top:1px solid #292524; }}
.sidebar-score-label {{ font-size:10px; text-transform:uppercase; letter-spacing:1.5px; color:#a8a29e; font-weight:600; }}
.sidebar-score-value {{ font-size:36px; font-weight:800; color:#fafaf9; margin-top:4px; line-height:1; }}
.sidebar-score-status {{ font-size:12px; color:#a8a29e; margin-top:4px; }}
.container {{ flex:1; max-width:1180px; margin:0 auto; padding:32px 40px; min-width:0; }}
.section-title {{ scroll-margin-top:24px; }}
.header {{ text-align:center; padding:48px 0 36px; }}
.header h1 {{ font-size:32px; font-weight:800; letter-spacing:-.5px; background:linear-gradient(135deg,#0f172a 0%,#334155 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.header .subtitle {{ color:var(--muted); font-size:14px; margin-top:6px; font-weight:500; }}
.kpi-strip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; margin-bottom:28px; }}
.kpi {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:18px 16px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,.04); }}
.kpi .kpi-value {{ font-size:22px; font-weight:700; }}
.kpi .kpi-label {{ font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.6px; margin-top:4px; font-weight:600; }}
.score-section {{ display:flex; gap:36px; align-items:flex-start; background:var(--card); border:1px solid var(--border); border-radius:16px; padding:32px; margin-bottom:28px; flex-wrap:wrap; box-shadow:0 1px 3px rgba(0,0,0,.04); }}
.score-ring {{ text-align:center; flex-shrink:0; }}
.score-label {{ font-size:15px; font-weight:700; margin-top:6px; letter-spacing:-.2px; }}
.sub-scores {{ flex:1; min-width:300px; }}
.sub-scores h3 {{ margin-bottom:14px; font-size:15px; font-weight:700; }}
.sub-score {{ display:flex; align-items:center; gap:10px; margin-bottom:10px; }}
.sub-label {{ width:180px; font-size:13px; flex-shrink:0; font-weight:500; }}
.sub-label .weight {{ color:var(--muted); font-weight:400; }}
.sub-track {{ flex:1; height:6px; background:#e5e7eb; border-radius:3px; overflow:hidden; }}
.sub-fill {{ height:100%; border-radius:3px; transition:width .3s ease; }}
.sub-value {{ width:36px; text-align:right; font-weight:700; font-size:13px; }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:14px; padding:28px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,.04); }}
.card-header {{ display:flex; align-items:center; gap:10px; margin-bottom:18px; flex-wrap:wrap; }}
.card-header h3 {{ font-size:16px; font-weight:700; letter-spacing:-.2px; }}
.card-icon {{ font-size:18px; }}
.badge {{ display:inline-block; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:600; letter-spacing:.2px; }}
.dimension-bars {{ display:flex; flex-direction:column; gap:12px; }}
.bar-row {{ display:flex; align-items:center; gap:10px; }}
.bar-label {{ width:140px; font-size:13px; font-weight:600; flex-shrink:0; }}
.bar-track {{ flex:1; height:28px; background:#f1f5f9; border-radius:8px; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:8px; display:flex; align-items:center; padding:0 10px; color:white; font-size:11px; font-weight:600; min-width:40px; }}
.bar-meta {{ font-size:11px; color:var(--muted); width:240px; text-align:right; flex-shrink:0; }}
.video-summary,.compliance-grid,.winner-grid,.volume-grid,.metric-strip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:14px; margin-bottom:20px; }}
.metric-box {{ text-align:center; padding:18px 14px; background:#f8fafc; border-radius:10px; border:1px solid var(--border); }}
.metric-value {{ font-size:24px; font-weight:700; }}
.metric-label {{ font-size:11px; color:var(--muted); margin-top:4px; font-weight:500; }}
.metric-bench {{ font-size:10px; color:var(--muted); margin-top:2px; }}
.data-table {{ width:100%; border-collapse:separate; border-spacing:0; font-size:12px; }}
.data-table th {{ background:#f8fafc; padding:10px 12px; text-align:left; font-weight:600; border-bottom:2px solid var(--border); font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:var(--muted); }}
.data-table td {{ padding:10px 12px; border-bottom:1px solid #f1f5f9; }}
.data-table tbody tr {{ transition:background .15s ease; }}
.data-table tbody tr:hover {{ background:#f8fafc; }}
.data-table tbody tr:last-child td {{ border-bottom:none; }}
.name-cell {{ max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-family:'SF Mono','Fira Code',monospace; font-size:11px; }}
.heatmap {{ width:100%; border-collapse:separate; border-spacing:0; font-size:12px; }}
.heatmap th {{ background:#f8fafc; padding:10px; text-align:center; font-weight:600; border-bottom:2px solid var(--border); font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:var(--muted); }}
.heatmap td {{ padding:10px; text-align:center; border-bottom:1px solid #f1f5f9; }}
.heatmap .angle-cell {{ text-align:left; font-weight:600; }}
.heatmap .empty-cell {{ color:#d1d5db; }}
.heatmap .total-cell {{ background:#f8fafc; font-weight:700; }}
.interpretation {{ margin-top:18px; }}
.interp-toggle {{ cursor:pointer; font-size:13px; font-weight:600; color:var(--accent); padding:8px 0; list-style:none; }}
.interp-toggle::-webkit-details-marker {{ display:none; }}
.interp-toggle::before {{ content:"▸ "; font-size:12px; }}
details[open] .interp-toggle::before {{ content:"▾ "; }}
.interp-content {{ padding:18px 20px; background:var(--accent-light); border-radius:10px; margin-top:8px; font-size:13px; line-height:1.75; border:1px solid #dbeafe; }}
.interp-content p {{ margin-bottom:10px; }}
.interp-content strong {{ color:#1e40af; }}
.iteration-card {{ background:linear-gradient(135deg,#fffbeb 0%,#fef3c7 100%); border:1px solid #fde68a; border-radius:12px; padding:22px; margin-bottom:16px; }}
.iteration-card h4 {{ font-size:14px; margin-bottom:8px; font-weight:700; }}
.iteration-card .script-section {{ font-size:13px; margin-bottom:6px; line-height:1.6; }}
.iteration-card .script-label {{ font-weight:700; color:#92400e; display:inline-block; width:80px; }}
.iteration-card .script-meta {{ display:flex; gap:8px; margin-top:12px; flex-wrap:wrap; }}
.iteration-card .meta-tag {{ background:rgba(255,255,255,.6); padding:3px 10px; border-radius:6px; font-size:11px; font-weight:600; border:1px solid #fde68a; }}
.muted {{ color:var(--muted); }}
h4 {{ font-size:14px; margin:18px 0 10px; font-weight:700; letter-spacing:-.1px; }}
.section-title {{ font-size:18px; font-weight:800; margin:36px 0 16px; padding-top:20px; border-top:1px solid var(--border); letter-spacing:-.3px; text-transform:uppercase; font-size:12px; color:var(--muted); letter-spacing:1px; }}
.unstructured-list {{ list-style:none; padding:0; }}
.unstructured-list li {{ padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:12px; font-family:'SF Mono','Fira Code',monospace; }}
.footer {{ text-align:center; padding:40px 0; color:var(--muted); font-size:11px; font-weight:500; letter-spacing:.3px; }}
.cover-bar {{ width:100%; height:120px; object-fit:cover; border-radius:16px 16px 0 0; display:block; }}
.header-wrap {{ background:var(--card); border:1px solid var(--border); border-radius:16px; margin-bottom:28px; box-shadow:0 1px 3px rgba(0,0,0,.04); overflow:hidden; }}
.header-wrap .header {{ padding:28px 32px 24px; border-radius:0; }}
.header-actions {{ display:flex; gap:10px; justify-content:center; margin-top:14px; }}
.btn {{ display:inline-flex; align-items:center; gap:6px; padding:8px 18px; border-radius:8px; font-size:12px; font-weight:600; text-decoration:none; cursor:pointer; border:none; transition:all .15s ease; }}
.btn-primary {{ background:var(--accent); color:white; }}
.btn-primary:hover {{ background:#6d28d9; }}
.btn-outline {{ background:transparent; color:var(--text); border:1px solid var(--border); }}
.btn-outline:hover {{ background:#f8fafc; }}
.range-select {{ padding:8px 14px; border-radius:8px; font-size:12px; font-weight:600; border:1px solid var(--border); background:white; color:var(--text); cursor:pointer; font-family:inherit; }}
.range-select:hover {{ background:#f8fafc; }}
.date-range {{ display:inline-block; background:#f1f5f9; padding:4px 14px; border-radius:6px; font-size:12px; font-weight:600; color:var(--text); margin-top:8px; letter-spacing:.2px; }}
@media (max-width:900px) {{ .sidebar {{ display:none; }} .container {{ padding:24px 16px; }} }}
@media (max-width:768px) {{ .bar-meta {{ display:none; }} .score-section {{ flex-direction:column; align-items:center; }} }}
</style>
</head>
<body>
<div class="layout">
<aside class="sidebar">
    <div class="sidebar-brand">
        <div class="sidebar-brand-title">Creative Health</div>
        <div class="sidebar-brand-name">{(a.get("brand_icon", "") + " ") if a.get("brand_icon") else ""}{client_name}</div>
    </div>
    <nav>
        <a href="#sec-volume"><span class="nav-dot"></span>Volume</a>
        <a href="#sec-dimensions"><span class="nav-dot"></span>Dimensions</a>
        <a href="#sec-heatmap"><span class="nav-dot"></span>Cross-Dimensional</a>
        <a href="#sec-video"><span class="nav-dot"></span>Video</a>
        {'<a href="#sec-hooks"><span class="nav-dot"></span>Hooks & Headlines</a>' if a.get("gemini_data") else ''}
        <a href="#sec-identity"><span class="nav-dot"></span>Identity</a>
        <a href="#sec-frequency"><span class="nav-dot"></span>Frequency</a>
        <a href="#sec-efficiency"><span class="nav-dot"></span>Efficiency</a>
        <a href="#sec-iterations"><span class="nav-dot"></span>Iterations</a>
        <a href="#sec-ads"><span class="nav-dot"></span>Ad-Level Detail</a>
        <a href="#sec-compliance"><span class="nav-dot"></span>Naming</a>
    </nav>
    <div class="sidebar-score">
        <div class="sidebar-score-label">Health Score</div>
        <div class="sidebar-score-value" style="color:{color}">{composite}</div>
        <div class="sidebar-score-status">{label}</div>
    </div>
</aside>
<div class="container">
<div class="header-wrap">
    {'<img class="cover-bar" src="' + a.get("cover_image", "") + '" alt="">' if a.get("cover_image") else ""}
    <div class="header">
        <h1>{(a.get("brand_icon", "") + " ") if a.get("brand_icon") else ""}{client_name}</h1>
        <div class="subtitle">Creative Health Report · {account_id} {("· " + target_str) if target_str else ""}</div>
        <div class="date-range">{a.get("date_start", "")} &mdash; {a.get("date_end", "") if a.get("date_start") else f"Last {days} days"}</div>
        <div class="header-actions">
            <select id="range-select" class="range-select">
                <option value="7">Last 7 days</option>
                <option value="14">Last 14 days</option>
                <option value="30" selected>Last 30 days</option>
                <option value="60">Last 60 days</option>
                <option value="90">Last 90 days</option>
            </select>
            <button class="btn btn-primary" id="gen-btn" onclick="(()=>{{const d=document.getElementById('range-select').value;const p=`Run /creative-health on {account_id} for the last ${{d}} days. Client: {client_name}. Metric: {a['primary_metric'].upper()}. Target: {a['metric_target']}.`;navigator.clipboard.writeText(p);const b=document.getElementById('gen-btn');b.textContent='Copied — paste into Claude';setTimeout(()=>b.textContent='Generate New Report',2000)}})()">Generate New Report</button>
            <button class="btn btn-outline" onclick="window.print()">Download PDF</button>
        </div>
    </div>
</div>

<div class="kpi-strip">
    <div class="kpi"><div class="kpi-value">{len(ads)}</div><div class="kpi-label">Active Ads</div></div>
    <div class="kpi"><div class="kpi-value">{fmt_money(a["total_spend"])}</div><div class="kpi-label">Total Spend</div></div>
    <div class="kpi"><div class="kpi-value">{a["total_purchases"]:.0f}</div><div class="kpi-label">Purchases</div></div>
    {metric_kpi}
    <div class="kpi"><div class="kpi-value">{a["hit_rate_account"]:.1f}%</div><div class="kpi-label">Account Win Rate</div></div>
    <div class="kpi"><div class="kpi-value">{a["hit_rate_classified"]:.1f}%</div><div class="kpi-label">Classified Win Rate</div></div>
    <div class="kpi"><div class="kpi-value" style="color:{"#ef4444" if a["avg_frequency"] >= 4 else "#f59e0b" if a["avg_frequency"] >= 2.5 else "#10b981"}">{a["avg_frequency"]:.1f}</div><div class="kpi-label">Avg Frequency</div></div>
</div>

<div class="score-section">
    {score_ring}
    <div class="sub-scores">
        <h3>Creative Health Breakdown</h3>
        {sub_bars}
    </div>
</div>

<div class="card" style="background:#f8fafc">
    <details><summary class="interp-toggle" style="color:#64748b">How is this score calculated?</summary>
    <div class="interp-content" style="background:white">
        <p><strong>Creative Health Score</strong> is a weighted composite of {"7" if has_hooks else "6"} sub-scores. Each measures a different dimension of creative portfolio health.{" Deep Mode adds Hook Type Diversity." if has_hooks else ""}</p>
        <table class="data-table">
            <thead><tr><th>Sub-score</th><th>Weight</th><th>What it measures</th><th>How it's calculated</th></tr></thead>
            <tbody>
                <tr><td>Funnel Balance</td><td>{"12" if has_hooks else "15"}%</td><td>Are you testing across all awareness stages?</td><td>Starts at 100, loses 1.67 pts for every % above 40% in the most dominant stage</td></tr>
                <tr><td>Angle Diversity</td><td>{"13" if has_hooks else "15"}%</td><td>How concentrated is spend across messaging angles?</td><td>Based on HHI (see below). Lower HHI = more diverse = higher score</td></tr>
                <tr><td>Media Diversity</td><td>10%</td><td>Is the format mix balanced or single-format heavy?</td><td>Penalises if any single format holds >35% of spend</td></tr>
                <tr><td>Winner Hit Rate</td><td>25%</td><td>What % of classified ads are winners?</td><td>Logarithmic curve. Winner = CPA at or below blended average. Harder to max at higher rates</td></tr>
                <tr><td>Spend on Winners</td><td>25%</td><td>Is the algorithm scaling winners, or spreading evenly?</td><td>Winner spend % / 60% benchmark. 60% on winners = full score</td></tr>
                <tr><td>Creative Volume</td><td>{"5" if has_hooks else "10"}%</td><td>Are enough new concepts being shipped?</td><td>Classified ads/week vs spend-tier benchmark (£5-15k=5/wk, £15-50k=8/wk)</td></tr>
                {'<tr><td>Hook Type Diversity</td><td>10%</td><td>Are you testing different hook approaches?</td><td>HHI-based. Measures spend concentration across hook types (Question, Bold Claim, Social Proof, etc.)</td></tr>' if has_hooks else ''}
            </tbody>
        </table>
        <p style="margin-top:12px"><strong>HHI (Herfindahl-Hirschman Index)</strong> measures spend concentration. Square each value's spend share %, sum all squares. <strong>< 1500</strong> = diverse (green), <strong>1500-2500</strong> = moderate (amber), <strong>> 2500</strong> = concentrated (red). Example: 3 angles at 50%/30%/20% → HHI = 2500+900+400 = 3800 (concentrated).</p>
        <p><strong>Winner classification:</strong> Ads need ≥ {fmt_money(a["classification_threshold"])} spend to be classified (max of 3× blended {metric_label}, 5× target {metric_label}). Winners = {metric_label} at or better than blended average ({fmt_cpa(a["overall_cpa"]) if a["primary_metric"] == "cpa" else fmt_roas(a["overall_roas"])}). Losers = {metric_label} worse than 1.5× blended or 0 purchases.</p>
    </div>
    </details>
</div>

<h2 class="section-title" id="sec-volume">Creative Volume & Concentration</h2>
{volume_html}
{winner_html}

<h2 class="section-title" id="sec-dimensions">Dimension Analysis</h2>
{dim_card("Funnel Stage", a["dim_funnel"], "🎯", "funnel")}
{dim_card("Angle / Message Territory", a["dim_angle"], "💬", "angle")}
{dim_card("Media Type", a["dim_media"], "🖼️", "media")}

<h2 class="section-title" id="sec-heatmap">Cross-Dimensional</h2>
{heatmap}

<h2 class="section-title" id="sec-video">Video Performance</h2>
{video_html}

{f'<h2 class="section-title" id="sec-hooks">Hooks & Headlines Performance</h2>' + chr(10) + generate_hooks_section(a.get("gemini_data", [])) if a.get("gemini_data") else ""}

<h2 class="section-title" id="sec-identity">Identity Analysis</h2>
{identity_html}

<h2 class="section-title" id="sec-frequency">Frequency & Creative Fatigue</h2>
{generate_frequency_section(a)}

<h2 class="section-title" id="sec-efficiency">Efficiency</h2>
{dead_html}

<h2 class="section-title" id="sec-iterations">Iteration Scripts</h2>
{iterations_html}

<h2 class="section-title" id="sec-ads">Ad-Level Detail</h2>
{top_html}

<h2 class="section-title" id="sec-compliance">Naming Compliance</h2>
{comp_html}

<div class="footer">Generated {datetime.now().strftime("%d %b %Y, %H:%M")} · LWU Creative Health v2.1{" · Deep Mode" if a.get("gemini_data") else ""}</div>
</div>
</div>
<script>
(()=>{{const links=document.querySelectorAll('.sidebar nav a');const secs=[...links].map(l=>document.querySelector(l.getAttribute('href'))).filter(Boolean);const io=new IntersectionObserver(es=>{{es.forEach(e=>{{if(e.isIntersecting){{links.forEach(l=>l.classList.remove('active'));const i=secs.indexOf(e.target);if(i>=0)links[i].classList.add('active')}}}})}},{{rootMargin:'-20% 0px -70% 0px'}});secs.forEach(s=>io.observe(s))}})();
</script>
</body>
</html>'''
    return html


# ============================================================
# EXPORTS
# ============================================================

def save_enriched_csv(ads, output_path):
    fieldnames = [
        "ad_name", "ad_id", "campaign_name", "adset_name",
        "spend", "impressions", "clicks", "ctr", "cpc", "cpm",
        "purchases", "purchase_value", "roas", "cpa",
        "video_3sec", "thruplay", "video_p25", "video_p50", "video_p75", "video_p100",
        "video_duration", "thumbstop_rate", "hold_rate",
        "tier", "source", "parseable", "funnel", "angle", "painpoint",
        "mediatype", "product", "identity", "concept_id",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ad in ads:
            writer.writerow({
                "ad_name": ad["name"], "ad_id": ad["ad_id"],
                "campaign_name": ad["campaign"], "adset_name": ad["adset"],
                "spend": ad["spend"], "impressions": ad["impressions"],
                "clicks": ad["clicks"], "ctr": ad["ctr"], "cpc": ad["cpc"], "cpm": ad["cpm"],
                "purchases": ad["purchases"], "purchase_value": ad["purchase_value"],
                "roas": ad["roas"], "cpa": round(ad.get("cpa", 0), 2),
                "video_3sec": ad["video_3sec"], "thruplay": ad["thruplay"],
                "video_p25": ad["video_p25"], "video_p50": ad["video_p50"],
                "video_p75": ad["video_p75"], "video_p100": ad["video_p100"],
                "video_duration": ad["video_duration"],
                "thumbstop_rate": round(ad["thumbstop_rate"], 2),
                "hold_rate": round(ad["hold_rate"], 2),
                "tier": ad.get("tier", ""), "source": ad["parsed"]["source"],
                "parseable": ad["parsed"]["parseable"], "funnel": ad["parsed"]["funnel"],
                "angle": ad["parsed"]["angle"], "painpoint": ad["parsed"]["painpoint"],
                "mediatype": ad["parsed"]["mediatype"], "product": ad["parsed"]["product"],
                "identity": ad["parsed"]["identity"], "concept_id": ad["parsed"]["concept_id"],
            })


def save_summary_json(analysis, output_path, client_name, account_id, days):
    a = analysis
    # Build per-dimension summaries for Claude interpretation
    dim_summaries = {}
    for dim_name, dim_key in [("funnel", "dim_funnel"), ("angle", "dim_angle"), ("media", "dim_media")]:
        dim = a[dim_key]
        dim_summaries[dim_name] = {
            "hhi": dim["hhi"], "rating": dim["rating"],
            "groups": [{
                "name": name, "spend": round(g["spend"], 2), "spend_pct": round(g["spend_pct"], 1),
                "count": g["count"], "purchases": g["purchases"],
                "roas": round(g["roas"], 2),
                "cpa": round(g["cpa"], 2) if g["purchases"] > 0 else 0,
                "winners": g["winners"],
            } for name, g in dim["groups"]]
        }

    # Top 10 ads for iteration context
    top_ads = [{
        "name": ad["name"], "tier": ad.get("tier", ""),
        "spend": round(ad["spend"], 2), "purchases": ad["purchases"],
        "roas": round(ad["roas"], 2), "cpa": round(ad.get("cpa", 0), 2),
        "funnel": ad["parsed"]["funnel"], "angle": ad["parsed"]["angle"],
        "mediatype": ad["parsed"]["mediatype"], "product": ad["parsed"]["product"],
        "identity": ad["parsed"]["identity"], "painpoint": ad["parsed"]["painpoint"],
        "thumbstop_rate": round(ad["thumbstop_rate"], 1),
        "hold_rate": round(ad["hold_rate"], 1),
    } for ad in sorted(a["ads"], key=lambda x: -x["spend"])[:15]]

    # Dead weight for interpretation
    dead = [{
        "name": ad["name"], "spend": round(ad["spend"], 2),
        "funnel": ad["parsed"]["funnel"], "angle": ad["parsed"]["angle"],
    } for ad in a["dead_weight"][:10]]

    summary = {
        "client": client_name, "account_id": account_id, "days": days,
        "primary_metric": a["primary_metric"], "metric_target": a["metric_target"],
        "generated": datetime.now().isoformat(),
        "composite_score": a["composite"], "sub_scores": a["sub_scores"],
        "total_ads": len(a["ads"]), "total_spend": round(a["total_spend"], 2),
        "total_purchases": a["total_purchases"], "overall_roas": round(a["overall_roas"], 2),
        "overall_cpa": round(a["overall_cpa"], 2),
        "winners": len(a["winners"]),
        "hit_rate_classified": round(a["hit_rate_classified"], 1),
        "hit_rate_account": round(a["hit_rate_account"], 1),
        "winner_spend_pct": round(a["winner_spend_pct"], 1),
        "ads_above_threshold": len(a["ads_above_threshold"]),
        "ads_below_threshold": len(a["ads_below_threshold"]),
        "spend_threshold": round(a["spend_threshold"], 2),
        "top5_spend_pct": round(a["top5_spend"] / a["total_spend"] * 100, 1) if a["total_spend"] > 0 else 0,
        "top10_spend_pct": round(a["top10_spend"] / a["total_spend"] * 100, 1) if a["total_spend"] > 0 else 0,
        "avg_thumbstop": round(a["avg_thumbstop"], 1),
        "avg_hold_rate": round(a["avg_hold"], 1),
        "compliance_rate": round(a["compliance_rate"], 1),
        "dead_weight_spend": round(a["dead_weight_spend"], 2),
        "dead_weight_pct": round(a["dead_weight_spend"] / a["total_spend"] * 100, 1) if a["total_spend"] > 0 else 0,
        "dimensions": dim_summaries,
        "top_ads": top_ads,
        "dead_weight_ads": dead,
    }
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Generate Creative Health Report")
    parser.add_argument("--input", required=True, help="Path to ads CSV")
    parser.add_argument("--client", default="Client", help="Client name")
    parser.add_argument("--account", default="", help="Account ID")
    parser.add_argument("--days", type=int, default=30, help="Date range")
    parser.add_argument("--metric", choices=["cpa", "roas"], default="cpa", help="Primary metric")
    parser.add_argument("--target", type=float, default=0, help="Metric target (e.g., 25 for £25 CPA)")
    parser.add_argument("--daily-freq", default="", help="Path to daily_frequency.json")
    parser.add_argument("--cover-image", default="", help="URL for brand cover image in header")
    parser.add_argument("--icon", default="", help="Emoji icon for the brand")
    parser.add_argument("--output", default="creative-health-report.html", help="Output HTML path")
    args = parser.parse_args()

    print(f"Loading data from {args.input}...")
    ads = load_csv(args.input)
    print(f"Loaded {len(ads)} ads")

    # Load pull metadata for date range
    input_dir = os.path.dirname(args.input)
    meta_path = os.path.join(input_dir, "pull_metadata.json")
    pull_meta = {}
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            pull_meta = json.load(f)

    # Load frequency data
    daily_freq = []
    account_freq = None

    if args.daily_freq and os.path.exists(args.daily_freq):
        daily_freq = load_daily_frequency(args.daily_freq)
    else:
        auto_path = os.path.join(input_dir, "daily_frequency.json")
        if os.path.exists(auto_path):
            daily_freq = load_daily_frequency(auto_path)
    if daily_freq:
        print(f"Loaded {len(daily_freq)} daily frequency data points")

    acct_path = os.path.join(input_dir, "account_frequency.json")
    if os.path.exists(acct_path):
        account_freq = load_account_frequency(acct_path)
        print(f"Account period frequency: {account_freq.get('frequency', 0)}")

    # Load Gemini deep mode data if available
    gemini_path = os.path.join(input_dir, "gemini_analysis.json")
    gemini_data = load_gemini_analysis(gemini_path)
    if gemini_data:
        print(f"Loaded Gemini deep mode data: {len(gemini_data)} ads analysed")
        # Backfill missing video durations from Gemini analysis
        gemini_durations = {}
        for item in gemini_data:
            dur = item.get("estimated_duration_sec") or item.get("video_duration_api") or 0
            if dur > 0:
                gemini_durations[item["ad_id"]] = float(dur)
        if gemini_durations:
            backfilled = 0
            for ad in ads:
                if ad["video_duration"] <= 0 and ad["ad_id"] in gemini_durations:
                    ad["video_duration"] = gemini_durations[ad["ad_id"]]
                    backfilled += 1
            if backfilled:
                print(f"  Backfilled {backfilled} video durations from Gemini data")

    print(f"Running analysis (primary metric: {args.metric.upper()}, target: {args.target})...")
    analysis = run_analysis(ads, primary_metric=args.metric, metric_target=args.target)
    analysis["daily_frequency"] = daily_freq
    analysis["gemini_data"] = gemini_data

    # If deep mode data exists, calculate hook type diversity and recalculate composite
    if gemini_data:
        hook_spend = {}
        for item in gemini_data:
            ht = item.get("hook_type", "Unknown")
            hook_spend[ht] = hook_spend.get(ht, 0) + item.get("spend", 0)
        total_hook_spend = sum(hook_spend.values()) or 1
        hook_hhi = sum((s / total_hook_spend * 100) ** 2 for s in hook_spend.values())
        # HHI-based score: same logic as angle/media diversity
        if hook_hhi < 1500:
            hook_score = 100
        elif hook_hhi < 2500:
            hook_score = max(40, 100 - (hook_hhi - 1500) / 10)
        elif hook_hhi < 5000:
            hook_score = max(10, 40 - (hook_hhi - 2500) / 100)
        else:
            hook_score = 10
        analysis["hook_hhi"] = round(hook_hhi)
        analysis["sub_scores"]["hook_diversity"] = round(hook_score, 1)
        # Redistribute weights: funnel 15→12, angle 15→13, hook 10 new
        ss = analysis["sub_scores"]
        analysis["composite"] = round(
            ss["funnel_balance"] * 0.12 +
            ss["angle_diversity"] * 0.13 +
            ss["media_diversity"] * 0.10 +
            ss["hit_rate"] * 0.25 +
            ss["spend_on_winners"] * 0.25 +
            ss["volume"] * 0.05 +
            ss["hook_diversity"] * 0.10
        )

    # Override avg_frequency with the correct account-level period value
    if account_freq and account_freq.get("frequency", 0) > 0:
        analysis["avg_frequency"] = account_freq["frequency"]
        analysis["account_reach"] = account_freq.get("reach", 0)

    # Pass branding + date range to report
    # Embed cover image as base64 if it's a local file
    import base64 as b64mod
    cover_src = args.cover_image
    if cover_src and os.path.exists(cover_src):
        ext = os.path.splitext(cover_src)[1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext.lstrip("."), "image/jpeg")
        with open(cover_src, "rb") as img_f:
            cover_src = f"data:{mime};base64,{b64mod.b64encode(img_f.read()).decode()}"
    analysis["cover_image"] = cover_src
    analysis["brand_icon"] = args.icon
    analysis["date_start"] = pull_meta.get("start_date", "")
    analysis["date_end"] = pull_meta.get("end_date", "")

    print("Generating HTML report...")
    html = generate_html(analysis, args.client, args.account, args.days)

    output_dir = os.path.dirname(args.output) or "."
    os.makedirs(output_dir, exist_ok=True)
    with open(args.output, "w") as f:
        f.write(html)
    print(f"HTML report: {args.output}")

    csv_path = args.output.replace(".html", "-enriched.csv")
    save_enriched_csv(ads, csv_path)
    print(f"Enriched CSV: {csv_path}")

    json_path = args.output.replace(".html", "-summary.json")
    save_summary_json(analysis, json_path, args.client, args.account, args.days)
    print(f"Summary JSON: {json_path}")

    print(f"\nCreative Health Score: {analysis['composite']}/100 ({score_label(analysis['composite'])})")


if __name__ == "__main__":
    main()
