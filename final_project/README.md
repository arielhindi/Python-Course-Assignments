# final_project — automated absorbance → calibration → western-blot loader

Project proposal
----------------

Goal
----
Create a small, robust pipeline that accepts a single absorbance export
(Excel or CSV) from a plate reader and produces an Excel workbook that:

- computes a blank-subtracted calibration (standard curve) and R²,
- reports concentrations for all sample wells (averaging technical
	replicates/duplicates automatically), and
- calculates the volume of each pooled/averaged sample required to load on
	a western blot gel to deliver a target mass of protein (e.g. 10 µg per lane).

Motivation
----------
Wet-lab workflows require repetitive manual calculations: blank subtraction,
standard curve fitting, averaging duplicate wells, and converting a target
mass into a loading volume using measured concentration. Automating these
steps removes human error and speeds up daily lab work — a single file
upload should give you both concentrations and exact loading volumes.

High-level approach
-------------------
1. Accept an absorbance file (Excel `.xlsx` or CSV). The loader will detect
	 standard plate layouts (8×12) or a long table with `Well,Absorbance`.
2. Ask the user (interactive prompt or groups file) which wells are blanks
	 and which are standards (allow duplicate wells), and the concentration
	 associated with each standard group. Optionally accept a mapping file to
	 run non-interactively.
3. Compute blank mean, subtract from all absorbances, compute mean and
	 standard deviation for technical replicates.
4. Fit a linear calibration (or optionally log/4PL later) to standards and
	 compute R² and fit diagnostics.
5. Convert blank-subtracted absorbances to concentrations for each sample
	 replicate, then compute the average concentration and standard error for
	 each biological sample (grouping by naming convention or a user-supplied
	 mapping table).
6. For each averaged sample, compute required loading volume to reach a
	 target mass per lane (user-specified, e.g. 10 µg). Formula:

	 volume (µL) = (target_mass (µg)) / (concentration (µg/µL))

	 The workbook will check units (if concentration returned in µg/mL, convert
	 appropriately) and flag impossible volumes (e.g. > max available volume).
7. Write an output Excel workbook with:
	 - `Calibration` sheet: standards, blank mean, fitted parameters (m, b), R²,
		 and a native Excel scatter chart of standards + fitted line.
	 - `Samples` sheet: raw replicate absorbances, blank-subtracted values,
		 estimated concentration per replicate (as Excel formulas), mean ± SD,
		 and required loading volume (Excel formula so manual edits to target
		 mass update volumes live).
	 - optional `Mapping` sheet when user supplies biological grouping info.

Features and UX
---------------
- Interactive mode: prompt for blank/standard groups.
- Non-interactive mode: accept a `--groups-file` and a `--mapping-file`
	(CSV) so the pipeline can be integrated into larger workflows.
- All concentration and volume calculations are written as Excel formulas
	(not only values) so users can tweak fit parameters or target mass inside
	Excel and immediately see updated volumes.
- Basic validation: reasonable absorbance ranges, detection of outlier
	standards, and warnings if the fit R² is poor.

Inputs
------
- Excel `.xlsx` or CSV containing either a labeled 8×12 plate or a two-
	column long table (`Well,Absorbance`).
- Interactive groups (stdin) or a groups file with lines like
	`A1,A2 -> 2000` and `A6,A7 -> blank`.
- Optional mapping CSV: biological sample name → list of well names.

Outputs
-------
- `output.xlsx` with `Calibration`, `Samples`, and `Mapping` sheets and an
	embedded scatter chart. Cells containing computed concentrations and
	loading volumes are Excel formulas referencing calibration metadata where
	possible.

Dependencies
------------
- Python 3.8+
- pandas
- openpyxl (read .xlsx)
- xlsxwriter (write .xlsx with charts)
