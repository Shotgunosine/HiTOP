#!/usr/bin/env python
"""Smoke test for the measEq (Wu & Estabrook 2016) invariance pipeline.

Handoff task 6 (HANDOFF_measeq_fix.md): ONE scale (insomnia), num_iter=50,
exercising the full ladder end-to-end through BOTH stepwise stages (metric
search, then scalar continuation), asserting the validated df formulas from
the task-1 validation (k items, 2 groups, 4 categories, std.lv W&E):

    configural -> thresholds : +k
    thresholds -> metric     : +(k-1)
    metric     -> scalar     : +(k-1)
    scalar     -> strict     : +k

Steps:
  1. df ladder: fit all 5 measEq levels on each dataset pair (no
     permutations) and assert the deltas above.
  2. run_specific_cfa whichcfa='strict' on the GP_EN pair (fit.py's
     5-level ladder with permutation tests + assert_level_adds_df).
  3. do_three_way_cfa_stepwise_mi on all three pairs (metric search);
     history pickle saved with the notebook's naming convention.
  4. do_stepwise_scalar_from_metric_run resuming from that pickle
     (scalar continuation, exercising load_metric_run + skip-lower).

Sanity guards (stop-and-report conditions from the handoff): extract_p
must return numeric strings (or 'NA' for untested levels) and every MI
dict recorded in the histories must be keyed by item names, not plabels.

Run from notebooks/ inside pixi:

    pixi run python smoke_test_measeq.py

Outputs (temp csv + pickles) go to ./log/smoke_measeq/. This is a smoke
test only -- num_iter=50 p-values are coarse; the df assertions are the
ground truth, the p-values are reported for eyeballing.
"""
import os
import platform
import sys
import traceback
from pathlib import Path

# BLAS threading must be pinned before rpy2 starts R (rpy2 issue #882)
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import pandas as pd  # noqa: E402

from hitop_cfa import (  # noqa: E402  (import starts the embedded R session)
    WU_ESTABROOK_LEVELS,
    assert_level_adds_df,
    do_stepwise_scalar_from_metric_run,
    do_three_way_cfa_stepwise_mi,
    fit_measeq_level,
    run_specific_cfa,
)
from hitop_cfa.fit import push_model_to_r  # noqa: E402
from hitop_cfa.r_env import ro  # noqa: E402

SCALE = 'insomnia'
FORMULA = 'insomnia =~hitop160 + hitop254 + hitop261 + hitop268'
ITEMS = [s.strip() for s in FORMULA.split("=~", 1)[1].split("+")]
K = len(ITEMS)
NUM_ITER = 50

# validated df arithmetic (handoff task 1)
EXPECTED_DELTAS = {
    ('configural', 'thresholds'): K,
    ('thresholds', 'metric'):     K - 1,
    ('metric', 'scalar'):         K - 1,
    ('scalar', 'strict'):         K,
}

HERE = Path(__file__).parent
DATA_DIR = HERE / '..' / 'data' / 'finaldata'
OUT_DIR = HERE / 'log' / 'smoke_measeq'
OUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_CSV = OUT_DIR / 'smoke_temp.csv'


def get_cpus():
    arch = platform.machine().lower()
    total = os.cpu_count()
    if 'arm' in arch or 'aarch' in arch:
        return total - 2
    return total // 2 - 1


def check_p_string(p, label, allow_na=True):
    """extract_p returning something non-numeric (other than 'NA' for an
    untested level) is a stop-and-report condition."""
    if p == 'NA':
        if allow_na:
            return None
        raise RuntimeError(f"{label}: unexpected 'NA' p-value")
    try:
        return float(p)
    except (TypeError, ValueError):
        raise RuntimeError(
            f"STOP-AND-REPORT: extract_p returned non-numeric {p!r} for "
            f"{label} -- the permuteMeasEq x measEq.syntax summary parse "
            f"broke.")


def check_mi_keys(history, stage):
    """Every recorded MI dict must be keyed by item names, not plabels."""
    if 'mis_used' not in history.columns:
        return
    for mis in history['mis_used'].dropna():
        if not isinstance(mis, dict) or not mis:
            continue
        bad = [k for k in mis if k not in ITEMS]
        if bad:
            raise RuntimeError(
                f"STOP-AND-REPORT: {stage} MI extractor returned non-item "
                f"keys {bad} (expected subset of {ITEMS}) -- plabel/NA "
                f"mapping broke.")
        print(f"  [{stage}] MI dict keys OK: {sorted(mis)}")


FAILURES = []


def run_step(label, fn):
    """Run one smoke step; on failure record it, print the traceback, and
    keep going so the remaining steps still produce evidence."""
    try:
        return fn()
    except Exception:
        print(f"\n!!! {label} FAILED:")
        traceback.print_exc(file=sys.stdout)
        FAILURES.append(label)
        return None


def main():
    cpus = get_cpus()
    print(f"Smoke test: scale={SCALE}, k={K}, num_iter={NUM_ITER}, "
          f"cpus={cpus}")

    data_val = pd.read_csv(DATA_DIR / 'dat_val.csv')
    data_gp = pd.read_csv(DATA_DIR / 'dat_gp_grid1st_full.csv')
    data_en = pd.read_csv(DATA_DIR / 'dat_en_grid1st_full.csv')
    pairs = {
        'val_gp': pd.concat([data_val, data_gp]),
        'val_en': pd.concat([data_val, data_en]),
        'gp_en':  pd.concat([data_gp, data_en]),
    }

    # ------------------------------------------------------------------
    print(f"\n{'='*64}\nSTEP 1: df ladder (all 5 measEq levels, each pair, "
          f"no permutations)\n{'='*64}")
    for pair, data in pairs.items():
        print(f"\n[{pair}]")
        push_model_to_r(SCALE, ITEMS, data, TEMP_CSV)
        dfs = {}
        for level, group_equal in WU_ESTABROOK_LEVELS:
            fit_measeq_level(ITEMS, group_equal=group_equal,
                             r_fit_name=f'fit_{level}')
            dfs[level] = float(
                ro.r(f'lavaan::fitMeasures(fit_{level}, "df")')[0])
        names = [lv for lv, _ in WU_ESTABROOK_LEVELS]
        line = "  ".join(f"{lv}={dfs[lv]:.0f}" for lv in names)
        print(f"  df ladder: {line}")
        for lo, hi in zip(names, names[1:]):
            # assert_level_adds_df is the production guard; the equality
            # check below is the smoke test's stricter ground truth
            delta = assert_level_adds_df(f'fit_{lo}', f'fit_{hi}', lo, hi)
            expected = EXPECTED_DELTAS[(lo, hi)]
            status = "OK" if delta == expected else "MISMATCH"
            print(f"  {lo} -> {hi}: d_df={delta:+.0f} "
                  f"(expected +{expected}) {status}")
            assert delta == expected, (
                f"{pair}: df({hi}) - df({lo}) = {delta}, expected "
                f"{expected} (k={K})")
    print("\nSTEP 1 PASSED: all df deltas match the validated formulas "
          "on all three pairs.")

    # ------------------------------------------------------------------
    print(f"\n{'='*64}\nSTEP 2: run_specific_cfa full ladder with "
          f"permutations (GP_EN pair)\n{'='*64}")

    def step2_fn():
        res = run_specific_cfa(
            whichscale=SCALE, item_list=ITEMS, whichcfa='strict',
            datasets={'GP_EN': pairs['gp_en']}, temp_path=TEMP_CSV,
            num_iter=NUM_ITER, cpus_to_use=cpus, return_vals=True)
        row = res[0]
        for level in ('pconfig', 'pthresholds', 'pmetric', 'pscalar',
                      'pstrict'):
            check_p_string(row[level], f"run_specific_cfa {level}")
        print(f"\nSTEP 2 p-values: {row}")
        return row

    step2 = run_step('STEP 2 (run_specific_cfa strict ladder)', step2_fn)

    # ------------------------------------------------------------------
    print(f"\n{'='*64}\nSTEP 3: stepwise metric search (3 pairs)\n{'='*64}")

    def step3_fn():
        final, removed, history = do_three_way_cfa_stepwise_mi(
            SCALE, orig_items={SCALE: FORMULA}, datasets=pairs,
            temp_path=TEMP_CSV, num_iter=NUM_ITER, cpus_to_use=cpus,
            min_items=3)
        check_mi_keys(history, 'metric-stage')
        for col in history.columns:
            if col.endswith('_p'):
                for v in history[col].dropna():
                    if not isinstance(v, float):
                        raise RuntimeError(
                            f"STOP-AND-REPORT: non-float p in history col "
                            f"{col}: {v!r}")
        print(f"\nSTEP 3 result: final={final} removed={removed}")
        # persist with the notebook's naming convention so step 4 can resume
        history['scale'] = SCALE
        history.to_pickle(OUT_DIR / f'{SCALE}_history.pkl')
        return final, removed, history

    step3 = run_step('STEP 3 (stepwise metric search)', step3_fn)

    # ------------------------------------------------------------------
    print(f"\n{'='*64}\nSTEP 4: scalar continuation from the metric run"
          f"\n{'='*64}")

    def step4_fn():
        final, removed, history = do_stepwise_scalar_from_metric_run(
            SCALE, OUT_DIR, datasets=pairs, temp_path=TEMP_CSV,
            num_iter=NUM_ITER, cpus_to_use=cpus, min_items=3)
        check_mi_keys(history, 'scalar-stage')
        history['scale'] = SCALE
        history.to_pickle(OUT_DIR / f'{SCALE}_scalar_history.pkl')
        print(f"\nSTEP 4 result: final={final} removed={removed}")
        return final, removed, history

    step4 = run_step('STEP 4 (scalar continuation)', step4_fn)

    # ------------------------------------------------------------------
    print(f"\n{'='*64}\nSMOKE TEST SUMMARY\n{'='*64}")
    print(f"df formulas: PASSED on all pairs "
          f"(+{K}, +{K-1}, +{K-1}, +{K} for k={K})")
    if step2 is not None:
        print(f"run_specific_cfa (GP_EN): {step2}")
    if step3 is not None:
        print(f"metric stepwise: core={step3[0]}, removed={step3[1]}")
    if step4 is not None:
        print(f"scalar continuation: core={step4[0]}, removed={step4[1]}")
        scalar_history = step4[2]
        main_rows = scalar_history[scalar_history.get('phase') == 'main']
        if len(main_rows):
            pcols = [c for c in main_rows.columns if c.endswith('_p')]
            print("scalar-stage per-pair p-values (main rows):")
            print(main_rows[['iteration', 'n_items', 'action'] + pcols]
                  .to_string(index=False))
    if FAILURES:
        print(f"\nSMOKE TEST FAILED in: {FAILURES}")
        return 1
    print("\nSMOKE TEST COMPLETE")
    return 0


if __name__ == '__main__':
    sys.exit(main())
