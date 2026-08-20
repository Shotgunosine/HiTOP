#!/usr/bin/env python
"""Check whether the scalar and strict invariance tests actually add
testable constraints (degrees of freedom) for ordinal WLSMV models.

Diagnosis for: permutation p = 1.0 at strict for everything that passes
scalar. If df(strict) == df(scalar), the strict comparison is vacuous
(delta-chi-square identically 0). Same logic checks metric -> scalar.

No permutation tests are run -- this only fits the four lavaan models per
scale and inspects df / free-parameter counts, so it takes seconds per
scale.

Usage (from the notebooks/ directory of the HiTOP repo, inside pixi):

    pixi run python check_invariance_dfs.py                  # all scales, gp_en pair
    pixi run python check_invariance_dfs.py insomnia panic   # specific scales
    pixi run python check_invariance_dfs.py --pair val_gp insomnia
    pixi run python check_invariance_dfs.py --data-dir /path/to/data/finaldata insomnia

Expected df jumps for a 2-group, 1-factor model with k items, 4 response
categories (3 thresholds/item), theta parameterization, marker
identification, IF each level constrains what it claims to:

    configural -> metric:  +(k - 1)          [loadings; marker already =1]
    metric -> scalar:      +~3k - (a few)    [thresholds, minus identification]
    scalar -> strict:      +(k or k - 1)     [residual variances]

If metric->scalar shows ~+3k-ish, scalar genuinely constrained thresholds.
If scalar->strict shows +0, strict was vacuous (the p = 1.0 explanation).
If metric->scalar also shows +0, scalar was vacuous too.
"""
import argparse
import os
import sys
from pathlib import Path

# BLAS threading must be pinned before rpy2 starts R (rpy2 issue #882)
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import pandas as pd            # noqa: E402
import rpy2.robjects as ro     # noqa: E402
from rpy2.robjects.packages import importr  # noqa: E402

lavaan = importr('lavaan')

ORIG_ITEMS = {
    'anhedonic_depression': 'anhedonic_depression =~hitop39 + hitop77 + hitop84 + hitop92 + hitop93 + hitop123 + hitop157 + hitop182 + hitop230 + hitop246',
    'anxious_worry': 'anxious_worry =~hitop20 + hitop34 + hitop89 + hitop203 + hitop240 + hitop248 + hitop265',
    'appetite_gain': 'appetite_gain =~hitop120 + hitop141 + hitop243 + hitop275',
    'appetite_loss': 'appetite_loss =~hitop280 + hitop283 + hitop109',
    'cognitive_problems': 'cognitive_problems =~hitop67 + hitop159 + hitop189 + hitop142',
    'hyposomnia': 'hyposomnia =~hitop99 + hitop181 + hitop5 + hitop66 + hitop231',
    'indecisiveness': 'indecisiveness =~hitop21 + hitop90 + hitop95',
    'insomnia': 'insomnia =~hitop160 + hitop254 + hitop261 + hitop268',
    'panic': 'panic =~hitop15 + hitop104 + hitop126 + hitop211 + hitop215 + hitop257',
    'separation_insecurity': 'separation_insecurity =~hitop40 + hitop50 + hitop69 + hitop81 + hitop113 + hitop136 + hitop151 + hitop197',
    'shame_guilt': 'shame_guilt =~hitop72 + hitop140 + hitop143 + hitop220',
    'situational_phobia': 'situational_phobia =~hitop16 + hitop165 + hitop225 + hitop247 + hitop278',
    'social_anxiety': 'social_anxiety =~hitop1 + hitop17 + hitop114 + hitop117 + hitop124 + hitop129 + hitop204 + hitop222 + hitop236 + hitop258',
    'well_being': 'well_being =~hitop9 + hitop23 + hitop54 + hitop106 + hitop149 + hitop200 + hitop244 + hitop245 + hitop250 + hitop281',
}

LEVELS = [
    ('configural', None),
    ('metric', '"loadings"'),
    ('scalar', 'c("loadings", "intercepts")'),
    ('strict', 'c("loadings", "intercepts", "residuals")'),
]


def load_pair(data_dir, pair):
    data_dir = Path(data_dir)
    val = data_dir / 'dat_val.csv'
    gp = data_dir / 'dat_gp_grid1st_full.csv'
    en = data_dir / 'dat_en_grid1st_full.csv'
    if pair == 'val_gp':
        return pd.concat([pd.read_csv(val), pd.read_csv(gp)])
    if pair == 'val_en':
        return pd.concat([pd.read_csv(val), pd.read_csv(en)])
    if pair == 'gp_en':
        return pd.concat([pd.read_csv(gp), pd.read_csv(en)])
    raise ValueError(f"unknown pair {pair!r}")


def fit_level(formula, items, group_equal, parameterization="theta"):
    """Fit one multigroup WLSMV model; return (df, npar, chisq) as floats."""
    ordered_str = 'c(' + ', '.join(f'"{i}"' for i in items) + ')'
    cmd = (f'cfa(testformula_r, data = rdata, group = "whichdata", '
           f'estimator = "WLSMV", parameterization = "{parameterization}", '
           f'ordered = {ordered_str}')
    if group_equal is not None:
        cmd += f', group.equal = {group_equal}'
    cmd += ')'
    fit = ro.r(cmd)
    ro.globalenv['fit_tmp'] = fit
    df = float(ro.r('fitMeasures(fit_tmp, "df")')[0])
    npar = float(ro.r('lavInspect(fit_tmp, "npar")')[0])
    chisq = float(ro.r('fitMeasures(fit_tmp, "chisq.scaled")')[0])
    return df, npar, chisq


def inspect_free_params(label):
    """Print which parameter classes are free/fixed per group for fit_tmp."""
    ro.r('''
        pt <- parTable(fit_tmp)
        res  <- pt[pt$op == "~~" & pt$lhs == pt$rhs & pt$lhs != pt$rhs[0], ]
        resid <- pt[pt$op == "~~" & pt$lhs == pt$rhs, ]
        thr  <- pt[pt$op == "|", ]
        ints <- pt[pt$op == "~1", ]
        cat(sprintf("    residual variances: %d free / %d total\\n",
                    sum(resid$free > 0), nrow(resid)))
        cat(sprintf("    thresholds:         %d free / %d total, %d cross-group equality labels\\n",
                    sum(thr$free > 0), nrow(thr),
                    sum(duplicated(thr$label[thr$label != ""]))))
        cat(sprintf("    intercepts (~1):    %d free / %d total\\n",
                    sum(ints$free > 0), nrow(ints)))
    ''')


def check_scale(scale, data, temp_path, parameterization="theta",
                verbose_params=False):
    formula = ORIG_ITEMS[scale]
    items = [s.strip() for s in formula.split("=~", 1)[1].split("+")]
    k = len(items)

    ro.globalenv['testformula_r'] = formula
    data.to_csv(temp_path)
    ro.r(f'rdata <- read.csv("{temp_path}", header = TRUE)')

    print(f"\n{'='*64}\n{scale}  ({k} items, 4 response categories assumed)\n{'='*64}")
    print(f"{'level':<12}{'df':>8}{'npar':>8}{'chisq':>12}{'d_df':>8}{'d_npar':>8}")

    prev_df = prev_npar = None
    dfs = {}
    for level, group_equal in LEVELS:
        try:
            df, npar, chisq = fit_level(formula, items, group_equal,
                                        parameterization)
        except Exception as e:
            print(f"{level:<12}  FIT FAILED: {e}")
            return None
        d_df = '' if prev_df is None else f"{df - prev_df:+.0f}"
        d_np = '' if prev_npar is None else f"{npar - prev_npar:+.0f}"
        print(f"{level:<12}{df:>8.0f}{npar:>8.0f}{chisq:>12.2f}{d_df:>8}{d_np:>8}")
        if verbose_params:
            inspect_free_params(level)
        dfs[level] = df
        prev_df, prev_npar = df, npar

    print(f"\nExpected if constraints are real "
          f"(k={k}, 3 thresholds/item, marker ID):")
    print(f"  config->metric : +{k - 1:d}  (loadings)")
    print(f"  metric->scalar : ~+{3 * k - 4:d} to +{3 * k:d}  (thresholds)")
    print(f"  scalar->strict : +{k - 1:d} or +{k:d}  (residual variances)")

    verdicts = []
    if dfs['metric'] - dfs['configural'] <= 0:
        verdicts.append("METRIC VACUOUS (d_df <= 0) -- unexpected, investigate")
    if dfs['scalar'] - dfs['metric'] <= 0:
        verdicts.append("SCALAR VACUOUS: 'intercepts' constrained nothing real")
    elif dfs['scalar'] - dfs['metric'] < k:
        verdicts.append(f"SCALAR PARTIAL: d_df={dfs['scalar']-dfs['metric']:.0f} "
                        f"is well below ~3k; check whether thresholds were "
                        f"constrained (op '|') or only phantom intercepts")
    if dfs['strict'] - dfs['scalar'] <= 0:
        verdicts.append("STRICT VACUOUS: explains permutation p = 1.0")

    if not verdicts:
        verdicts.append("All levels add df; constraints appear real.")
    for v in verdicts:
        print(f"  >> {v}")
    return dfs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scales', nargs='*', default=[],
                    help='scales to check (default: all)')
    ap.add_argument('--pair', default='gp_en',
                    choices=['val_gp', 'val_en', 'gp_en'],
                    help='which dataset pair to fit (default gp_en)')
    ap.add_argument('--data-dir', default='../data/finaldata',
                    help='directory with dat_val.csv etc. '
                         '(default ../data/finaldata, i.e. run from notebooks/)')
    ap.add_argument('--temp', default='./df_check_temp.csv',
                    help='scratch csv for the python->R handoff')
    ap.add_argument('--parameterization', default='theta',
                    choices=['theta', 'delta'])
    ap.add_argument('--show-params', action='store_true',
                    help='also print free/fixed counts for residuals, '
                         'thresholds, and intercepts at each level')
    args = ap.parse_args()

    scales = args.scales or list(ORIG_ITEMS)
    unknown = [s for s in scales if s not in ORIG_ITEMS]
    if unknown:
        sys.exit(f"unknown scale(s): {unknown}; choose from {list(ORIG_ITEMS)}")

    print(f"pair={args.pair}  parameterization={args.parameterization}  "
          f"data_dir={args.data_dir}")
    data = load_pair(args.data_dir, args.pair)
    print(f"loaded {len(data)} rows")

    summary = {}
    for scale in scales:
        dfs = check_scale(scale, data, args.temp,
                          parameterization=args.parameterization,
                          verbose_params=args.show_params)
        if dfs is not None:
            summary[scale] = dfs

    if len(summary) > 1:
        print(f"\n{'='*64}\nSUMMARY (df by level)\n{'='*64}")
        print(f"{'scale':<24}{'config':>8}{'metric':>8}{'scalar':>8}{'strict':>8}"
              f"{'s-m':>6}{'st-s':>6}")
        for scale, dfs in summary.items():
            print(f"{scale:<24}{dfs['configural']:>8.0f}{dfs['metric']:>8.0f}"
                  f"{dfs['scalar']:>8.0f}{dfs['strict']:>8.0f}"
                  f"{dfs['scalar']-dfs['metric']:>6.0f}"
                  f"{dfs['strict']-dfs['scalar']:>6.0f}")


if __name__ == '__main__':
    main()
