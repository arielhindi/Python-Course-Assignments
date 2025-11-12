"""Conversion and parsing logic for baking conversions.

Pure functions that operate on numbers and strings. This module depends only on
the `ingredients` module to read/write ingredient data.
"""

from __future__ import annotations

from typing import Dict

import ingredients

# Optional Pint integration (if installed). Pint can help with parsing units
# and performing reliable unit arithmetic. We use it only when available and
# still fall back to simple factors otherwise.
try:
    import pint

    _HAS_PINT = True
    _REGISTRY = pint.UnitRegistry()
except Exception:
    _HAS_PINT = False
    _REGISTRY = None


UNIT_ALIASES = {
    "g": "g",
    "gram": "g",
    "grams": "g",
    "cup": "cup",
    "cups": "cup",
    "c": "cup",
    "tbsp": "tbsp",
    "tbs": "tbsp",
    "tablespoon": "tbsp",
    "tablespoons": "tbsp",
    "tsp": "tsp",
    "teaspoon": "tsp",
    "teaspoons": "tsp",
}


def normalize_unit(u: str) -> str | None:
    if not u:
        return None
    key = u.strip().lower()
    # If Pint is available, try to parse some common unit strings robustly.
    if _HAS_PINT:
        # Accept things like 'tablespoon', 'tbsp', 'tbs', etc. Map to our short names.
        try:
            q = _REGISTRY.parse_expression(key)
            # get the dimensionality: we only accept volume or mass here
            # Map common pint units to our short names
            if "teaspoon" in key or key.startswith("tsp"):
                return "tsp"
            if "tablespoon" in key or key.startswith("tbsp") or key.startswith("tbs"):
                return "tbsp"
            if "cup" in key:
                return "cup"
            if key in ("g", "gram", "grams", "gramme"):
                return "g"
        except Exception:
            pass
    return UNIT_ALIASES.get(key)


def parse_amount(s: str) -> float:
    s = (s or "").strip()
    if not s:
        raise ValueError("empty amount")
    # allow simple fractions like '1/2'
    if "/" in s and not any(c.isalpha() for c in s):
        parts = s.split("/")
        if len(parts) == 2:
            num, den = parts
            return float(num) / float(den)
    return float(s)


def convert_to_grams(amount: float, unit: str, grams_per_cup: float) -> float:
    if unit == "cup":
        cups = amount
    elif unit == "tbsp":
        cups = amount / 16.0
    elif unit == "tsp":
        cups = amount / 48.0
    else:
        raise ValueError(f"Unsupported unit for conversion to grams: {unit}")
    return cups * grams_per_cup


def convert_from_grams(grams: float, grams_per_cup: float) -> Dict[str, float]:
    cups = grams / grams_per_cup
    tbsp = cups * 16.0
    tsp = cups * 48.0
    return {"cup": cups, "tbsp": tbsp, "tsp": tsp}


def get_or_ask_grams_per_cup(ingredient: str) -> float | None:
    """Return grams_per_cup if known, otherwise None.

    The caller (GUI or CLI) can then decide to prompt the user to add it.
    """
    return ingredients.get_grams_per_cup(ingredient)


def add_ingredient_permanently(ingredient: str, grams_per_cup: float) -> None:
    ingredients.add_custom_ingredient(ingredient, grams_per_cup)
