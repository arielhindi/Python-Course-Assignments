"""Command-line interface for baking conversions.

Usage examples:
  python3 day02/baking_conversions_command_line.py flour 100 g
  python3 day02/baking_conversions_command_line.py "brown sugar" 1 cup
  python3 day02/baking_conversions_command_line.py --list

If an ingredient isn't known, provide --grams-per-cup (or -p) to supply it non-interactively.
"""

from __future__ import annotations

import argparse
import os
import sys
import importlib.util
from typing import Dict


def load_interactive_module() -> object:
    # Load the interactive script as a module so we can reuse mappings & functions
    this_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(this_dir, "baking_conversions.py")
    spec = importlib.util.spec_from_file_location("baking_conversions", path)
    if spec is None or spec.loader is None:
        raise ImportError("Could not load baking_conversions.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[arg-type]
    return module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Baking ingredient conversions (grams <-> cups/tbsp/tsp)")
    parser.add_argument("ingredient", nargs="?", help="Ingredient name (e.g. flour, sugar)")
    parser.add_argument("amount", nargs="?", help="Amount to convert (number or simple fraction like 1/2)")
    parser.add_argument("unit", nargs="?", help="Unit of amount (g, cup, tbsp, tsp)")
    parser.add_argument("-p", "--grams-per-cup", type=float, help="Provide grams per 1 cup for unknown ingredient")
    parser.add_argument("--list", action="store_true", help="List built-in known ingredients")

    args = parser.parse_args(argv)

    module = load_interactive_module()
    grams_map: Dict[str, float] = {k.lower(): v for k, v in module.DEFAULT_GRAMS_PER_CUP.items()}

    if args.list:
        print("Known ingredients (built-in):")
        for name in sorted(set(grams_map.keys())):
            print(f"  {name} — {grams_map[name]} g/cup")
        return 0

    if not (args.ingredient and args.amount and args.unit):
        parser.print_help()
        return 2

    ingredient = args.ingredient.strip()
    try:
        amount = module.parse_amount(args.amount)
    except Exception:
        print("Couldn't parse amount. Use a number like 100 or a simple fraction like 1/2.")
        return 2

    unit = module.normalize_unit(args.unit)
    if unit is None:
        print("Unknown unit. Allowed: g, grams, cup(s), tbsp/tbs, tsp")
        return 2

    if amount <= 0:
        print("Amount must be positive.")
        return 2

    key = ingredient.lower()
    grams_per_cup = grams_map.get(key)
    if grams_per_cup is None:
        if args.grams_per_cup is not None:
            grams_per_cup = args.grams_per_cup
        else:
            print(f"Unknown ingredient '{ingredient}'. Provide --grams-per-cup to convert non-interactively.")
            return 3

    if unit == "g":
        grams = amount
        conv = module.convert_from_grams(grams, grams_per_cup)
        print(f"{grams:.2f} g of {ingredient} is approximately:")
        print(f"  {conv['cup']:.3f} cup(s)")
        print(f"  {conv['tbsp']:.2f} tablespoon(s)")
        print(f"  {conv['tsp']:.1f} teaspoon(s)")
    else:
        grams = module.convert_to_grams(amount, unit, grams_per_cup)
        friendly = unit
        if unit == "tbsp":
            friendly = "tablespoon(s)"
        elif unit == "tsp":
            friendly = "teaspoon(s)"
        elif unit == "cup":
            friendly = "cup(s)"
        print(f"{amount} {friendly} of {ingredient} is approximately {grams:.2f} g")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.")
        raise SystemExit(1)
