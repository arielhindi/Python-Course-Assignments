# Baking Conversions (day03 assignment)

This folder contains a small Python project that provides
conversions between grams and common kitchen volume units (cups, tablespoons, teaspoons)
for common baking ingredients. It includes:

- a GUI application (`baking_conversions_gui.py`) using Tkinter
- pure business logic (`business_logic.py`) with parsing and conversion functions
- ingredient data and persistence (`ingredients.py`) with a JSON-backed custom list
- pytest tests for logic and persistence (`test_business_logic.py`, `test_ingredients.py`)

Short summary
-------------
The GUI lets you enter an ingredient, an amount, and a unit (g / cup / tbsp / tsp).
If the ingredient is not known, the GUI will offer to add it permanently (saved in
`custom_ingredients.json` in this folder). The conversion math uses grams-per-cup
values (stored for each ingredient) and converts between grams and cup/tbsp/tsp using
simple kitchen factors (1 cup = 16 tbsp = 48 tsp).

Files
-----
- `baking_conversions_gui.py` — GUI front-end only (Tkinter). Reads/writes ingredients via `ingredients.py` and calls `business_logic.py` for conversions.
- `business_logic.py` — parsing, unit normalization, convert_to_grams, convert_from_grams. Optional Pint support is present if Pint is installed.
- `ingredients.py` — built-in mapping + JSON persistence for custom ingredients. You can override the location of the custom JSON by setting the `CUSTOM_INGREDIENTS_PATH` environment variable.
- `custom_ingredients.json` — persistent store (initially `{}`).
- `test_business_logic.py`, `test_ingredients.py` — pytest tests.

How to run
----------
1) (Optional) create and activate a virtualenv (recommended):

```bash
# macOS / zsh example
python3 -m venv .venv
source .venv/bin/activate
```

2) Install the optional dependencies used by the project (Pint is optional but recommended for robust unit handling; pytest is used for tests):

```bash
pip install pytest
# optional: pint for improved unit parsing
pip install pint
```

3) Run the GUI:

```bash
python3 day03/baking_conversions_gui.py
```

4) Run tests:

```bash
pytest day03 -q
```

Notes on persistence and testing
-------------------------------
- Custom ingredients are saved in `day03/custom_ingredients.json` by default.
- Tests use a temporary file by setting the environment variable `CUSTOM_INGREDIENTS_PATH`
  so running tests will not overwrite your default JSON file.

Optional third-party library
----------------------------
- Pint (https://pint.readthedocs.io) is supported optionally. If installed, the
  business logic attempts to use Pint for more robust unit parsing. The code
  still works without it.

Developer / provenance
----------------------
This code (all files in this folder) was generated programmatically by GPT-5 mini. 

Prompts:
1)
"in the day03 folder: seperate the file \"baking_conversions_gui.py\" into 3 files, the main one containing only the gui elements of the code, a second called buissnes logic containing the function part, and a third which has the list of the ingredients and conversions. a couple upgrades i want you to implement: 1. create another file in the day03 folder which will use pytest to ensure the code works. 2. if possible, search for a 3rd party library which can help with the code. 3. anytime a user asks for a conversion of an ingredient that doesnt exist in the list, ask if they would like to add that ingredient and its conversion ratio permanantly to the ingredient list."

2)
"i added pytest to my enviornment - try running it now. i would like you to implement all the next steps you recommended"

3)
"open a readme file in the day03 folder with explanations on what the main code is for, and how to run the gui code. include the dependencies and a short guide on how to install them. explain that this code was completely written by GPT-5 mini and include the prompts i used."



