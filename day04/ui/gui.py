"""Tkinter GUI for IMS-based stargazing recommender.

The GUI asks the user for date and location, runs the analysis, and displays
the score, confidence, and a recommendation. The window uses a simple
starry-themed background image if Pillow is installed and an image file is
placed in the `day04/ui/` folder called `stars_bg.jpg` (optional).

Dependencies: tkinter (builtin), requests, beautifulsoup4, pillow (optional)
"""

from __future__ import annotations

import datetime
import os
import tkinter as tk
from tkinter import ttk, messagebox

from day04 import business_logic  # type: ignore


class StargazeApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Stargazing Recommender")
        self.geometry("600x420")

        # No background image; use default window background

        frm = ttk.Frame(self, padding=12)
        frm.place(relx=0.5, rely=0.05, anchor="n")

        ttk.Label(frm, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(frm)
        self.date_entry.grid(row=0, column=1, sticky="w")
        self.date_entry.insert(0, datetime.date.today().isoformat())

        ttk.Label(frm, text="Location:").grid(row=1, column=0, sticky="w")
        self.loc_entry = ttk.Entry(frm)
        self.loc_entry.grid(row=1, column=1, sticky="w")
        self.loc_entry.insert(0, "Tel Aviv")

        run_btn = ttk.Button(frm, text="Analyze", command=self.on_analyze)
        run_btn.grid(row=2, column=0, columnspan=2, pady=(8, 0))

        self.output = tk.Text(self, width=72, height=15, bg="#001022", fg="#ddf7ff")
        self.output.place(relx=0.5, rely=0.28, anchor="n")

    def on_analyze(self) -> None:
        s = self.date_entry.get().strip()
        loc = self.loc_entry.get().strip() or "Tel Aviv"
        try:
            date = datetime.date.fromisoformat(s)
        except Exception:
            messagebox.showerror("Invalid date", "Please enter date in YYYY-MM-DD format")
            return

        self._append_output(f"Analyzing {date.isoformat()} for {loc}...\n")
        try:
            result = business_logic.analyze_date(date, loc)
        except Exception as exc:
            self._append_output(f"Analysis failed: {exc}\n")
            return

        self._show_result(result)

    def _append_output(self, text: str) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.configure(state="disabled")

    def _show_result(self, r: dict) -> None:
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", f"Visibility score: {r['score']:.1f}/100\n")
        self.output.insert("end", f"Confidence in forecast: {r['confidence']*100:.0f}%\n")
        self.output.insert("end", f"Cloudiness: {r.get('cloudiness')}%\n")
        self.output.insert("end", f"Precipitation chance: {r.get('precip_prob')}%\n")
        mf = r.get('moon_phase_frac')
        if mf is not None:
            self.output.insert("end", f"Moon phase (0=new,0.5=full): {mf:.2f}\n")
        self.output.insert("end", f"Meteor shower: {r.get('meteor_shower')} intensity {r.get('meteor_intensity'):.2f}\n")
        if r.get('recommendation'):
            rec = r['recommendation']
            self.output.insert("end", f"Recommendation: try {rec['date']} (estimated score {rec['score']:.1f})\n")
        else:
            self.output.insert("end", "Recommendation: no better date found soon.\n")
        # Show reliability message
        if r.get('reliability_msg'):
            self.output.insert("end", f"\n[Info] {r['reliability_msg']}\n")
        self.output.configure(state="disabled")


def main() -> None:
    app = StargazeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
