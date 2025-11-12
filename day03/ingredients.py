"""Ingredient data and persistence for baking conversions.

Provides a built-in mapping plus optional persistent custom entries stored in
`custom_ingredients.json` in the same directory.
"""

from __future__ import annotations

import json
import os
from typing import Dict


DEFAULT_GRAMS_PER_CUP: Dict[str, float] = {
    "all-purpose flour": 125.0,
    "flour": 125.0,
    "plain flour": 125.0,
    "granulated sugar": 200.0,
    "sugar": 200.0,
    "brown sugar (packed)": 220.0,
    "brown sugar": 220.0,
    "powdered sugar": 120.0,
    "butter": 227.0,
    "unsalted butter": 227.0,
    "salted butter": 227.0,
    "cocoa powder": 85.0,
    "honey": 340.0,
    "milk": 240.0,
    "water": 240.0,
}


def _custom_file_path() -> str:
    # Allow tests or users to override the custom file location via env var.
    env = os.environ.get("CUSTOM_INGREDIENTS_PATH")
    if env:
        return env
    return os.path.join(os.path.dirname(__file__), "custom_ingredients.json")


def load_custom() -> Dict[str, float]:
    path = _custom_file_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {k.lower(): float(v) for k, v in data.items()}
    except FileNotFoundError:
        return {}
    except Exception:
        # If file is corrupt, ignore and return empty custom set
        return {}


def save_custom(custom: Dict[str, float]) -> None:
    path = _custom_file_path()
    # write atomically
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(custom, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def get_all_ingredients() -> Dict[str, float]:
    combined = {k.lower(): v for k, v in DEFAULT_GRAMS_PER_CUP.items()}
    custom = load_custom()
    combined.update(custom)
    return combined


def get_grams_per_cup(ingredient: str) -> float | None:
    key = ingredient.strip().lower()
    return get_all_ingredients().get(key)


def add_custom_ingredient(ingredient: str, grams_per_cup: float) -> None:
    if grams_per_cup <= 0:
        raise ValueError("grams_per_cup must be positive")
    key = ingredient.strip().lower()
    custom = load_custom()
    custom[key] = grams_per_cup
    save_custom(custom)
