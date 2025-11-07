"""Simple Tkinter GUI for baking conversions.

Reuses conversion functions from `baking_conversions.py` in the same folder.

Fields:
 - Ingredient (text)
 - Amount (number or simple fraction like 1/2)
 - Unit (g, cup, tbsp, tsp)
 - Optional grams-per-cup field to provide value for unknown ingredients

Click Convert to show results. Click "List known" to see built-in ingredients.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict


def load_conversion_module():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "baking_conversions.py")
    spec = importlib.util.spec_from_file_location("baking_conversions", path)
    if spec is None or spec.loader is None:
        raise ImportError("Could not load baking_conversions.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[arg-type]
    return mod


class BakingConverterGUI(tk.Tk):
    def __init__(self, conv_module) -> None:
        super().__init__()
        self.title("Baking Conversions")
        self.conv = conv_module
        self.grams_map: Dict[str, float] = {k.lower(): v for k, v in self.conv.DEFAULT_GRAMS_PER_CUP.items()}

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # Ingredient
        ttk.Label(frm, text="Ingredient:").grid(row=0, column=0, sticky="w")
        self.ing_entry = ttk.Entry(frm, width=30)
        self.ing_entry.grid(row=0, column=1, columnspan=2, sticky="ew")

        # Amount
        ttk.Label(frm, text="Amount:").grid(row=1, column=0, sticky="w")
        self.amount_entry = ttk.Entry(frm, width=12)
        self.amount_entry.grid(row=1, column=1, sticky="w")

        # Unit
        ttk.Label(frm, text="Unit:").grid(row=1, column=2, sticky="w")
        self.unit_var = tk.StringVar(value="g")
        unit_menu = ttk.OptionMenu(frm, self.unit_var, "g", "g", "cup", "tbsp", "tsp")
        unit_menu.grid(row=1, column=3, sticky="w")

        # Grams per cup override
        ttk.Label(frm, text="Grams per cup (optional):").grid(row=2, column=0, sticky="w")
        self.gpc_entry = ttk.Entry(frm, width=12)
        self.gpc_entry.grid(row=2, column=1, sticky="w")

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=(8, 0))
        convert_btn = ttk.Button(btn_frame, text="Convert", command=self.on_convert)
        convert_btn.grid(row=0, column=0, padx=4)
        list_btn = ttk.Button(btn_frame, text="List known", command=self.on_list_known)
        list_btn.grid(row=0, column=1, padx=4)
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.on_clear)
        clear_btn.grid(row=0, column=2, padx=4)

        # Results
        self.results = tk.Text(frm, width=48, height=6, wrap="word")
        self.results.grid(row=4, column=0, columnspan=4, pady=(8, 0))
        self.results.configure(state="disabled")

        # make grid expand nicely
        for i in range(4):
            frm.columnconfigure(i, weight=1)

    def on_clear(self) -> None:
        self.ing_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.gpc_entry.delete(0, tk.END)
        self.unit_var.set("g")
        self._set_results("")

    def on_list_known(self) -> None:
        names = sorted(set(self.grams_map.keys()))
        out = "Known ingredients (built-in):\n"
        for n in names:
            out += f"  {n} — {self.grams_map[n]} g/cup\n"
        messagebox.showinfo("Known ingredients", out)

    def _set_results(self, text: str) -> None:
        self.results.configure(state="normal")
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, text)
        self.results.configure(state="disabled")

    def on_convert(self) -> None:
        ingredient = self.ing_entry.get().strip()
        if not ingredient:
            messagebox.showerror("Input error", "Please enter an ingredient name.")
            return

        amount_s = self.amount_entry.get().strip()
        try:
            amount = self.conv.parse_amount(amount_s)
        except Exception:
            messagebox.showerror("Input error", "Couldn't parse amount. Use a number like 100 or a simple fraction like 1/2.")
            return

        unit_raw = self.unit_var.get()
        unit = self.conv.normalize_unit(unit_raw)
        if unit is None:
            messagebox.showerror("Input error", "Unknown unit selected.")
            return

        if amount <= 0:
            messagebox.showerror("Input error", "Amount must be positive.")
            return

        key = ingredient.lower()
        grams_per_cup = self.grams_map.get(key)
        # If override provided in GUI, use it
        override = self.gpc_entry.get().strip()
        if override:
            try:
                gpc_val = float(override)
                if gpc_val <= 0:
                    raise ValueError()
                grams_per_cup = gpc_val
            except Exception:
                messagebox.showerror("Input error", "Grams per cup must be a positive number.")
                return

        if grams_per_cup is None:
            messagebox.showerror("Unknown ingredient", "Ingredient not known. Provide grams per cup in the field to convert.")
            return

        if unit == "g":
            grams = amount
            conv = self.conv.convert_from_grams(grams, grams_per_cup)
            out = f"{grams:.2f} g of {ingredient} is approximately:\n"
            out += f"  {conv['cup']:.3f} cup(s)\n"
            out += f"  {conv['tbsp']:.2f} tablespoon(s)\n"
            out += f"  {conv['tsp']:.1f} teaspoon(s)\n"
        else:
            grams = self.conv.convert_to_grams(amount, unit, grams_per_cup)
            friendly = unit
            if unit == "tbsp":
                friendly = "tablespoon(s)"
            elif unit == "tsp":
                friendly = "teaspoon(s)"
            elif unit == "cup":
                friendly = "cup(s)"
            out = f"{amount} {friendly} of {ingredient} is approximately {grams:.2f} g\n"

        self._set_results(out)


def main() -> None:
    try:
        conv_module = load_conversion_module()
    except Exception as exc:
        print("Failed to load conversion module:", exc)
        sys.exit(1)

    app = BakingConverterGUI(conv_module)
    app.mainloop()


if __name__ == "__main__":
    main()
