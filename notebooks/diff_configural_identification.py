#!/usr/bin/env python
"""Diff the free-parameter structure between plain cfa() configural and
measEq.syntax (Wu & Estabrook 2016) configural, to document WHY their
degrees of freedom differ.

Follow-up to check_invariance_dfs_v2.py after finding that plain and
measEq dfs differ at every level including configural. This script shows
where the difference lives: for each parameter class (loadings, thresholds,
intercepts, (residual) variances, latent means/variances) it counts free
vs fixed parameters per group under each identification scheme, prints a
side-by-side table, and lists the specific parameters whose free/fixed
status differs.

No permutation tests; a couple of model fits per scale, seconds each.

Usage (from the notebooks/ directory, inside pixi):

    pixi run python diff_configural_identification.py insomnia
    pixi run python diff_configural_identification.py --pair val_gp panic
    pixi run python diff_configural_identification.py            # all scales, summary only
    pixi run python diff_configural_identification.py --level metric insomnia
"""
import argparse
import os
import sys
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import pandas as pd            # noqa: E402
import rpy2.robjects as ro     # noqa: E402
from rpy2.robjects import pandas2ri  # noqa: E402
from rpy2.robjects.conversion import localconverter  # noqa: E402
from rpy2.robjects.packages import importr  # noqa: E402

lavaan = importr('lavaan')
semtools = importr('semTools')

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

# group.equal sets per level under each scheme (None = configural)
PLAIN_LEVELS = {
    'configural': None,
    'metric': '"loadings"',
    'scalar': 'c("loadings", "intercepts")',
    'strict': 'c("loadings", "intercepts", "residuals")',
}
MEASEQ_LEVELS = {
    'configural': None,
    'thresholds': ('thresholds',),
    'metric': ('thresholds', 'loadings'),
    'scalar': ('thresholds', 'loadings', 'intercepts'),
    'strict': ('thresholds', 'loadings', 'intercepts', 'residuals'),
}


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


def push_data(formula, data, temp_path):
    ro.globalenv['testformula_r'] = formula
    data.to_csv(temp_path)
    ro.r(f'rdata <- read.csv("{temp_path}", header = TRUE)')


def fit_plain(items, level, parameterization="theta"):
    ordered_str = 'c(' + ', '.join(f'"{i}"' for i in items) + ')'
    cmd = (f'fit_tmp <- cfa(testformula_r, data = rdata, group = "whichdata", '
           f'estimator = "WLSMV", parameterization = "{parameterization}", '
           f'ordered = {ordered_str}')
    ge = PLAIN_LEVELS[level]
    if ge is not None:
        cmd += f', group.equal = {ge}'
    ro.r(cmd + ')')


def fit_measeq(items, level, parameterization="theta",
               id_fac="auto.fix.first"):
    ordered_str = 'c(' + ', '.join(f'"{i}"' for i in items) + ')'
    ge = MEASEQ_LEVELS[level]
    ge_str = ''
    if ge:
        ge_str = 'group.equal = c(' + ', '.join(f'"{g}"' for g in ge) + '), '
    ro.r(f'''
        measeq_mod <- semTools::measEq.syntax(
            configural.model = testformula_r,
            data = rdata, group = "whichdata",
            ordered = {ordered_str},
            parameterization = "{parameterization}",
            estimator = "WLSMV",
            ID.fac = "{id_fac}",
            ID.cat = "Wu.Estabrook.2016",
            {ge_str}return.fit = FALSE)
        measeq_mod_str <- as.character(measeq_mod)
        fit_tmp <- lavaan::cfa(measeq_mod_str, data = rdata,
                               group = "whichdata", ordered = {ordered_str},
                               parameterization = "{parameterization}",
                               estimator = "WLSMV")
    ''')


def get_partable():
    """Pull the current fit_tmp parTable into pandas."""
    ro.r('pt_tmp <- lavaan::parTable(fit_tmp)')
    pt_r = ro.r('pt_tmp')
    with localconverter(ro.default_converter + pandas2ri.converter):
        pt = ro.conversion.rpy2py(pt_r)
    return pt


def classify(pt, factor_name):
    """Add a 'pclass' column: loading / threshold / intercept /
    resid_var / lat_var / lat_mean / scale / other."""
    def _cls(row):
        op, lhs, rhs = row['op'], row['lhs'], row['rhs']
        if op == '=~':
            return 'loading'
        if op == '|':
            return 'threshold'
        if op == '~1':
            return 'lat_mean' if lhs == factor_name else 'intercept'
        if op == '~~' and lhs == rhs:
            return 'lat_var' if lhs == factor_name else 'resid_var'
        if op == '~*~':
            return 'scale_factor'
        return 'other'
    pt = pt.copy()
    pt['pclass'] = pt.apply(_cls, axis=1)
    return pt


def summarize(pt):
    """free/fixed counts by (pclass, group). Rows with group==0 are
    equality-constraint bookkeeping; keep only group>0."""
    pt = pt[pt['group'] > 0]
    out = (pt.assign(is_free=pt['free'] > 0)
             .groupby(['pclass', 'group'])['is_free']
             .agg(free='sum', total='count')
             .reset_index())
    out['fixed'] = out['total'] - out['free']
    return out


def df_and_npar():
    df = float(ro.r('fitMeasures(fit_tmp, "df")')[0])
    npar = float(ro.r('lavInspect(fit_tmp, "npar")')[0])
    return df, npar


def compare_scale(scale, data, temp_path, level, parameterization,
                  detail=True):
    formula = ORIG_ITEMS[scale]
    items = [s.strip() for s in formula.split("=~", 1)[1].split("+")]
    factor = formula.split("=~", 1)[0].strip()
    push_data(formula, data, temp_path)

    print(f"\n{'='*72}\n{scale} ({len(items)} items) -- level: {level}\n{'='*72}")

    fit_plain(items, level, parameterization)
    df_p, np_p = df_and_npar()
    pt_p = classify(get_partable(), factor)
    sum_p = summarize(pt_p)

    fit_measeq(items, level, parameterization)
    df_m, np_m = df_and_npar()
    pt_m = classify(get_partable(), factor)
    sum_m = summarize(pt_m)

    print(f"plain : df = {df_p:.0f}, npar = {np_p:.0f}")
    print(f"measEq: df = {df_m:.0f}, npar = {np_m:.0f}   "
          f"(d_df = {df_m - df_p:+.0f}, d_npar = {np_m - np_p:+.0f})")

    merged = pd.merge(
        sum_p, sum_m, on=['pclass', 'group'], how='outer',
        suffixes=('_plain', '_measeq')).fillna(0)
    order = ['loading', 'threshold', 'intercept', 'resid_var',
             'scale_factor', 'lat_var', 'lat_mean', 'other']
    merged['_o'] = merged['pclass'].map({c: i for i, c in enumerate(order)})
    merged = merged.sort_values(['_o', 'group']).drop(columns='_o')

    print(f"\n{'class':<14}{'grp':>4} | {'plain free/tot':>15} | "
          f"{'measEq free/tot':>16} | note")
    for _, r in merged.iterrows():
        fp, tp = int(r['free_plain']), int(r['total_plain'])
        fm, tm = int(r['free_measeq']), int(r['total_measeq'])
        note = ''
        if fp != fm:
            note = f"free differs ({fm - fp:+d})"
        elif tp != tm:
            note = f"param count differs ({tm - tp:+d})"
        print(f"{r['pclass']:<14}{int(r['group']):>4} | "
              f"{fp:>7d}/{tp:<7d} | {fm:>8d}/{tm:<7d} | {note}")

    if detail:
        # list individual parameters whose free-status differs
        key = ['lhs', 'op', 'rhs', 'group']
        p = pt_p[pt_p['group'] > 0][key + ['free', 'ustart', 'pclass']]
        m = pt_m[pt_m['group'] > 0][key + ['free', 'ustart']]
        both = pd.merge(p, m, on=key, how='outer',
                        suffixes=('_plain', '_measeq'),
                        indicator=True)
        both['free_plain'] = both['free_plain'].fillna(-1)
        both['free_measeq'] = both['free_measeq'].fillna(-1)
        diff = both[
            ((both['free_plain'] > 0) != (both['free_measeq'] > 0)) |
            (both['_merge'] != 'both')]
        if len(diff):
            print(f"\nParameters whose free/fixed status differs "
                  f"({len(diff)} rows; free=-1 means absent from that model):")
            with pd.option_context('display.max_rows', 200,
                                   'display.width', 120):
                cols = ['lhs', 'op', 'rhs', 'group', 'pclass',
                        'free_plain', 'ustart_plain',
                        'free_measeq', 'ustart_measeq']
                cols = [c for c in cols if c in diff.columns]
                print(diff[cols].to_string(index=False))
        else:
            print("\nNo individual parameter differs in free/fixed status "
                  "(difference must come from equality labels/constraints).")

    return dict(scale=scale, df_plain=df_p, df_measeq=df_m,
                npar_plain=np_p, npar_measeq=np_m)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scales', nargs='*', default=[],
                    help='scales to diff (default: all, summary table only)')
    ap.add_argument('--pair', default='gp_en',
                    choices=['val_gp', 'val_en', 'gp_en'])
    ap.add_argument('--data-dir', default='../data/finaldata')
    ap.add_argument('--temp', default='./ident_diff_temp.csv')
    ap.add_argument('--parameterization', default='theta',
                    choices=['theta', 'delta'])
    ap.add_argument('--level', default='configural',
                    choices=list(PLAIN_LEVELS),
                    help='which level to diff (measEq side uses its own '
                         'cumulative set for the same label; default '
                         'configural)')
    ap.add_argument('--id-fac', default='auto.fix.first',
                    help='measEq.syntax ID.fac (try std.lv to see whether '
                         'the df gap is an ID.fac artifact)')
    args = ap.parse_args()

    scales = args.scales or list(ORIG_ITEMS)
    unknown = [s for s in scales if s not in ORIG_ITEMS]
    if unknown:
        sys.exit(f"unknown scale(s): {unknown}")

    # per-scale parameter detail only when explicitly given scales;
    # full-sweep mode prints the summary table only
    detail = bool(args.scales)

    print(f"pair={args.pair} level={args.level} "
          f"parameterization={args.parameterization} ID.fac={args.id_fac}")
    data = load_pair(args.data_dir, args.pair)
    print(f"loaded {len(data)} rows")

    global fit_measeq
    _orig_fit_measeq = fit_measeq
    if args.id_fac != 'auto.fix.first':
        def fit_measeq(items, level, parameterization="theta",  # noqa: F811
                       id_fac=args.id_fac):
            return _orig_fit_measeq(items, level, parameterization, id_fac)

    rows = []
    for scale in scales:
        try:
            rows.append(compare_scale(scale, data, args.temp, args.level,
                                      args.parameterization, detail=detail))
        except Exception as e:
            print(f"\n{scale}: FAILED ({e})")

    if len(rows) > 1:
        print(f"\n{'='*72}\nSUMMARY ({args.level})\n{'='*72}")
        print(f"{'scale':<24}{'df_plain':>9}{'df_measEq':>10}{'d_df':>6}"
              f"{'npar_pl':>9}{'npar_mE':>9}{'d_np':>6}")
        for r in rows:
            print(f"{r['scale']:<24}{r['df_plain']:>9.0f}"
                  f"{r['df_measeq']:>10.0f}"
                  f"{r['df_measeq']-r['df_plain']:>+6.0f}"
                  f"{r['npar_plain']:>9.0f}{r['npar_measeq']:>9.0f}"
                  f"{r['npar_measeq']-r['npar_plain']:>+6.0f}")


if __name__ == '__main__':
    main()
