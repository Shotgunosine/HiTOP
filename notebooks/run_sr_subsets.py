#!/usr/bin/env python
"""Invariance ladders + ICC(2,1) for the HiTOP-SR-composition item subsets.

Exploratory follow-up to the HiTOP-SR crosswalk
(notebooks/build_hitopsr_crosswalk.py, data/hitopsr_crosswalk.csv): for
every current HiTOP-SR (sub)scale whose items were fielded here (>= 3
scoreable items), run the same permutation-tested Wu-Estabrook ladder as
the main analysis (NB_2_cfa_as_reg) on the three sample pairs, and
ICC(2,1) on the recontact cohort (NB_3_ICC's method), so the SR item sets
get 2-week-window psychometrics directly.

Not run because they equal already-reported scales:
  - SR Appetite Loss == fielded appetite_loss (identical 3-item scale)
  - SR Insomnia content-complete version == fielded insomnia full scale
    (the SR reworded hitop268); the verbatim 3-item subset IS run.
Not run because too few fielded items: SR Cognitive Problems (2/5),
Manic Energy (2/7), Anhedonia/Depressed Mood/Lassitude (1 each).

Usage (from anywhere, inside pixi):
    pixi run python notebooks/run_sr_subsets.py                  # full run
    pixi run python notebooks/run_sr_subsets.py --num-iter 50 \
        --out-dir data/rehearsal_sr_subsets                      # rehearsal
    ... --icc-only / --cfa-only to run one half.
"""
import argparse
import datetime
import os
import platform
import sys
import traceback
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

FIN_DIR = ROOT / 'data' / 'finaldata'

# SR-composition subsets. 'proxy' items are fielded items the SR carried
# over with rewritten text (see data/hitopsr_crosswalk.csv, match='rewrite');
# 'missing' counts SR items never fielded.
SR_SUBSETS = {
    'sr_anxious_worry': dict(
        items=['hitop203', 'hitop240', 'hitop265'],
        sr_scale='Distress-Dysphoria / Anxious Worry', proxy=[], missing=0),
    'sr_situational_phobia': dict(
        items=['hitop165', 'hitop225', 'hitop247', 'hitop278'],
        sr_scale='Specific Phobia Index / Situational Phobias', proxy=[], missing=0),
    'sr_insomnia_verbatim': dict(
        items=['hitop160', 'hitop254', 'hitop261'],
        sr_scale='Insomnia (verbatim 3 of 4; 4th is rewritten hitop268)',
        proxy=[], missing=1),
    'sr_social_anxiety': dict(
        items=['hitop1', 'hitop17', 'hitop114', 'hitop129', 'hitop124'],
        sr_scale='Social Anxiety', proxy=['hitop124'], missing=0),
    'sr_shame_guilt': dict(
        items=['hitop72', 'hitop140', 'hitop220'],
        sr_scale='Distress-Dysphoria / Shame-Guilt', proxy=['hitop220'], missing=0),
    'sr_well_being_partial': dict(
        items=['hitop23', 'hitop106', 'hitop149', 'hitop244'],
        sr_scale='Well-being (4 of 5; "I felt motivated" not fielded)',
        proxy=[], missing=1),
    'sr_panic_partial': dict(
        items=['hitop126', 'hitop211', 'hitop257'],
        sr_scale='Panic (3 of 5)', proxy=[], missing=2),
}


def default_cpus():
    total = os.cpu_count()
    arch = platform.machine().lower()
    if 'arm' in arch or 'aarch' in arch:
        return total - 2
    return total // 2 - 1


def stamp(msg):
    print(f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}",
          flush=True)


def run_icc(out_dir):
    import pingouin as pg

    data_gp = pd.read_csv(FIN_DIR / 'dat_gp_gridall_full.csv', index_col=0)
    data_en = pd.read_csv(FIN_DIR / 'dat_en_gridall_full.csv', index_col=0)
    data_gp = data_gp.rename(columns={'caseid': 'Subject'})
    data_en = data_en.rename(columns={'caseid': 'Subject'})
    samples = {'gp': data_gp, 'en': data_en,
               'combined': pd.concat([data_gp, data_en])}

    rows = []
    for subset, meta in SR_SUBSETS.items():
        items = meta['items']
        items_rc = [i + '_recontact' for i in items]
        for sample, data in samples.items():
            d = data[['Subject'] + items + items_rc].dropna()
            score = pd.DataFrame({
                'Subject': d['Subject'],
                'Original': d[items].sum(axis=1),
                'Recontact': d[items_rc].sum(axis=1),
            })
            melted = score.melt(id_vars='Subject',
                                value_vars=['Original', 'Recontact'],
                                var_name='Session', value_name='Score')
            icc = pg.intraclass_corr(data=melted, targets='Subject',
                                     raters='Session', ratings='Score')
            # pingouin >= 0.4 labels ICC(2,1) as 'ICC(A,1)' (McGraw & Wong)
            icc = icc.set_index('Type')
            icc2 = icc.loc['ICC(A,1)'] if 'ICC(A,1)' in icc.index else icc.loc['ICC2']
            ci = icc2['CI95'] if 'CI95' in icc2.index else icc2['CI95%']
            rows.append(dict(
                subset=subset, sr_scale=meta['sr_scale'], sample=sample,
                n=len(d), n_items=len(items),
                icc=round(float(icc2['ICC']), 4),
                ci_lo=round(float(ci[0]), 4),
                ci_hi=round(float(ci[1]), 4),
            ))
            stamp(f"ICC {subset} [{sample}] n={len(d)}: "
                  f"{rows[-1]['icc']} [{rows[-1]['ci_lo']}, {rows[-1]['ci_hi']}]")
    res = pd.DataFrame(rows)
    res.to_csv(out_dir / 'icc_sr_subsets.csv', index=False)
    stamp(f"ICC results -> {out_dir / 'icc_sr_subsets.csv'}")
    return res


def run_cfa(out_dir, num_iter, cpus_to_use):
    # importing hitop_cfa starts the embedded R session
    from hitop_cfa import run_specific_cfa

    data_val = pd.read_csv(FIN_DIR / 'dat_val.csv')
    data_gp = pd.read_csv(FIN_DIR / 'dat_gp_grid1st_full.csv')
    data_en = pd.read_csv(FIN_DIR / 'dat_en_grid1st_full.csv')
    datasets = {
        'V_GP': pd.concat([data_val, data_gp]),
        'V_EN': pd.concat([data_val, data_en]),
        'GP_EN': pd.concat([data_gp, data_en]),
    }

    helpfile_dir = out_dir / 'temp'
    helpfile_dir.mkdir(exist_ok=True, parents=True)
    temp_path = helpfile_dir / 'cfa_temp.csv'
    err_log = out_dir / 'run_errors.log'

    all_rows = []
    for subset, meta in SR_SUBSETS.items():
        stamp(f"CFA ladder for {subset} ({meta['items']}), "
              f"num_iter={num_iter}")
        try:
            res = run_specific_cfa(
                whichscale=subset,
                item_list=meta['items'],
                whichcfa='strict',
                datasets=datasets,
                temp_path=temp_path,
                num_iter=num_iter,
                cpus_to_use=cpus_to_use,
                return_vals=True,
            )
        except Exception as exc:
            msg = (f"[{datetime.datetime.now().isoformat(timespec='seconds')}]"
                   f" ERROR in ladder for {subset}: {exc!r}")
            print(msg, flush=True)
            with open(err_log, 'a') as fh:
                fh.write(msg + '\n' + traceback.format_exc() + '\n')
            continue
        res = pd.DataFrame(res)
        res['scale'] = subset
        res['sr_scale'] = meta['sr_scale']
        res['items'] = ' '.join(meta['items'])
        all_rows.append(res)
        combined = pd.concat(all_rows).replace('NA', pd.NA)
        for col in ['pconfig', 'pthresholds', 'pmetric', 'pscalar', 'pstrict']:
            combined[col] = pd.to_numeric(combined[col], errors='coerce')
        combined.to_csv(out_dir / 'sr_cfa_res.csv', index=False)
    stamp(f"CFA results -> {out_dir / 'sr_cfa_res.csv'}")
    return all_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--num-iter', type=int, default=1000)
    ap.add_argument('--out-dir', default=str(ROOT / 'data' / 'cfa_sr_subsets'))
    ap.add_argument('--cpus', type=int, default=default_cpus())
    ap.add_argument('--icc-only', action='store_true')
    ap.add_argument('--cfa-only', action='store_true')
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)
    stamp(f"out_dir={out_dir} num_iter={args.num_iter} cpus={args.cpus}")

    if not args.cfa_only:
        run_icc(out_dir)
    if not args.icc_only:
        run_cfa(out_dir, args.num_iter, args.cpus)
    stamp('DONE')


if __name__ == '__main__':
    main()
