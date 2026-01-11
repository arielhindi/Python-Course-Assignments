import argparse
import pandas as pd

import os
import math
from typing import Dict, List, Tuple, Optional


def well_name(row: int, col: int) -> str:
    return f"{chr(ord('A')+row)}{col+1}"


def _is_number(v) -> bool:
    try:
        float(v)
        return True
    except Exception:
        return False


def read_plate_file(path: str) -> Dict[str, float]:
    """Try to read an Excel/CSV file and return mapping well->absorbance.

    Supports:
    - 8x12 grid where rows correspond to A-H and columns 1-12
    - long table with columns 'Well' and 'Absorbance'
    """
    if path.lower().endswith(('.xls', '.xlsx')):
        # prefer openpyxl engine when available to avoid ambiguous engine errors
        try:
            df = pd.read_excel(path, header=None, engine='openpyxl')
        except Exception:
            # fallback to default (let pandas choose)
            df = pd.read_excel(path, header=None)
    else:
        # try CSV
        df = pd.read_csv(path, header=None)

    # If dataframe looks like 8x12 (or contains 8x12 block) try to map
    h, w = df.shape

    def is_row_label(val: object) -> bool:
        try:
            s = str(val).strip()
            return len(s) == 1 and s.upper() >= 'A' and s.upper() <= 'H'
        except Exception:
            return False

    def is_col_header(val: object) -> bool:
        try:
            v = str(val).strip()
            if not v:
                return False
            iv = int(float(v))
            return 1 <= iv <= 12
        except Exception:
            return False

    # find candidate label column
    label_col = None
    label_rows = None
    for c in range(w):
        rows_with_label = [r for r in range(h) if is_row_label(df.iat[r, c])]
        if len(rows_with_label) >= 2:
            seqs = []
            cur = [rows_with_label[0]]
            for idx in rows_with_label[1:]:
                if idx == cur[-1] + 1:
                    cur.append(idx)
                else:
                    seqs.append(cur)
                    cur = [idx]
            seqs.append(cur)
            longest = max(seqs, key=len)
            if len(longest) >= 2:
                label_col = c
                label_rows = longest
                break

    header_row = None
    header_cols = None
    for r in range(h):
        cols_with_nums = [c for c in range(w) if is_col_header(df.iat[r, c])]
        if len(cols_with_nums) >= 2:
            seqs = []
            cur = [cols_with_nums[0]]
            for idx in cols_with_nums[1:]:
                if idx == cur[-1] + 1:
                    cur.append(idx)
                else:
                    seqs.append(cur)
                    cur = [idx]
            seqs.append(cur)
            longest = max(seqs, key=len)
            if len(longest) >= 2:
                header_row = r
                header_cols = longest
                break

    if label_col is not None and header_row is not None:
        mapping: Dict[str, float] = {}
        col_nums = []
        for c in header_cols:
            try:
                col_nums.append(int(float(str(df.iat[header_row, c]).strip())))
            except Exception:
                col_nums.append(None)
        for i_idx, r in enumerate(label_rows):
            label = str(df.iat[r, label_col]).strip()
            if not label:
                continue
            row_letter = label.upper()
            for j_idx, c in enumerate(header_cols):
                col_num = col_nums[j_idx]
                if col_num is None:
                    continue
                well = f"{row_letter}{col_num}"
                try:
                    val = df.iat[r, c]
                    if isinstance(val, str):
                        v2 = val.strip().replace(',', '')
                    else:
                        v2 = val
                    mapping[well] = float(v2)
                except Exception:
                    mapping[well] = math.nan
        if mapping:
            return mapping

    # try to find 8x12 block
    if h >= 8 and w >= 12:
        for r0 in range(0, max(1, h - 7)):
            for c0 in range(0, max(1, w - 11)):
                candidates = []
                if r0 + 8 <= h and c0 + 12 <= w:
                    candidates.append(df.iloc[r0:r0+8, c0:c0+12])
                if r0 + 9 <= h and c0 + 13 <= w:
                    candidates.append(df.iloc[r0+1:r0+9, c0+1:c0+13])
                if r0 + 8 <= h and c0 + 13 <= w:
                    candidates.append(df.iloc[r0:r0+8, c0+1:c0+13])
                if r0 + 9 <= h and c0 + 12 <= w:
                    candidates.append(df.iloc[r0+1:r0+9, c0:c0+12])

                for block in candidates:
                    def try_float(x):
                        try:
                            if isinstance(x, str):
                                x2 = x.strip().replace(',', '')
                            else:
                                x2 = x
                            float(x2)
                            return True
                        except Exception:
                            return False

                    numeric_mask = block.applymap(try_float)
                    if numeric_mask.values.sum() >= 8*12*0.5:
                        mapping: Dict[str, float] = {}
                        for i in range(8):
                            for j in range(12):
                                val = block.iat[i, j]
                                try:
                                    if isinstance(val, str):
                                        val2 = val.strip().replace(',', '')
                                    else:
                                        val2 = val
                                    mapping[well_name(i, j)] = float(val2)
                                except Exception:
                                    mapping[well_name(i, j)] = math.nan
                        return mapping

    # Try long format
    cols = list(df.columns)
    txtcols = [str(c).lower() for c in cols]
    if 'well' in txtcols and ('abs' in ''.join(txtcols) or 'absorbance' in txtcols):
        well_col = cols[txtcols.index('well')]
        abs_idx = next(i for i,c in enumerate(txtcols) if 'absorb' in c)
        abs_col = cols[abs_idx]
        mapping = {}
        for _, row in df.iterrows():
            w = str(row[well_col]).strip()
            try:
                mapping[w] = float(row[abs_col])
            except Exception:
                mapping[w] = math.nan
        return mapping

    # fallback
    if df.shape[1] >= 2:
        mapping = {}
        for _, row in df.iterrows():
            w = str(row.iloc[0]).strip()
            try:
                mapping[w] = float(row.iloc[1])
            except Exception:
                mapping[w] = math.nan
        return mapping

    raise RuntimeError("Could not interpret plate file format; expected 8x12 grid or Well/Absorbance table")


def prompt_groups() -> Tuple[List[str], List[Tuple[List[str], Optional[float]]]]:
    """Ask the user for blank wells and standard groups.

    Returns (blank_wells, standards) where standards is list of (wells, conc)
    """
    print("Enter groups, one per line. Format examples:")
    print("  A1,A2 -> blank")
    print("  B1,B2 -> 2.0")
    print("Finish with an empty line.")
    standards: List[Tuple[List[str], float]] = []
    blank_wells: List[str] = []
    while True:
        try:
            line = input('group> ').strip()
        except EOFError:
            break
        if not line:
            break
        if '->' not in line:
            print("Invalid format; use 'W1,W2 -> value' where value is numeric or 'blank'")
            continue
        left, right = [s.strip() for s in line.split('->', 1)]
        wells = [w.strip().upper() for w in left.split(',') if w.strip()]
        if right.lower() == 'blank':
            blank_wells.extend(wells)
        else:
            try:
                conc = float(right)
            except Exception:
                print('Could not parse concentration; try again')
                continue
            standards.append((wells, conc))
    return blank_wells, standards


def compute_calibration(blank_wells: List[str], standards: List[Tuple[List[str], float]], mapping: Dict[str, float]):
    # compute blank mean
    blank_vals = [mapping[w] for w in blank_wells if w in mapping and isinstance(mapping[w], (int, float))]
    blank_mean = sum(blank_vals) / len(blank_vals) if blank_vals else 0.0

    xs = []
    ys = []
    for wells, conc in standards:
        vals = [mapping[w] for w in wells if w in mapping and isinstance(mapping[w], (int, float))]
        if not vals:
            raise RuntimeError(f'No numeric values for wells {wells}')
        mean_abs = sum(vals) / len(vals)
        ys.append(mean_abs - blank_mean)
        xs.append(conc)

    # fit y = m*x + b
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(xs, ys))
    den = sum((xi - mean_x) ** 2 for xi in xs)
    if den == 0:
        raise RuntimeError('Zero variance in concentrations; cannot fit')
    m = num / den
    b = mean_y - m * mean_x
    # R^2
    ss_res = sum((yi - (m * xi + b)) ** 2 for xi, yi in zip(xs, ys))
    ss_tot = sum((yi - mean_y) ** 2 for yi in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0
    return m, b, r2, blank_mean


def write_results_excel(out_path: str, mapping: Dict[str, float], standards: List[Tuple[List[str], float]], m: float, b: float, r2: float, blank_mean: float):
    # create a DataFrame for calibration points and samples, then write with xlsxwriter and add chart
    cal_rows = []
    for wells, conc in standards:
        vals = [mapping[w] for w in wells if w in mapping]
        mean_abs = sum(vals) / len(vals)
        cal_rows.append({'Concentration': conc, 'MeanAbs': mean_abs, 'MeanAbs_blank_sub': mean_abs - blank_mean})

    samples = []
    assigned = {w for grp, _ in standards for w in grp}
    for w in sorted(mapping):
        if w in assigned:
            continue
        val = mapping[w]
        if not isinstance(val, (int, float)):
            continue
        adj = val - blank_mean
        try:
            est = (adj - b) / m
        except Exception:
            est = float('nan')
        samples.append({'Well': w, 'Absorbance': val, 'Abs_blank_sub': adj, 'Estimated_Conc': est})

    cal_df = pd.DataFrame(cal_rows)
    samp_df = pd.DataFrame(samples)

    # write to Excel with a chart using xlsxwriter
    with pd.ExcelWriter(out_path, engine='xlsxwriter') as writer:
        cal_df.to_excel(writer, sheet_name='Calibration', index=False)
        samp_df.to_excel(writer, sheet_name='Samples', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Calibration']
        worksheet_samples = writer.sheets['Samples']
        # create scatter chart: x = Concentration, y = MeanAbs_blank_sub
        chart = workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
        # data ranges
        nrows = len(cal_df)
        if nrows > 0:
            chart.add_series({
                'name': 'Standards',
                'categories': ['Calibration', 1, 0, nrows, 0],
                'values':     ['Calibration', 1, 2, nrows, 2],
                'marker': {'type': 'circle', 'size': 6},
            })
            # add a trendline series by computing fitted y for plotting points
            xs_list = cal_df['Concentration'].tolist()
            ys_fit = [m * x + b for x in xs_list]
            # write fit values to new column
            fit_col = cal_df.shape[1] + 1
            for i, v in enumerate(ys_fit, start=1):
                worksheet.write(i, fit_col, v)
            chart.add_series({
                'name': 'Fit',
                'categories': ['Calibration', 1, 0, nrows, 0],
                'values':     ['Calibration', 1, fit_col, nrows, fit_col],
                'line': {'color': 'red'},
            })
            chart.set_x_axis({'name': 'Concentration'})
            chart.set_y_axis({'name': 'Absorbance (blank-subtracted)'})
            chart.set_title({'name': f'Calibration (R^2={r2:.3f})'})
            worksheet.insert_chart('E2', chart, {'x_scale': 1.5, 'y_scale': 1.5})
        # write fitted function and stats below the calibration table
        meta_row = nrows + 3
        worksheet.write(meta_row, 0, 'Slope (m)')
        worksheet.write(meta_row, 1, m)
        worksheet.write(meta_row+1, 0, 'Intercept (b)')
        worksheet.write(meta_row+1, 1, b)
        worksheet.write(meta_row+2, 0, 'R^2')
        worksheet.write(meta_row+2, 1, r2)
        worksheet.write(meta_row+3, 0, 'Blank mean')
        worksheet.write(meta_row+3, 1, blank_mean)
        # write equation text
        eq_text = f"y = {m:.9g}*x + {b:.9g}"
        worksheet.write(meta_row+4, 0, 'Fitted function')
        worksheet.write(meta_row+4, 1, eq_text)

        # replace estimated concentration column in Samples sheet with formulas
        # Samples columns: Well (A), Absorbance (B), Abs_blank_sub (C), Estimated_Conc (D)
        # data rows start at 1 (row 0 is header)
        for i in range(len(samp_df)):
            excel_row = i + 1  # 0-based index for xlsxwriter (header at row 0)
            # Abs_blank_sub is column C (index 2), Estimated_Conc is column D (index 3)
            # Excel rows are 1-based in A1 notation
            a1_row = excel_row + 1
            # build formula using constants m and b
            if m == 0:
                formula = '=NA()'
            else:
                formula = f"=(C{a1_row} - {b}) / {m}"
            worksheet_samples.write_formula(excel_row, 3, formula)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Plate file (Excel or CSV)')
    parser.add_argument('--output', '-o', help='Output Excel file', default='calibration_output.xlsx')
    args = parser.parse_args()

    mapping = read_plate_file(args.input)
    print(f'Read {len(mapping)} wells from {args.input}')
    blank_wells, standards = prompt_groups()
    if not standards:
        print('No standards provided; aborting')
        return
    m, b, r2, blank_mean = compute_calibration(blank_wells, standards, mapping)
    print(f'Fit: y = {m:.6g} x + {b:.6g} (R^2={r2:.4f}), blank_mean={blank_mean:.6g}')
    write_results_excel(args.output, mapping, standards, m, b, r2, blank_mean)
    print(f'Wrote results to {args.output}')


if __name__ == '__main__':
    main()
