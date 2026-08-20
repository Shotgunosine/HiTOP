#!/usr/bin/env python
"""Status of a NB_2_cfa_as_reg-style pipeline run (3-way or gp_en variant),
read from the incrementally-persisted artifacts in its cfa dir.

Usage (from notebooks/):
    pixi run python pipeline_status.py ../data/cfa_gp_en   # the 2-way run
    pixi run python pipeline_status.py                      # ../data/cfa

Note: when run headless (run_overnight.sh / nbconvert), the stepwise
cells' prints are captured in the notebook and invisible until it
finishes -- the artifacts read here (updated after every scale, plus the
temp csv touched at every model fit) are the live signal.
"""
import sys
import time
from pathlib import Path

import pandas as pd

cfa = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('../data/cfa')
if not cfa.exists():
    sys.exit(f'{cfa} does not exist (run not started?)')


def age(path):
    if not path.exists():
        return None
    s = time.time() - path.stat().st_mtime
    return (f'{s:.0f}s ago' if s < 120 else
            f'{s/60:.0f}m ago' if s < 7200 else f'{s/3600:.1f}h ago')


def stage(name, final, in_progress, describe):
    fin, prog = cfa / final, cfa / in_progress
    if fin.exists() and (not prog.exists()
                         or fin.stat().st_mtime >= prog.stat().st_mtime):
        print(f'  {name:<18} DONE      {describe(fin)}  ({age(fin)})')
        return True
    if prog.exists():
        print(f'  {name:<18} running   {describe(prog)}  (updated {age(prog)})')
        return False
    print(f'  {name:<18} not started')
    return False


def n_scales_csv(p):
    df = pd.read_csv(p)
    return f'{df["scale"].nunique()} scales'


def stepwise_desc(p):
    df = pd.read_pickle(p)
    if not len(df) or 'scale' not in df.columns:
        return '0 scales'
    if 'item_nos' in df.columns:
        found = int(df['item_nos'].notna().sum())
        return f'{len(df)} scales ({found} with a core)'
    return f'{len(df)} scales (none with a core)'


def scalar_desc(p):
    df = pd.read_pickle(p)
    if not len(df):
        return '0 scales'
    lv = df['core_level'].value_counts(dropna=False).to_dict()
    parts = [f"{int(v)} {('none' if pd.isna(k) else k)}" for k, v in lv.items()]
    return f"{len(df)} scales ({', '.join(parts)})"


print(f'pipeline status for {cfa.resolve()}')
stage('baseline', 'orig_cfa_res.csv', 'orig_cfa_res_in_progress.csv',
      n_scales_csv)
stage('stepwise metric', 'stepwise.pkl', 'stepwise_in_progress.pkl',
      stepwise_desc)
stage('scalar continuation', 'stepwise_scalar.pkl',
      'stepwise_scalar_in_progress.pkl', scalar_desc)
stage('strict report', 'final_cores_strict_report.csv',
      'final_cores_strict_report_in_progress.csv', n_scales_csv)

temp = cfa / 'temp' / 'cfa_temp.csv'
if temp.exists():
    print(f'  last model fit    {age(temp)} (temp csv touch)')
err = cfa / 'run_errors.log'
if err.exists():
    print(f'\n!!! run_errors.log present ({age(err)}):')
    print(err.read_text()[-1500:])
else:
    print('  no errors recorded')
