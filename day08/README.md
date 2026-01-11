# day08 — 96-well plate absorbance analysis

This is a command-line tool that loads a 96-well plate absorbance file
(Excel or CSV), builds a blank-subtracted linear calibration from user-
specified standard wells, and writes the results into an Excel workbook
with a native scatter chart. The previous Tk GUI is deprecated; use
`day08/excel_calibrate.py`.

For a full usage guide (dependencies, file formats, run examples and
troubleshooting), see `day08/USAGE.md`.

Usage
-----

Install dependencies into a virtualenv (recommended):

```bash
python -m pip install -r day08/requirements.txt
```

Run the Excel-based calibration helper:

```bash
python -m day08.excel_calibrate path/to/BCA.xlsx -o BCA_with_graphs.xlsx
```

The script will prompt you to enter blank well groups and standard groups (format: `A1,A2 -> blank` or `B1,B2 -> 2.0`). It writes an Excel file containing the calibration table, the samples table, and a native Excel scatter chart.

How it works
------------
- Accepts either a labeled 8×12 plate grid (rows A–H, cols 1–12) or a simple
  long table with columns `Well` and `Absorbance` (e.g. `A1,0.123`). The
  loader includes heuristics to locate numeric blocks in export files.
- You specify groups interactively (or via heredoc) in the format
  `A1,A2 -> 1000` or `B1,B2 -> blank` where `blank` marks blank wells.
- The script computes the blank mean, subtracts it from all absorbance
  readings, fits a straight line (MeanAbs_blank_sub = m*Concentration + b),
  reports m, b and R², and writes estimated concentrations into the
  `Samples` sheet as Excel formulas so the workbook recalculates live.

Notes
-----
- The script expects reasonable numeric absorbance values. If your file uses
  a different layout, export it as a simple CSV with a header and columns
  `Well,Absorbance` and try again.
- This is a lightweight tool intended for quick classroom use. If you'd like
  CSV/JSON export or automated grouping rules, I can add them.
