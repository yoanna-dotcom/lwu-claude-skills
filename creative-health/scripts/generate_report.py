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
            }
            if ad["spend"] > 0:
                ads.append(ad)
    return ads


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

    # Winner classification
    spends = sorted([a["spend"] for a in ads])
    median_spend = spends[len(spends) // 2] if spends else 0
    winner_threshold = median_spend * 10
    for ad in ads:
        if ad["spend"] >= winner_threshold and ad["purchases"] > 0:
            ad["tier"] = "Winner"
        elif ad["purchases"] > 0:
            ad["tier"] = "Mid"
        else:
            ad["tier"] = "Loser"

    winners = [a for a in ads if a["tier"] == "Winner"]
    mids = [a for a in ads if a["tier"] == "Mid"]
    losers = [a for a in ads if a["tier"] == "Loser"]

    # Creative volume — meaningful spend threshold
    # Threshold = 1% of total spend or £20, whichever is higher
    spend_threshold = max(20, total_spend * 0.01)
    ads_above_threshold = [a for a in ads if a["spend"] >= spend_threshold]
    ads_below_threshold = [a for a in ads if a["spend"] < spend_threshold]
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

    # ============ RECALIBRATED SCORING ============
    # Funnel Balance (10%) — penalty starts at 40% (not 50%)
    funnel_shares = [g["spend_pct"] for _, g in dim_funnel["groups"]]
    max_funnel = max(funnel_shares) if funnel_shares else 100
    funnel_score = max(0, min(100, 100 - max(0, (max_funnel - 40)) * 1.67))

    # Angle Diversity (10%) — HHI based
    angle_score = max(0, min(100, 100 - (dim_angle["hhi"] - 500) / 40))

    # Media Type Diversity (10%) — penalty starts at 35%
    media_shares = [g["spend_pct"] for _, g in dim_media["groups"]]
    max_media = max(media_shares) if media_shares else 100
    media_score = max(0, min(100, 100 - max(0, (max_media - 35)) * 1.54))

    # Winner Hit Rate (15%) — logarithmic, harder to max
    hit_rate = (len(winners) / len(ads) * 100) if ads else 0
    hit_rate_score = min(100, 40 * math.log(1 + hit_rate) / math.log(1 + 8)) if hit_rate > 0 else 0
    # Rescale: 8% → ~40, 15% → ~62, 25% → ~78
    hit_rate_score = min(100, hit_rate_score * 2.5)

    # Spend on Winners (15%) — logarithmic
    winner_spend = sum(a["spend"] for a in winners)
    winner_spend_pct = (winner_spend / total_spend * 100) if total_spend > 0 else 0
    spend_winner_score = min(100, (winner_spend_pct / 60) * 100)

    # Hold Rate (10%) — keep, but flag as approximate
    hold_score = min(100, (avg_hold / 25) * 100) if video_ads else 50

    # Naming Compliance (10%)
    compliance_score = compliance_rate

    # Creative Volume (10%) — scale by account spend tier
    weeks = 4.3
    ads_per_week = len(ads_above_threshold) / weeks  # Only count meaningful ads
    # Benchmark by spend tier: <£5k/mo=3/wk, £5-15k=5/wk, £15-50k=8/wk, >£50k=12/wk
    monthly_spend = total_spend  # This is already the period spend
    if monthly_spend < 5000: vol_bench = 3
    elif monthly_spend < 15000: vol_bench = 5
    elif monthly_spend < 50000: vol_bench = 8
    else: vol_bench = 12
    volume_score = min(100, (ads_per_week / vol_bench) * 100)

    # Composite — removed thumbstop until metric is fixed
    composite = round(
        funnel_score * 0.12 +
        angle_score * 0.12 +
        media_score * 0.12 +
        hit_rate_score * 0.18 +
        spend_winner_score * 0.18 +
        hold_score * 0.08 +
        compliance_score * 0.10 +
        volume_score * 0.10
    )

    return {
        "ads": ads, "total_spend": total_spend, "total_purchases": total_purchases,
        "total_revenue": total_revenue, "overall_roas": overall_roas, "overall_cpa": overall_cpa,
        "primary_metric": primary_metric, "metric_target": metric_target,
        "winners": winners, "mids": mids, "losers": losers,
        "winner_threshold": winner_threshold, "hit_rate": hit_rate,
        "winner_spend": winner_spend, "winner_spend_pct": winner_spend_pct,
        "spend_threshold": spend_threshold,
        "ads_above_threshold": ads_above_threshold, "ads_below_threshold": ads_below_threshold,
        "top5_spend": top5_spend, "top10_spend": top10_spend,
        "parseable": parseable, "unparseable": unparseable, "compliance_rate": compliance_rate,
        "dim_funnel": dim_funnel, "dim_angle": dim_angle, "dim_media": dim_media,
        "video_ads": video_ads, "avg_thumbstop": avg_thumbstop, "avg_hold": avg_hold,
        "video_spend": video_spend, "video_roas": video_roas, "video_cpa": video_cpa,
        "dead_weight": dead_weight, "dead_weight_spend": dead_weight_spend,
        "cross_af": cross_af, "identity_groups": identity_groups,
        "composite": composite,
        "sub_scores": {
            "funnel_balance": round(funnel_score, 1), "angle_diversity": round(angle_score, 1),
            "media_diversity": round(media_score, 1), "hit_rate": round(hit_rate_score, 1),
            "spend_on_winners": round(spend_winner_score, 1),
            "hold_rate": round(hold_score, 1), "compliance": round(compliance_score, 1),
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

    # Sub-score bars
    sub_items = [
        ("Funnel Balance", ss["funnel_balance"], 12),
        ("Angle Diversity", ss["angle_diversity"], 12),
        ("Media Type Diversity", ss["media_diversity"], 12),
        ("Winner Hit Rate", ss["hit_rate"], 18),
        ("Spend on Winners", ss["spend_on_winners"], 18),
        ("Hold Rate", ss["hold_rate"], 8),
        ("Naming Compliance", ss["compliance"], 10),
        ("Creative Volume", ss["volume"], 10),
    ]
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
            <div class="metric-box"><div class="metric-value" style="color:var(--muted)">{len(a["ads_below_threshold"])}</div><div class="metric-label">Below Threshold (Noise)</div><div class="metric-bench">{fmt_money(sum(x["spend"] for x in a["ads_below_threshold"]))} total</div></div>
            <div class="metric-box"><div class="metric-value">{len(a["ads_above_threshold"]) / 4.3:.1f}</div><div class="metric-label">Meaningful Ads / Week</div></div>
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

    winner_html = f'''<div class="card">
        <div class="card-header"><span class="card-icon">⭐</span><h3>Winner / Mid / Loser Distribution</h3></div>
        <p class="muted" style="margin-bottom:12px">Winner = spend ≥10× account median ({fmt_money(a["winner_threshold"])}) with ≥1 purchase.</p>
        <div class="winner-grid">
            <div class="metric-box" style="border-left:4px solid #10b981"><div class="metric-value" style="color:#10b981">{len(a["winners"])}</div><div class="metric-label">Winners ({pct(len(a["winners"]),len(ads))}%)</div><div class="metric-bench">{fmt_money(a["winner_spend"])} · {a["winner_spend_pct"]:.0f}% of spend</div></div>
            <div class="metric-box" style="border-left:4px solid #f59e0b"><div class="metric-value" style="color:#f59e0b">{len(a["mids"])}</div><div class="metric-label">Mid ({pct(len(a["mids"]),len(ads))}%)</div><div class="metric-bench">{fmt_money(sum(x["spend"] for x in a["mids"]))}</div></div>
            <div class="metric-box" style="border-left:4px solid #ef4444"><div class="metric-value" style="color:#ef4444">{len(a["losers"])}</div><div class="metric-label">Losers ({pct(len(a["losers"]),len(ads))}%)</div><div class="metric-bench">{fmt_money(sum(x["spend"] for x in a["losers"]))}</div></div>
        </div>
        {wp}
        <div class="interpretation" id="interp-winners"><details><summary class="interp-toggle">Data Interpretation</summary><div class="interp-content"><!-- INTERPRETATION:winners --></div></details></div>
    </div>'''

    # Heatmap
    funnels_order = ["TOF", "MOF", "BOF"]
    angles_sorted = sorted(a["cross_af"].keys(), key=lambda x: -sum(a["cross_af"][x][f]["spend"] for f in funnels_order))
    heatmap = '<div class="card"><div class="card-header"><span class="card-icon">🔥</span><h3>Angle × Funnel Heatmap</h3></div>'
    heatmap += '<table class="heatmap"><thead><tr><th>Angle</th>'
    for f in funnels_order: heatmap += f'<th>{f}</th>'
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
        video_html += f'''<div class="video-summary">
            <div class="metric-box"><div class="metric-value">{a["avg_thumbstop"]:.1f}%</div><div class="metric-label">Avg Thumbstop*</div><div class="metric-bench">*video_play_actions — relative only</div></div>
            <div class="metric-box"><div class="metric-value" style="color:{score_color(min(100, a["avg_hold"]/25*100))}">{a["avg_hold"]:.1f}%</div><div class="metric-label">Avg Hold Rate</div><div class="metric-bench">ThruPlay / 3-sec views</div></div>
            <div class="metric-box"><div class="metric-value">{len(a["video_ads"])}</div><div class="metric-label">Video Ads</div><div class="metric-bench">{pct(a["video_spend"], a["total_spend"])}% of spend</div></div>
            <div class="metric-box"><div class="metric-value">{vid_metric}</div><div class="metric-label">Video {metric_label}</div><div class="metric-bench">vs {acct_metric} account avg</div></div>
        </div>
        <h4>Top Videos by Spend</h4>
        <table class="data-table"><thead><tr><th>Ad</th><th>Spend</th><th>Thumbstop*</th><th>Hold</th><th>{metric_label}</th><th>Duration</th></tr></thead><tbody>'''
        for v in sorted(a["video_ads"], key=lambda x: -x["spend"])[:10]:
            ns = v["name"][:55] + "..." if len(v["name"]) > 55 else v["name"]
            dur = f'{v["video_duration"]:.0f}s' if v["video_duration"] > 0 else "—"
            if a["primary_metric"] == "cpa":
                perf = fmt_cpa(v["cpa"])
            else:
                perf = fmt_roas(v["roas"])
            video_html += f'<tr><td class="name-cell" title="{v["name"]}">{ns}</td><td>{fmt_money(v["spend"])}</td><td>{v["thumbstop_rate"]:.1f}%</td><td>{v["hold_rate"]:.1f}%</td><td>{perf}</td><td>{dur}</td></tr>'
        video_html += '</tbody></table>'
    else:
        video_html += '<p class="muted">No video data available.</p>'
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
<style>
:root {{ --bg:#f8fafc; --card:#fff; --border:#e2e8f0; --text:#1e293b; --muted:#64748b; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }}
.container {{ max-width:1200px; margin:0 auto; padding:24px; }}
.header {{ text-align:center; padding:40px 0 32px; }}
.header h1 {{ font-size:28px; font-weight:700; }}
.header .subtitle {{ color:var(--muted); font-size:14px; }}
.kpi-strip {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:12px; margin-bottom:24px; }}
.kpi {{ background:var(--card); border:1px solid var(--border); border-radius:10px; padding:16px; text-align:center; }}
.kpi .kpi-value {{ font-size:22px; font-weight:700; }}
.kpi .kpi-label {{ font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; margin-top:2px; }}
.score-section {{ display:flex; gap:32px; align-items:flex-start; background:var(--card); border:1px solid var(--border); border-radius:12px; padding:28px; margin-bottom:24px; flex-wrap:wrap; }}
.score-ring {{ text-align:center; flex-shrink:0; }}
.score-label {{ font-size:16px; font-weight:600; margin-top:4px; }}
.sub-scores {{ flex:1; min-width:300px; }}
.sub-scores h3 {{ margin-bottom:12px; font-size:16px; }}
.sub-score {{ display:flex; align-items:center; gap:10px; margin-bottom:8px; }}
.sub-label {{ width:180px; font-size:13px; flex-shrink:0; }}
.sub-label .weight {{ color:var(--muted); }}
.sub-track {{ flex:1; height:8px; background:#e5e7eb; border-radius:4px; overflow:hidden; }}
.sub-fill {{ height:100%; border-radius:4px; }}
.sub-value {{ width:36px; text-align:right; font-weight:600; font-size:13px; }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:24px; margin-bottom:20px; }}
.card-header {{ display:flex; align-items:center; gap:10px; margin-bottom:16px; flex-wrap:wrap; }}
.card-header h3 {{ font-size:17px; font-weight:600; }}
.card-icon {{ font-size:20px; }}
.badge {{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }}
.dimension-bars {{ display:flex; flex-direction:column; gap:10px; }}
.bar-row {{ display:flex; align-items:center; gap:10px; }}
.bar-label {{ width:140px; font-size:13px; font-weight:500; flex-shrink:0; }}
.bar-track {{ flex:1; height:24px; background:#f1f5f9; border-radius:6px; overflow:hidden; }}
.bar-fill {{ height:100%; border-radius:6px; display:flex; align-items:center; padding:0 8px; color:white; font-size:11px; font-weight:600; min-width:40px; }}
.bar-meta {{ font-size:11px; color:var(--muted); width:240px; text-align:right; flex-shrink:0; }}
.video-summary,.compliance-grid,.winner-grid,.volume-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:16px; margin-bottom:20px; }}
.metric-box {{ text-align:center; padding:16px; background:#f8fafc; border-radius:8px; }}
.metric-value {{ font-size:24px; font-weight:700; }}
.metric-label {{ font-size:12px; color:var(--muted); margin-top:2px; }}
.metric-bench {{ font-size:10px; color:var(--muted); margin-top:2px; }}
.data-table {{ width:100%; border-collapse:collapse; font-size:12px; }}
.data-table th {{ background:#f8fafc; padding:8px 10px; text-align:left; font-weight:600; border-bottom:2px solid var(--border); font-size:11px; text-transform:uppercase; letter-spacing:.3px; }}
.data-table td {{ padding:8px 10px; border-bottom:1px solid var(--border); }}
.data-table tr:hover {{ background:#f8fafc; }}
.name-cell {{ max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-family:'SF Mono',monospace; font-size:11px; }}
.heatmap {{ width:100%; border-collapse:collapse; font-size:12px; }}
.heatmap th {{ background:#f8fafc; padding:10px; text-align:center; font-weight:600; border-bottom:2px solid var(--border); }}
.heatmap td {{ padding:10px; text-align:center; border-bottom:1px solid var(--border); }}
.heatmap .angle-cell {{ text-align:left; font-weight:500; }}
.heatmap .empty-cell {{ color:#cbd5e1; }}
.heatmap .total-cell {{ background:#f8fafc; font-weight:600; }}
.interpretation {{ margin-top:16px; }}
.interp-toggle {{ cursor:pointer; font-size:13px; font-weight:600; color:#3b82f6; padding:8px 0; list-style:none; }}
.interp-toggle::-webkit-details-marker {{ display:none; }}
.interp-toggle::before {{ content:"▶ "; font-size:10px; }}
details[open] .interp-toggle::before {{ content:"▼ "; }}
.interp-content {{ padding:16px; background:#f0f9ff; border-radius:8px; margin-top:8px; font-size:13px; line-height:1.7; }}
.interp-content p {{ margin-bottom:10px; }}
.interp-content strong {{ color:#1e40af; }}
.iteration-card {{ background:#fefce8; border:1px solid #fde68a; border-radius:10px; padding:20px; margin-bottom:16px; }}
.iteration-card h4 {{ font-size:14px; margin-bottom:8px; }}
.iteration-card .script-section {{ font-size:13px; margin-bottom:6px; }}
.iteration-card .script-label {{ font-weight:600; color:#92400e; display:inline-block; width:80px; }}
.iteration-card .script-meta {{ display:flex; gap:8px; margin-top:10px; flex-wrap:wrap; }}
.iteration-card .meta-tag {{ background:#fef3c7; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:500; }}
.muted {{ color:var(--muted); }}
h4 {{ font-size:14px; margin:16px 0 10px; }}
.section-title {{ font-size:20px; font-weight:700; margin:32px 0 16px; padding-top:16px; border-top:2px solid var(--border); }}
.unstructured-list {{ list-style:none; padding:0; }}
.unstructured-list li {{ padding:6px 0; border-bottom:1px solid var(--border); font-size:12px; font-family:'SF Mono',monospace; }}
.footer {{ text-align:center; padding:32px 0; color:var(--muted); font-size:12px; }}
@media (max-width:768px) {{ .bar-meta {{ display:none; }} .score-section {{ flex-direction:column; align-items:center; }} }}
</style>
</head>
<body>
<div class="container">
<div class="header">
    <h1>Creative Health Report</h1>
    <div class="subtitle">{client_name} · {account_id} · Last {days} days {("· " + target_str) if target_str else ""}</div>
</div>

<div class="kpi-strip">
    <div class="kpi"><div class="kpi-value">{len(ads)}</div><div class="kpi-label">Active Ads</div></div>
    <div class="kpi"><div class="kpi-value">{fmt_money(a["total_spend"])}</div><div class="kpi-label">Total Spend</div></div>
    <div class="kpi"><div class="kpi-value">{a["total_purchases"]:.0f}</div><div class="kpi-label">Purchases</div></div>
    {metric_kpi}
    <div class="kpi"><div class="kpi-value">{a["hit_rate"]:.1f}%</div><div class="kpi-label">Hit Rate</div></div>
    <div class="kpi"><div class="kpi-value">{len(a["video_ads"])}</div><div class="kpi-label">Video Ads</div></div>
</div>

<div class="score-section">
    {score_ring}
    <div class="sub-scores">
        <h3>Creative Health Breakdown</h3>
        {sub_bars}
    </div>
</div>

<h2 class="section-title">Creative Volume & Concentration</h2>
{volume_html}
{winner_html}

<h2 class="section-title">Dimension Analysis</h2>
{dim_card("Funnel Stage", a["dim_funnel"], "🎯", "funnel")}
{dim_card("Angle / Message Territory", a["dim_angle"], "💬", "angle")}
{dim_card("Media Type", a["dim_media"], "🖼️", "media")}

<h2 class="section-title">Cross-Dimensional</h2>
{heatmap}

<h2 class="section-title">Video Performance</h2>
{video_html}

<h2 class="section-title">Identity Analysis</h2>
{identity_html}

<h2 class="section-title">Efficiency</h2>
{dead_html}

<h2 class="section-title">Iteration Scripts</h2>
{iterations_html}

<h2 class="section-title">Ad-Level Detail</h2>
{top_html}

<h2 class="section-title">Naming Compliance</h2>
{comp_html}

<div class="footer">Generated {datetime.now().strftime("%Y-%m-%d %H:%M")} · Creative Health Report v2.0 · LWU</div>
</div>
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
        "winners": len(a["winners"]), "hit_rate": round(a["hit_rate"], 1),
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
    parser.add_argument("--output", default="creative-health-report.html", help="Output HTML path")
    args = parser.parse_args()

    print(f"Loading data from {args.input}...")
    ads = load_csv(args.input)
    print(f"Loaded {len(ads)} ads")

    print(f"Running analysis (primary metric: {args.metric.upper()}, target: {args.target})...")
    analysis = run_analysis(ads, primary_metric=args.metric, metric_target=args.target)

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
