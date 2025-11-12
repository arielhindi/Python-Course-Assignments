"""Tkinter GUI wiring for baking conversions.

This file contains only GUI-related code and uses the pure functions in
`business_logic.py` and the ingredient persistence in `ingredients.py`.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from business_logic import (
    parse_amount,
    normalize_unit,
    convert_from_grams,
    convert_to_grams,
    add_ingredient_permanently,
)
import ingredients


class BakingConverterGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Baking Conversions")
        self.grams_map = ingredients.get_all_ingredients()

        frm = ttk.Frame(self, padding=12)
        frm.grid(row=0, column=0, sticky="nsew")

        # Ingredient (use Combobox for basic autocomplete/dropdown)
        ttk.Label(frm, text="Ingredient:").grid(row=0, column=0, sticky="w")
        ing_values = sorted(self.grams_map.keys())
        self.ing_combo = ttk.Combobox(frm, values=ing_values, width=30)
        self.ing_combo.grid(row=0, column=1, columnspan=2, sticky="ew")
        # allow typing
        self.ing_combo.set("")

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

        for i in range(4):
            frm.columnconfigure(i, weight=1)

    def on_clear(self) -> None:
        # clear combobox value
        self.ing_combo.set("")
        self.amount_entry.delete(0, tk.END)
        self.gpc_entry.delete(0, tk.END)
        self.unit_var.set("g")
        self._set_results("")

    def on_list_known(self) -> None:
        names = sorted(set(self.grams_map.keys()))
        out = "Known ingredients (built-in + custom):\n"
        for n in names:
            out += f"  {n} — {self.grams_map[n]} g/cup\n"
        messagebox.showinfo("Known ingredients", out)

    def _set_results(self, text: str) -> None:
        self.results.configure(state="normal")
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, text)
        self.results.configure(state="disabled")

    def on_convert(self) -> None:
        # read from combobox (user may type or select)
        ingredient = (self.ing_combo.get() or "").strip()
        if not ingredient:
            messagebox.showerror("Input error", "Please enter an ingredient name.")
            return

        amount_s = self.amount_entry.get().strip()
        try:
            amount = parse_amount(amount_s)
        except Exception:
            messagebox.showerror("Input error", "Couldn't parse amount. Use a number like 100 or a simple fraction like 1/2.")
            return

        unit_raw = self.unit_var.get()
        unit = normalize_unit(unit_raw)
        if unit is None:
            messagebox.showerror("Input error", "Unknown unit selected.")
            return

        if amount <= 0:
            messagebox.showerror("Input error", "Amount must be positive.")
            return

        grams_per_cup = ingredients.get_grams_per_cup(ingredient)

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
            add = messagebox.askyesno("Unknown ingredient", f"'{ingredient}' is not known. Add it permanently?")
            if add:
                gpc = simpledialog.askfloat("Add ingredient", "Enter grams per 1 cup for this ingredient:", minvalue=0.0001)
                if gpc is None:
                    messagebox.showinfo("Cancelled", "Did not add ingredient.")
                    return
                try:
                    add_ingredient_permanently(ingredient, float(gpc))
                    # refresh local map
                    self.grams_map = ingredients.get_all_ingredients()
                    # refresh combobox values so the newly added ingredient appears
                    self.ing_combo["values"] = sorted(self.grams_map.keys())
                    grams_per_cup = float(gpc)
                except Exception as exc:
                    messagebox.showerror("Error", f"Failed to add ingredient: {exc}")
                    return
            else:
                messagebox.showinfo("Info", "Provide grams per cup in the field to convert, or add the ingredient permanently.")
                return

        if unit == "g":
            grams = amount
            conv = convert_from_grams(grams, grams_per_cup)
            out = f"{grams:.2f} g of {ingredient} is approximately:\n"
            out += f"  {conv['cup']:.3f} cup(s)\n"
            out += f"  {conv['tbsp']:.2f} tablespoon(s)\n"
            out += f"  {conv['tsp']:.1f} teaspoon(s)\n"
        else:
            grams = convert_to_grams(amount, unit, grams_per_cup)
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
    app = BakingConverterGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
