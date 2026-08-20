#!/usr/bin/env python
"""Headless per-scale exhaustive invariant-subset search (HPC entry point).

Runs exhaustive_search_scale for ONE scale -- the unit of HPC parallelism
(one SLURM array task per scale). Progress persists to
{cfa_dir}/exhaustive_progress_{scale}.pkl exactly as in the exploratory
notebook, so results transfer back by copying that pickle into the local
data/cfa/: the notebook's search loop then short-circuits the completed
scale and re-prints its results into the parsed log.

REPRODUCIBILITY: permuteMeasEq's L'Ecuyer RNG streams are split by worker
count, so the permutation p for a given test depends on --cpus. The whole
pipeline was run with 14 workers; keep --cpus 14 (the default) on HPC so
every test is bit-identical to the local pipeline. Request at least 14
CPUs per task.

Examples (inside the container):
    python run_exhaustive_scale.py anhedonic_depression \
        --data-dir /data/finaldata --cfa-dir /data/cfa --num-iter 1000
    python run_exhaustive_scale.py gad_sum --scale-set other \
        --data-dir /data/finaldata --cfa-dir /data/cfa
"""
import argparse
import os
import sys
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import pandas as pd

from hitop_cfa import exhaustive_search_scale, stepwise_configural_cap
from hitop_cfa.scales import ORIG_ITEMS, OTHER_SCALES


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scale', help='scale name (see hitop_cfa.scales)')
    ap.add_argument('--scale-set', choices=['hitop', 'other'], default=None,
                    help='hitop = 3-way search over the HiTOP scales; '
                         'other = gp_en-only search over PHQ/GAD/BAARS. '
                         'Inferred from the scale name when omitted.')
    ap.add_argument('--whichcfa', default='scalar')
    ap.add_argument('--num-iter', type=int, default=1000)
    ap.add_argument('--cpus', type=int, default=14,
                    help='permuteMeasEq workers. KEEP 14 for bit-identical '
                         'results with the local pipeline (RNG streams are '
                         'split by worker count).')
    ap.add_argument('--data-dir', default='../data/finaldata')
    ap.add_argument('--cfa-dir', default='../data/cfa')
    ap.add_argument('--min-items', type=int, default=3)
    ap.add_argument('--alpha-screen', type=float, default=0.005)
    ap.add_argument('--no-cap', action='store_true',
                    help='ignore the stepwise configural-certificate size cap')
    args = ap.parse_args()

    scale_set = args.scale_set
    if scale_set is None:
        scale_set = 'hitop' if args.scale in ORIG_ITEMS else 'other'
    formulas = ORIG_ITEMS if scale_set == 'hitop' else OTHER_SCALES
    if args.scale not in formulas:
        sys.exit(f"unknown scale {args.scale!r} for scale set {scale_set!r}; "
                 f"choose from {list(formulas)}")

    data_dir = Path(args.data_dir)
    cfa_dir = Path(args.cfa_dir)
    cfa_dir.mkdir(parents=True, exist_ok=True)

    val = pd.read_csv(data_dir / 'dat_val.csv')
    gp = pd.read_csv(data_dir / 'dat_gp_grid1st_full.csv')
    en = pd.read_csv(data_dir / 'dat_en_grid1st_full.csv')
    if scale_set == 'hitop':
        # ORDER MATTERS: val_gp first (most-lethal pair -> early abandon)
        datasets = {'val_gp': pd.concat([val, gp]),
                    'val_en': pd.concat([val, en]),
                    'gp_en': pd.concat([gp, en])}
    else:
        datasets = {'gp_en': pd.concat([gp, en])}

    items = formulas[args.scale].split('=~', 1)[1].strip().split(' + ')
    n = len(items)
    cap = None
    if scale_set == 'hitop' and not args.no_cap:
        cap = stepwise_configural_cap(cfa_dir, args.scale, n)
        print(f'stepwise configural certificate cap: {cap}')

    temp_dir = cfa_dir / 'temp'
    temp_dir.mkdir(exist_ok=True)
    # per-scale temp csv so parallel array tasks sharing cfa_dir never collide
    temp_path = temp_dir / f'cfa_temp_{args.scale}.csv'

    print(f'scale={args.scale} ({n} items, {scale_set}) whichcfa={args.whichcfa} '
          f'num_iter={args.num_iter} cpus={args.cpus} alpha_screen={args.alpha_screen}')
    successes, success_size = exhaustive_search_scale(
        whichscale=args.scale,
        whichcfa=args.whichcfa,
        orig_items=formulas,
        datasets=datasets,
        temp_path=temp_path,
        num_iter=args.num_iter,
        cpus_to_use=args.cpus,
        min_items=args.min_items,
        max_size=cap,
        alpha_screen=args.alpha_screen,
        progress_path=cfa_dir / f'exhaustive_progress_{args.scale}.pkl',
    )
    if successes:
        # same print pattern the notebook's parse cells read
        print(f'\n!!!!! Found at least one invariant subset for SCALE {args.scale} with ITEMS = {success_size} (removing {n - success_size} items)\n')
        print(successes)
    else:
        print(f'\nno invariant subset found for {args.scale}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
