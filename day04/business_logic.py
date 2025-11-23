"""Business logic for stargazing suitability evaluation.

This module provides functions to compute a stargazing "score" and a
recommendation based on weather data (cloudiness, precipitation probability),
moon phase, and meteor shower activity.

Functions are deliberately pure and easy to test. Confidence is estimated
heuristically based on how far in the future the requested date is.
"""

from __future__ import annotations

import datetime
from typing import Dict, Tuple

import math

from day04 import ims_downloader


def moon_phase_fraction(date: datetime.date) -> float:
    """Return the moon phase as a fraction: 0=new, 0.5=full, 1=next new.

    Uses a simple algorithm (approximate). 0..1 where 0 or 1 means new moon,
    0.5 means full moon.
    """
    # Simple approximation from Conway's algorithm
    year = date.year
    month = date.month
    day = date.day
    if month < 3:
        year -= 1
        month += 12
    a = int(year / 100)
    b = int(a / 4)
    c = 2 - a + b
    e = int(365.25 * (year + 4716))
    f = int(30.6001 * (month + 1))
    jd = c + day + e + f - 1524.5
    # Known new moon reference (2000-01-06 18:14 UT) JD ~ 2451550.1
    days_since_new = jd - 2451550.1
    synodic_month = 29.53058867
    phase = (days_since_new % synodic_month) / synodic_month
    return float(phase)


METEOR_SHOWERS = {
    # approximate peak dates (month, day) and relative activity multiplier
    (1, 4): ("Quadrantids", 0.8),
    (4, 22): ("Lyrids", 0.6),
    (8, 12): ("Perseids", 1.0),
    (10, 21): ("Orionids", 0.5),
    (12, 14): ("Geminids", 1.0),
}


def meteor_shower_activity(date: datetime.date) -> Tuple[str | None, float]:
    """Return a tuple (shower_name or None, intensity 0..1) for the date.

    We score based on proximity to known peaks: closer to peak gives higher
    intensity. This is approximate but useful for recommending favorable
    stargazing dates.
    """
    best_name = None
    best_intensity = 0.0
    for (m, d), (name, multiplier) in METEOR_SHOWERS.items():
        peak = datetime.date(date.year, m, d)
        days = abs((date - peak).days)
        # activity decreases with distance; assume +/- 7 days window
        if days <= 7:
            intensity = multiplier * (1 - days / 8.0)
            if intensity > best_intensity:
                best_intensity = intensity
                best_name = name
    return best_name, float(best_intensity)


def visibility_score(cloudiness: float | None, precip_prob: float | None, phase_frac: float, meteor_intensity: float) -> float:
    """Compute a 0..100 visibility score where higher is better for stargazing.

    - cloudiness: percent 0..100 (None -> treated as 50)
    - precip_prob: percent 0..100 (None -> 0)
    - phase_frac: 0..1 (0 new, 0.5 full; we reduce score near full moon)
    - meteor_intensity: 0..1 (adds small bonus when strong showers)
    """
    c = 50.0 if cloudiness is None else float(cloudiness)
    p = 0.0 if precip_prob is None else float(precip_prob)

    # base from cloudiness: more clouds => lower score
    base = max(0.0, 100.0 - c)

    # precipitation penalty
    base -= p * 0.8

    # moon penalty: compute distance from full moon
    moon_dist = abs(phase_frac - 0.5)
    moon_penalty = max(0.0, (0.5 - moon_dist) * 40.0)  # up to -20 when near full
    base -= moon_penalty

    # meteor shower bonus (small)
    base += meteor_intensity * 12.0

    # clamp
    score = max(0.0, min(100.0, base))
    return float(score)


def confidence_for_date(requested: datetime.date, forecast_provided_date: datetime.date) -> float:
    """Estimate confidence 0..1 based on forecast horizon.

    For example, forecasts for same-day to 3 days ahead are more reliable.
    """
    days = (requested - forecast_provided_date).days
    if days <= 0:
        return 0.9
    if days <= 3:
        return 0.75
    if days <= 7:
        return 0.5
    return 0.25


def analyze_date(date: datetime.date, location: str = "Tel Aviv") -> Dict[str, object]:
    """High-level analysis: download (or load) forecast, parse, and compute recommendations.

    Returns a dictionary with fields:
      - score: 0..100
      - confidence: 0..1
      - cloudiness, precip_prob, moon_phase_frac, meteor_shower, meteor_intensity
      - recommendation: string (if bad, a suggested alternate date)
    """
    # load downloaded data if exists, otherwise download
    import os

    path = os.path.join(os.path.dirname(__file__), "data", f"ims_{date.isoformat()}_{location.strip().lower().replace(' ','_')}.html")
    used_html_scraping = False
    if os.path.exists(path):
        html = ims_downloader.load_saved_forecast(path)
        parsed = ims_downloader.parse_cloudiness_and_precip(html)
        forecast_date = datetime.date.today()  # assume forecast provided today
        used_html_scraping = True
    else:
        try:
            path = ims_downloader.download_forecast(date, location)
            html = ims_downloader.load_saved_forecast(path)
            parsed = ims_downloader.parse_cloudiness_and_precip(html)
            forecast_date = datetime.date.today()
            used_html_scraping = True
        except Exception:
            # if download failed, fall back to unknowns
            parsed = {"cloudiness": None, "precip_prob": None}
            forecast_date = datetime.date.today()
            used_html_scraping = True

    phase = moon_phase_fraction(date)
    shower_name, meteor_intensity = meteor_shower_activity(date)
    score = visibility_score(parsed.get("cloudiness"), parsed.get("precip_prob"), phase, meteor_intensity)
    conf = confidence_for_date(date, forecast_date)

    recommendation = None
    if score < 35.0:
        # recommend next nearby good date within next 14 days
        best_date = None
        best_score = -1.0
        for delta in range(1, 15):
            d = date + datetime.timedelta(days=delta)
            # try to load (or download) forecast for d if available; else use heuristics
            p = {}  # try to load
            path_d = os.path.join(os.path.dirname(__file__), "data", f"ims_{d.isoformat()}_{location.strip().lower().replace(' ','_')}.html")
            if os.path.exists(path_d):
                html_d = ims_downloader.load_saved_forecast(path_d)
                p = ims_downloader.parse_cloudiness_and_precip(html_d)
            else:
                p = {"cloudiness": None, "precip_prob": None}
            ph = moon_phase_fraction(d)
            _, mi = meteor_shower_activity(d)
            sc = visibility_score(p.get("cloudiness"), p.get("precip_prob"), ph, mi)
            if sc > best_score:
                best_score = sc
                best_date = d
        if best_date is not None:
            recommendation = {"date": best_date.isoformat(), "score": best_score}

    reliability_msg = "Forecast data was scraped from the public IMS website. This is less reliable than official API data and may be incomplete or outdated."
    return {
        "score": score,
        "confidence": conf,
        "cloudiness": parsed.get("cloudiness"),
        "precip_prob": parsed.get("precip_prob"),
        "moon_phase_frac": phase,
        "meteor_shower": shower_name,
        "meteor_intensity": meteor_intensity,
        "recommendation": recommendation,
        "data_source": "html_scraping" if used_html_scraping else "api",
        "reliability_msg": reliability_msg if used_html_scraping else "Forecast data is from the official IMS API.",
    }


if __name__ == "__main__":
    # quick demo
    today = datetime.date.today()
    out = analyze_date(today)
    import pprint

    pprint.pprint(out)
