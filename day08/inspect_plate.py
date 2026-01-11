"""Command-line inspector for 96-well plate files.

Usage:
    python -m day08.inspect_plate /path/to/plate.xlsx

This prints candidate 8x12 blocks found in the sheet along with the fraction
of numeric cells, and exits with code 0 if a block was selected.
"""
from __future__ import annotations

import sys
import math
from typing import Dict

try:
    import pandas as pd
except Exception:
    pd = None

def _is_number_str(x: object) -> bool:
    try:
        if isinstance(x, str):
            x = x.strip().replace(',', '')
        float(x)
        return True
    except Exception:
        return False

def inspect(path: str) -> Dict[str, float]:
    if pd is None:
        raise RuntimeError('pandas required; pip install -r day08/requirements.txt')
    print(f'Reading {path} ...')
    df = pd.read_excel(path, header=None) if path.lower().endswith(('.xls', '.xlsx')) else pd.read_csv(path, header=None)
    h, w = df.shape
    print(f'Sheet size: {h} rows x {w} cols')

    found_any = False
    for r0 in range(0, max(1, h - 7)):
        for c0 in range(0, max(1, w - 11)):
            candidates = []
            if r0 + 8 <= h and c0 + 12 <= w:
                candidates.append((r0, c0, df.iloc[r0:r0+8, c0:c0+12]))
            if r0 + 9 <= h and c0 + 13 <= w:
                candidates.append((r0+1, c0+1, df.iloc[r0+1:r0+9, c0+1:c0+13]))
            if r0 + 8 <= h and c0 + 13 <= w:
                candidates.append((r0, c0+1, df.iloc[r0:r0+8, c0+1:c0+13]))
            if r0 + 9 <= h and c0 + 12 <= w:
                candidates.append((r0+1, c0, df.iloc[r0+1:r0+9, c0:c0+12]))

            for rr, cc, block in candidates:
                total = 8*12
                num_numeric = sum(1 for v in block.values.flatten() if _is_number_str(v))
                frac = num_numeric/total
                if frac >= 0.2:
                    print(f'Candidate block at r={rr} c={cc} -> numeric {num_numeric}/{total} ({frac:.2f})')
                    found_any = True
    if not found_any:
        print('No candidate 8x12 blocks found (try exporting a simple Well/Absorbance CSV).')
    return {}

def main(argv):
    if len(argv) < 2:
        print('Usage: python -m day08.inspect_plate /path/to/file')
        return 2
    path = argv[1]
    try:
        inspect(path)
    except Exception as e:
        print('Error:', e)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
