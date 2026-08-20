#!/usr/bin/env python
"""Analyze log/calibration_pairs.csv: propose alpha_screen and quantify
what a parametric pre-screen would have saved / cost on the overnight
run's 954 recorded permutation tests.

Run from notebooks/: pixi run python analyze_calibration.py
"""
import pandas as pd
import numpy as np

df = pd.read_csv('log/calibration_pairs.csv')
LEVELS = ['configural', 'thresholds', 'metric', 'scalar', 'strict']
df['level'] = pd.Categorical(df['level'], LEVELS, ordered=True)

print(f"paired tests: {len(df)}   non-convergent refits: {int((~df.converged).sum())}")
usable = df[df.converged & df.param_p.notna()].copy()
print(f"usable pairs: {len(usable)}\n")

print("per-level agreement (Spearman rho of param vs perm p):")
for lev, g in usable.groupby('level', observed=True):
    if len(g) > 2:
        rho = g[['param_p', 'perm_p']].corr(method='spearman').iloc[0, 1]
        print(f"  {lev:<11} n={len(g):>3}  rho={rho:.3f}")

# THE feasibility quantity: among permutation PASSERS (perm_p >= .05),
# how small does the parametric p ever get? alpha_screen must sit safely
# below that minimum, or the screen could discard a real passer.
print("\nminimum parametric p among permutation passers (perm_p >= .05):")
passers = usable[usable.perm_p >= 0.05]
q_min_all = passers.param_p.min()
for lev, g in passers.groupby('level', observed=True):
    if len(g):
        gmin = g.loc[g.param_p.idxmin()]
        print(f"  {lev:<11} n={len(g):>3}  min param_p = {gmin.param_p:.4f} "
              f"(perm_p={gmin.perm_p:.3f}, {gmin.scale}/{gmin.pair}, "
              f"{int(gmin.n_items)} items)")
print(f"  OVERALL     n={len(passers):>3}  min param_p = {q_min_all:.4f}")

# margin check against the fuzz zone: passers comfortably above .05
solid = usable[usable.perm_p >= 0.10]
print(f"\namong SOLID passers (perm_p >= .10, n={len(solid)}): "
      f"min param_p = {solid.param_p.min():.4f}")

print("\ncandidate alpha_screen performance on the recorded tests:")
print(f"{'alpha':>8}{'tests screened out':>20}{'would-be passers lost':>24}"
      f"{'closest lost perm_p':>21}")
for alpha in (0.02, 0.01, 0.005, 0.002, 0.001):
    killed = usable[usable.param_p < alpha]
    lost = killed[killed.perm_p >= 0.05]
    closest = f"{lost.perm_p.max():.3f}" if len(lost) else "-"
    print(f"{alpha:>8}{len(killed):>15} ({len(killed)/len(usable):.0%})"
          f"{len(lost):>18}{closest:>21}")

# cascade savings: a screened-out level also spares every deeper
# permutation test of the same (item_set, pair) ladder
print("\ncascade savings estimate (permutation tests avoided incl. deeper levels):")
usable['combo'] = usable.scale + '|' + usable.pair + '|' + usable.n_items.astype(str)
key = usable.sort_values('level')
for alpha in (0.01, 0.005, 0.001):
    avoided = 0
    for _, g in key.groupby(['scale', 'pair', 'n_items'], observed=True):
        fail_ix = np.where(g.param_p.values < alpha)[0]
        if len(fail_ix):
            avoided += len(g) - fail_ix[0]
    print(f"  alpha={alpha}: ~{avoided}/{len(usable)} permutation tests avoided "
          f"({avoided/len(usable):.0%})")
