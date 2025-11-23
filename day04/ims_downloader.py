"""Downloader and basic parser for Israeli Meteorological Service (IMS) data.

This module provides functions to download IMS pages (or API endpoints, if
available) and save raw responses to disk under `day04/data/`. It also exposes
very small parsing helpers that attempt to extract simple fields (cloud cover,
precipitation chance) from the saved HTML/JSON. The IMS site structure can
change, so parsing may need to be adjusted later.

Notes:
- This code uses `requests` to fetch pages and `bs4` (BeautifulSoup) to parse
  HTML. Install with: `pip install requests beautifulsoup4`.
- The downloader saves raw responses so you can inspect them and adjust the
  parser manually.
"""

from __future__ import annotations

import datetime
import os
from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)


def _filename_for(date: datetime.date, location: str) -> str:
    safe_loc = location.strip().lower().replace(" ", "_")
    return os.path.join(DATA_DIR, f"ims_{date.isoformat()}_{safe_loc}.html")


def download_forecast(date: datetime.date, location: str = "Tel Aviv") -> str:
    """Download IMS content for the given date and location and save to disk.

    Returns the path to the saved file. This function currently fetches the
    IMS front page (or a location-specific page if you update the URL below).
    You may need to adjust the URL to the correct IMS endpoint for forecasts.
    """
    # NOTE: IMS site structure/API may vary; change this URL to the proper
    # endpoint for a location/date forecast when known.
    base_url = "https://ims.gov.il/en"  # placeholder; refine for detailed data

    # Example: if IMS provides a location-specific URL format, construct it here.
    params = {"q": location}
    resp = requests.get(base_url, params=params, timeout=20)
    resp.raise_for_status()

    path = _filename_for(date, location)
    with open(path, "wb") as f:
        f.write(resp.content)
    return path


def load_saved_forecast(path: str) -> str:
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace")


def parse_cloudiness_and_precip(html: str) -> Dict[str, Optional[float]]:
    """Try to extract cloudiness (%) and precipitation chance (%) from HTML.

    Returns dict: { "cloudiness": float|None, "precip_prob": float|None }

    This is a very small heuristic parser. Inspect the saved HTML files in
    `day04/data/` and update this function to match actual IMS content.
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")

    result = {"cloudiness": None, "precip_prob": None}

    # heuristics: look for phrases like "Cloud cover: 30%" or "Clouds 30%"
    import re

    m = re.search(r"[Cc]loud(?:s| cover)?[:\s]*([0-9]{1,3})\s*%", text)
    if m:
        try:
            result["cloudiness"] = float(m.group(1))
        except Exception:
            pass

    m2 = re.search(r"[Pp]recip(?:itation|\.)?[:\s]*([0-9]{1,3})\s*%", text)
    if m2:
        try:
            result["precip_prob"] = float(m2.group(1))
        except Exception:
            pass

    # fallback: look for "Rain: 20%" or "Prob of rain 20%"
    m3 = re.search(r"[Rr]ain[:\s]*([0-9]{1,3})\s*%", text)
    if m3 and result["precip_prob"] is None:
        try:
            result["precip_prob"] = float(m3.group(1))
        except Exception:
            pass

    return result


if __name__ == "__main__":
    # small demo when run directly
    today = datetime.date.today()
    try:
        path = download_forecast(today, "Tel Aviv")
        print("Saved to:", path)
        html = load_saved_forecast(path)
        print(parse_cloudiness_and_precip(html))
    except Exception as e:
        print("Download/parse failed:", e)
