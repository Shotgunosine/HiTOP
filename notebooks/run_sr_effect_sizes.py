#!/usr/bin/env python
"""Practical-impact effect sizes for the HiTOP-SR-composition subsets.

Applies the same machinery as NB_invariance_effect_sizes to the SR
subsets' invariance violations (data/cfa_sr_subsets/sr_cfa_res.csv, from
notebooks/run_sr_subsets.py):

1. For every subset x pair that fails full invariance, the metric-model
   DIF decomposition (hitop_cfa.effect_size.dif_effect_sizes): real
   latent severity gap vs DIF-induced score bias, per-item signed bias
   and dMACS, net and gross sum-score bias, 95% CIs from the robust
   parameter covariance. Where configural already fails (or does not
   converge) the metric model is an approximation / may not fit;
   non-convergence is recorded, not fatal.
2. For configural failures with >= 5 items, per-group polychoric EFA
   diagnostics and Schmid-Leiman dimensionality effect sizes
   (hitop_cfa.efa): phi, omegaH, criterion-correlation attenuation,
   required-n inflation. (3-4-item subsets are structurally excluded
   from the 2-factor check.)

Outputs (data/cfa_sr_subsets/):
    sr_dif_per_item.csv   mirrors data/effect_sizes/gp_pairwise_dif_per_item.csv
    sr_dif_summary.csv    mirrors data/effect_sizes/pairwise_dif_summary.csv
    sr_efa_summary.csv    mirrors data/effect_sizes/configural_efa_summary.csv
    sr_dimensionality.csv mirrors data/effect_sizes/dimensionality_effect_sizes.csv

Run inside pixi:  pixi run python notebooks/run_sr_effect_sizes.py
"""
import datetime
import sys
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from run_sr_subsets import SR_SUBSETS  # noqa: E402  (same directory)

FIN_DIR = ROOT / 'data' / 'finaldata'
OUT_DIR = ROOT / 'data' / 'cfa_sr_subsets'
LEVELS = ['configural', 'thresholds', 'metric', 'scalar', 'strict']
PCOLS = ['pconfig', 'pthresholds', 'pmetric', 'pscalar', 'pstrict']


def stamp(msg):
    print(f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}",
          flush=True)


def first_failing_level(row):
    """None means the cell passes strict. 'configural (nonconvergent)'
    marks a configural model that did not converge."""
    if pd.isna(row['pconfig']):
        return 'configural (nonconvergent)'
    for level, col in zip(LEVELS, PCOLS):
        p = row[col]
        if pd.isna(p):
            # ladder stopped earlier (previous level failed) -- shouldn't
            # reach here because the failure returns first; mid-ladder
            # non-convergence also lands here
            return f'{level} (nonconvergent)'
        if p < 0.05:
            return level
    return None


def main():
    from hitop_cfa.effect_size import dif_effect_sizes
    from hitop_cfa.efa import dimensionality_effect_sizes, polychoric_efa

    res = pd.read_csv(OUT_DIR / 'sr_cfa_res.csv')

    data_val = pd.read_csv(FIN_DIR / 'dat_val.csv')
    data_gp = pd.read_csv(FIN_DIR / 'dat_gp_grid1st_full.csv')
    data_en = pd.read_csv(FIN_DIR / 'dat_en_grid1st_full.csv')
    pairs = {
        'val_gp': pd.concat([data_val, data_gp]),
        'val_en': pd.concat([data_val, data_en]),
        'gp_en': pd.concat([data_gp, data_en]),
    }
    pair_label = {'V_GP': 'val_gp', 'V_EN': 'val_en', 'GP_EN': 'gp_en'}
    groups = {'validation': data_val, 'gp': data_gp, 'en': data_en}
    pair_groups = {'val_gp': ('validation', 'gp'),
                   'val_en': ('validation', 'en'),
                   'gp_en': ('gp', 'en')}

    temp_dir = OUT_DIR / 'temp'
    temp_dir.mkdir(exist_ok=True, parents=True)

    # ---- 1. DIF decomposition for every violation ----
    per_item_rows, summary_rows = [], []
    for _, r in res.iterrows():
        failed_at = first_failing_level(r)
        if failed_at is None:
            stamp(f'{r.scale} {r.pair}: passes strict -- no violation to size')
            continue
        pair = pair_label[r.pair]
        items = SR_SUBSETS[r.scale]['items']
        stamp(f'DIF effect sizes: {r.scale} x {pair} (failed at {failed_at})')
        base = dict(scale=r.scale, pair=pair, failed_at=failed_at,
                    n_items=len(items))
        try:
            per_item, summary = dif_effect_sizes(
                r.scale, items, pairs[pair],
                temp_dir / 'es_temp.csv', n_draws=1000)
        except Exception as exc:
            stamp(f'  ERROR: {exc!r}')
            traceback.print_exc()
            summary_rows.append(dict(base, error=repr(exc)))
            continue
        if per_item is None or not summary.get('converged', False):
            stamp('  metric model did not converge')
            summary_rows.append(dict(base, error='metric_nonconvergent'))
            continue
        pi = per_item.copy()
        pi.insert(0, 'pair', pair)
        pi.insert(0, 'scale', r.scale)
        per_item_rows.append(pi)
        summary_rows.append(dict(
            base,
            scale_max=summary['scale_max_points'],
            alpha=summary['alpha'],
            alpha_lo=summary['alpha_ci'][0], alpha_hi=summary['alpha_ci'][1],
            real_gap_pts=summary['real_gap_points'],
            net_bias_pts=summary['net_sum_bias_points'],
            net_lo=summary['net_ci'][0], net_hi=summary['net_ci'][1],
            gross_bias_pts=summary['gross_abs_bias_points'],
            gross_lo=summary['gross_ci'][0], gross_hi=summary['gross_ci'][1],
            max_dMACS=float(per_item['dMACS'].max()),
            max_dMACS_item=per_item.loc[per_item['dMACS'].idxmax(), 'item'],
            error='',
        ))
        # incremental saves
        pd.concat(per_item_rows).to_csv(OUT_DIR / 'sr_dif_per_item.csv',
                                        index=False)
        pd.DataFrame(summary_rows).to_csv(OUT_DIR / 'sr_dif_summary.csv',
                                          index=False)
    pd.DataFrame(summary_rows).to_csv(OUT_DIR / 'sr_dif_summary.csv',
                                      index=False)

    # ---- 2. Dimensionality for configural failures ----
    config_fail = res.assign(
        failed=[first_failing_level(r) for _, r in res.iterrows()])
    config_fail = config_fail[config_fail.failed.astype(str)
                              .str.startswith('configural')]
    efa_rows, dim_rows = [], []
    seen = set()
    for _, r in config_fail.iterrows():
        items = SR_SUBSETS[r.scale]['items']
        pair = pair_label[r.pair]
        for glabel in pair_groups[pair]:
            key = (r.scale, glabel)
            if key in seen:
                continue
            seen.add(key)
            if (len(items) - 2) ** 2 < len(items) + 2:
                dim_rows.append(dict(scale=r.scale, group=glabel,
                                     converged=False,
                                     reason=f'{len(items)} items: 2-factor '
                                            'EFA not identified'))
                continue
            stamp(f'EFA / dimensionality: {r.scale} x {glabel}')
            try:
                efa = polychoric_efa(r.scale, items, groups[glabel],
                                     temp_dir / 'efa_temp.csv')
                erow = dict(scale=r.scale, group=glabel, n=efa['n'],
                            eig1=efa['eigenvalues'][0],
                            eig2=efa['eigenvalues'][1],
                            eig2_over_eig1=round(
                                efa['eigenvalues'][1] / efa['eigenvalues'][0], 3))
                if efa['one_factor']:
                    f = efa['one_factor']['fit']
                    w = efa['one_factor']['worst_residuals'].iloc[0]
                    erow.update(cfi_1f=round(f['cfi_robust'], 3),
                                rmsea_1f=round(f['rmsea_robust'], 3),
                                worst_resid_pair=f"{w['item1']}~{w['item2']}",
                                worst_resid=w['resid'])
                if efa['two_factor']:
                    f2 = efa['two_factor']['fit']
                    erow.update(cfi_2f=round(f2['cfi_robust'], 3),
                                rmsea_2f=round(f2['rmsea_robust'], 3))
                efa_rows.append(erow)
                dim = dimensionality_effect_sizes(
                    r.scale, items, groups[glabel], temp_dir / 'dim_temp.csv')
                dim_rows.append(dict(scale=r.scale, group=glabel, **dim))
            except Exception as exc:
                stamp(f'  ERROR: {exc!r}')
                traceback.print_exc()
                dim_rows.append(dict(scale=r.scale, group=glabel,
                                     converged=False, reason=repr(exc)))
            if efa_rows:
                pd.DataFrame(efa_rows).to_csv(OUT_DIR / 'sr_efa_summary.csv',
                                              index=False)
            if dim_rows:
                pd.DataFrame(dim_rows).to_csv(
                    OUT_DIR / 'sr_dimensionality.csv', index=False)

    stamp('DONE')


if __name__ == '__main__':
    main()
