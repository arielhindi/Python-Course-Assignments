# day08 usage

This document explains how to run the `day08` plate calibrator, its
dependencies, acceptable input formats and example commands.

## What the code does

- Loads an absorbance export (xlsx or CSV) and searches for a 96-well layout
  or a simple two-column long table (`Well,Absorbance`).
- Lets you specify which wells are the blank and which wells are standards
  (duplicates allowed), together with the standard concentrations.
- Computes the blank mean, subtracts it from all absorbance values,
  performs a linear fit (MeanAbs_blank_sub = m * Concentration + b), and
  computes R².
- Writes an Excel workbook containing:
  - `Calibration` sheet: standards table, slope (m), intercept (b), R²,
    blank mean and a single-line text of the fitted function.
  - `Samples` sheet: all wells, their blank-subtracted absorbance and an
    `Estimated_Conc` column implemented as an Excel formula so Excel will
    recalculate concentrations live.
  - A native Excel scatter chart (standards + fitted line) embedded in the
    `Calibration` sheet.

## Dependencies

See `day08/requirements.txt`. The main packages are:
- pandas
- openpyxl
- xlsxwriter

Install into a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r day08/requirements.txt
```

## Input file formats

Supported inputs:
- A labeled plate grid (rows A..H, columns 1..12).
- A long table with columns `Well` and `Absorbance`.
- A simple CSV exported as `Well,Absorbance`.

## Running the calibrator

```bash
python -m day08.excel_calibrate path/to/BCA.xlsx -o day08/BCA_with_graphs.xlsx
```

Interactive group input examples:

```
A1,B1 -> 2000
A2,B2 -> 1000
A3,B3 -> 500
A4,B4 -> 250
A5,B5 -> 25
A6,B6 -> blank

# (finish with an empty line)
```

Non-interactive (heredoc):

```bash
source .venv/bin/activate
python -m day08.excel_calibrate day08/BCA.xlsx -o day08/BCA_with_graphs.xlsx <<'EOF'
A1,B1 -> 2000
A2,B2 -> 1000
A3,B3 -> 500
A4,B4 -> 250
A5,B5 -> 25
A6,B6 -> blank
EOF
```

## Troubleshooting

If the loader fails to detect the plate region, run:

```bash
python -m day08.inspect_plate path/to/BCA.xlsx
```

This prints candidate 8x12 blocks and numeric fractions to help you locate the
data.

## Output

- `Calibration` sheet: calibration table, slope/intercept/R²/blank mean and
  a fitted-function text.
- `Samples` sheet: well list, blank-subtracted absorbances and `Estimated_Conc`
  cells implemented with Excel formulas so values update when the calibration
  numbers are edited.

If you'd like small changes (Samples formulas to reference calibration cells,
`--groups-file` for full non-interactive runs, additional formatting), I can
implement them quickly.
