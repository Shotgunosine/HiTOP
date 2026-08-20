#!/usr/bin/env python
"""Calibrate a parametric pre-screen alpha for the exhaustive search.

Pairs every permutation p recorded by the overnight run (baseline,
stepwise histories, strict report -- targets inventoried in
log/calib_targets.pkl) with its parametric analog computed by refitting
the measEq ladder (no permutations): configural -> pvalue.scaled of the
model fit; delta levels -> Satorra-2000 scaled difference p from
lavaan::lavTestLRT.

Output: log/calibration_pairs.csv with columns
    scale, n_items, pair, level, perm_p, param_p, converged

Run from notebooks/: pixi run python calibrate_screen.py
"""
import os
import pickle
import sys

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np
import pandas as pd

from hitop_cfa import WU_ESTABROOK_LEVELS, fit_measeq_level, set_seeds
from hitop_cfa.measeq import fit_is_converged
from hitop_cfa.r_env import ro

LEVELS = [name for name, _ in WU_ESTABROOK_LEVELS]
GE = dict(WU_ESTABROOK_LEVELS)

targets = pickle.load(open('log/calib_targets.pkl', 'rb'))

d = '../data/finaldata'
val = pd.read_csv(f'{d}/dat_val.csv')
gp = pd.read_csv(f'{d}/dat_gp_grid1st_full.csv')
en = pd.read_csv(f'{d}/dat_en_grid1st_full.csv')
PAIRS = {'val_gp': pd.concat([val, gp]),
         'val_en': pd.concat([val, en]),
         'gp_en': pd.concat([gp, en])}

TEMP = 'log/calib_temp.csv'
current_pair = None

rows = []
# order by pair so the data csv is pushed to R only three times
items_by_pair = sorted(targets.items(), key=lambda kv: kv[0][2])
n = len(items_by_pair)
for ix, ((scale, items, pair), perm_ps) in enumerate(items_by_pair):
    if pair != current_pair:
        PAIRS[pair].to_csv(TEMP)
        ro.r(f'rdata <- read.csv("{TEMP}", header = TRUE)')
        ro.globalenv['group'] = 'whichdata'
        current_pair = pair
    ro.globalenv['testformula_r'] = scale + " =~ " + " + ".join(items)

    max_lv = max(LEVELS.index(l) for l in perm_ps)
    set_seeds(12345)
    param_p = {}
    prev_ok = True
    for li in range(max_lv + 1):
        lev = LEVELS[li]
        try:
            fit_measeq_level(list(items), GE[lev], r_fit_name=f'cfit_{li}')
            ok = fit_is_converged(f'cfit_{li}')
        except Exception:
            ok = False
        if not ok:
            param_p[lev] = (np.nan, False)
            prev_ok = False
            continue
        if li == 0:
            p = float(ro.r('lavaan::fitMeasures(cfit_0, "pvalue.scaled")')[0])
        elif prev_ok:
            p = float(ro.r(
                f'lavaan::lavTestLRT(cfit_{li-1}, cfit_{li})'
                f'[2, "Pr(>Chisq)"]')[0])
        else:
            p = np.nan
        param_p[lev] = (p, True)
        prev_ok = True

    for lev, perm in perm_ps.items():
        pp, conv = param_p.get(lev, (np.nan, False))
        rows.append(dict(scale=scale, n_items=len(items), pair=pair,
                         level=lev, perm_p=perm, param_p=pp, converged=conv))
    if (ix + 1) % 50 == 0 or ix == n - 1:
        print(f'{ix + 1}/{n} combos done', flush=True)
        pd.DataFrame(rows).to_csv('log/calibration_pairs.csv', index=None)

pd.DataFrame(rows).to_csv('log/calibration_pairs.csv', index=None)
print(f'wrote {len(rows)} paired tests to log/calibration_pairs.csv')
