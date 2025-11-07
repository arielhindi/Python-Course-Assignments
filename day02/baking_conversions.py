
"""Interactive baking ingredient conversion helper.

Asks for:
 - ingredient (e.g. "all-purpose flour" or "flour")
 - amount (number)
 - unit (g or cups/tbs/tsp aliases)

Then prints the amount in the opposite unit(s).

If an ingredient isn't in the built-in mapping, the script will ask the user
to provide grams-per-cup for that ingredient so it can perform the conversion.
"""

from __future__ import annotations

import sys
from typing import Dict


DEFAULT_GRAMS_PER_CUP: Dict[str, float] = {
	# Common baking conversions (grams per 1 US cup)
	"all-purpose flour": 125.0,
	"flour": 125.0,
	"plain flour": 125.0,
	"granulated sugar": 200.0,
	"sugar": 200.0,
	"brown sugar (packed)": 220.0,
	"brown sugar": 220.0,
	"powdered sugar": 120.0,  # confectioners'
	"butter": 227.0,
	"unsalted butter": 227.0,
	"salted butter": 227.0,
	"cocoa powder": 85.0,
	"honey": 340.0,
	"milk": 240.0,
	"water": 240.0,
}


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
	key = u.strip().lower()
	return UNIT_ALIASES.get(key)


def get_grams_per_cup_for(ingredient: str, mapping: Dict[str, float]) -> float:
	key = ingredient.strip().lower()
	if key in mapping:
		return mapping[key]

	# Not found: ask user to provide grams-per-cup so we can proceed.
	while True:
		try:
			val = input(f"I don't have '{ingredient}'. Enter grams per 1 cup for this ingredient: ").strip()
			grams_per_cup = float(val)
			if grams_per_cup <= 0:
				print("Please enter a positive number.")
				continue
			# store in mapping for this run
			mapping[key] = grams_per_cup
			return grams_per_cup
		except ValueError:
			print("That's not a valid number. Try again.")


def convert_to_grams(amount: float, unit: str, grams_per_cup: float) -> float:
	# unit is normalized to one of: 'cup', 'tbsp', 'tsp'
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


def parse_amount(s: str) -> float:
	s = s.strip()
	# allow simple fractions like '1/2'
	if "/" in s and not any(c.isalpha() for c in s):
		try:
			num, den = s.split("/")
			return float(num) / float(den)
		except Exception:
			pass
	return float(s)


def main() -> None:
	print("Baking ingredient converter — convert between grams and cups/tbs/tsp")

	ingredient = input("Ingredient (e.g. 'flour', 'sugar', 'butter'): ").strip()
	if not ingredient:
		print("Ingredient cannot be empty. Exiting.")
		return

	amount_str = input("Amount to convert (number, e.g. 100 or 1/2): ").strip()
	try:
		amount = parse_amount(amount_str)
	except Exception:
		print("Couldn't understand the amount. Please use a number like 100 or fraction like 1/2.")
		return

	unit_str = input("Unit (g or cups/tbs/tsp): ").strip()
	unit = normalize_unit(unit_str or "")
	if unit is None:
		print("Unknown unit. Allowed: g, grams, cup(s), tbsp/tbs, tsp")
		return

	if amount <= 0:
		print("Amount must be positive.")
		return

	# Prepare mapping copy to allow user-provided values during runtime
	grams_map = {k.lower(): v for k, v in DEFAULT_GRAMS_PER_CUP.items()}

	if unit == "g":
		grams = amount
		grams_per_cup = get_grams_per_cup_for(ingredient, grams_map)
		conv = convert_from_grams(grams, grams_per_cup)
		print(f"\n{grams:.2f} g of {ingredient} is approximately:")
		print(f"  {conv['cup']:.3f} cup(s)")
		print(f"  {conv['tbsp']:.2f} tablespoon(s)")
		print(f"  {conv['tsp']:.1f} teaspoon(s)")
	else:
		grams_per_cup = get_grams_per_cup_for(ingredient, grams_map)
		grams = convert_to_grams(amount, unit, grams_per_cup)
		# Determine a friendly unit name for output
		friendly = unit
		if unit == "tbsp":
			friendly = "tablespoon(s)"
		elif unit == "tsp":
			friendly = "teaspoon(s)"
		elif unit == "cup":
			friendly = "cup(s)"

		print(f"\n{amount} {friendly} of {ingredient} is approximately {grams:.2f} g")


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("\nInterrupted by user.")
		sys.exit(1)
