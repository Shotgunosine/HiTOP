#!/usr/bin/env python
"""Dress rehearsal for the overnight measEq runs.

Executes PATCHED COPIES of the production notebooks end-to-end, in the
order the author will run them, so any crash surfaces now instead of
overnight:

    NB_2_cfa_as_reg -> NB_2_cfa_exploratory -> NB_invariance_plot ->
    NB_3_ICC -> NB_icc_plots -> NB_4_convdiv

Patches applied to the copies (the production notebooks are untouched):
  - num_iter = 50 (permutation tests stay cheap but real)
  - orig_items restricted to 3 small scales (insomnia, appetite_loss,
    shame_guilt); the exploratory other-scales set restricted to gad_sum
  - every OUTPUT path (cfa_dir, icc_dir, convdiv_res_dir, temp csv)
    redirected into ../data/rehearsal/ so nothing touches data/cfa etc.
  - NB_4's nperms/nboots cut to 20

The executed copies are written as notebooks/zz_rehearsal_*.ipynb (with
outputs, for inspection) and the sandbox is wiped at startup so re-runs
are clean. Run from notebooks/ inside pixi:

    pixi run python rehearse_overnight.py

Exit code 0 = every notebook executed top-to-bottom and the artifact
chain checks passed.
"""
import json
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).parent
SANDBOX = (HERE / '..' / 'data' / 'rehearsal').resolve()
SCALES = ('insomnia', 'appetite_loss', 'shame_guilt')
NUM_ITER = 50

OVERRIDE_HEADER = "# === REHEARSAL OVERRIDES (auto-inserted; not production) ===\n"


def load_nb(name):
    with open(HERE / name) as fh:
        return json.load(fh)


def cell_src(cell):
    src = cell.get('source', '')
    return ''.join(src) if isinstance(src, list) else src


def find_cell_idx(nb, marker):
    for ix, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code' and marker in cell_src(cell):
            return ix
    raise RuntimeError(f"no code cell contains marker {marker!r}")


def insert_code_after(nb, marker, source):
    ix = find_cell_idx(nb, marker)
    nb['cells'].insert(ix + 1, {
        'cell_type': 'code', 'id': uuid.uuid4().hex[:8], 'metadata': {},
        'execution_count': None, 'outputs': [],
        'source': OVERRIDE_HEADER + source,
    })


def replace_in_nb(nb, old, new, required=True):
    hit = False
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        src = cell_src(cell)
        if old in src:
            cell['source'] = src.replace(old, new)
            hit = True
    if required and not hit:
        raise RuntimeError(f"pattern not found in any cell: {old!r}")


def write_and_execute(nb, name):
    out_name = f'zz_rehearsal_{name}'
    with open(HERE / out_name, 'w') as fh:
        json.dump(nb, fh, indent=1)
    print(f"\n=== executing {out_name} ===", flush=True)
    t0 = time.time()
    proc = subprocess.run(
        ['pixi', 'run', 'jupyter', 'nbconvert', '--to', 'notebook',
         '--execute', '--inplace', '--ExecutePreprocessor.timeout=-1',
         out_name],
        cwd=HERE, capture_output=True, text=True)
    mins = (time.time() - t0) / 60
    if proc.returncode != 0:
        print(proc.stdout[-3000:])
        print(proc.stderr[-6000:])
        print(f"!!! {out_name} FAILED after {mins:.1f} min")
        return False, mins
    print(f"{out_name} OK ({mins:.1f} min)")
    return True, mins


ORIG_ITEMS_RESTRICT = (
    f"orig_items = {{k: v for k, v in orig_items.items() if k in {SCALES!r}}}\n"
    f"print('REHEARSAL scales:', list(orig_items))"
)


def patch_as_reg():
    nb = load_nb('NB_2_cfa_as_reg.ipynb')
    insert_code_after(nb, "cfa_dir = dat_dir / 'cfa'",
        "cfa_dir = Path('../data/rehearsal/cfa')\n"
        "cfa_dir.mkdir(parents=True, exist_ok=True)\n"
        "helpfile_dir = cfa_dir / 'temp'\n"
        "helpfile_dir.mkdir(exist_ok=True, parents=True)\n"
        "path_to_helpfile = helpfile_dir / 'cfa_temp.csv'")
    insert_code_after(nb, 'num_iter = 1000', f'num_iter = {NUM_ITER}')
    insert_code_after(nb, "orig_items = {", ORIG_ITEMS_RESTRICT)
    return nb


def patch_exploratory():
    nb = load_nb('NB_2_cfa_exploratory.ipynb')
    insert_code_after(nb, "cfa_dir = dat_dir / 'cfa'",
        "cfa_dir = Path('../data/rehearsal/cfa')\n"
        "cfa_dir.mkdir(parents=True, exist_ok=True)\n"
        "helpfile_dir = cfa_dir / 'manual_temp'\n"
        "helpfile_dir.mkdir(exist_ok=True, parents=True)\n"
        "path_to_helpfile = helpfile_dir / 'cfa_temp.csv'")
    insert_code_after(nb, 'num_iter = 1000', f'num_iter = {NUM_ITER}')
    insert_code_after(nb, "orig_items = {", ORIG_ITEMS_RESTRICT)
    # restrict the other-scales section to gad_sum (7 items) to bound time
    replace_in_nb(nb, "other_luts = {",
                  "other_scales = {'gad_sum': other_scales['gad_sum']}  "
                  "# REHEARSAL restriction\n\nother_luts = {")
    return nb


def patch_invariance_plot():
    nb = load_nb('NB_invariance_plot.ipynb')
    replace_in_nb(nb, "'../data/cfa/orig_cfa_res.csv'",
                  "'../data/rehearsal/cfa/orig_cfa_res.csv'")
    return nb


def patch_nb3():
    nb = load_nb('NB_3_ICC.ipynb')
    insert_code_after(nb, "icc_dir = dat_dir / 'icc'",
        "cfa_dir = Path('../data/rehearsal/cfa')\n"
        "icc_dir = Path('../data/rehearsal/icc')\n"
        "icc_dir.mkdir(parents=True, exist_ok=True)")
    return nb


def patch_icc_plots():
    nb = load_nb('NB_icc_plots.ipynb')
    insert_code_after(nb, "icc_dir = dat_dir / 'icc'",
                      "icc_dir = Path('../data/rehearsal/icc')")
    return nb


def patch_nb4():
    nb = load_nb('NB_4_convdiv.ipynb')
    insert_code_after(nb, "convdiv_res_dir = dat_dir / 'convdiv'",
        "convdiv_res_dir = Path('../data/rehearsal/convdiv')\n"
        "convdiv_res_dir.mkdir(parents=True, exist_ok=True)\n"
        "log_dir = Path('./log/rehearsal/logs_convdiv')\n"
        "log_dir.mkdir(exist_ok=True, parents=True)")
    replace_in_nb(nb, "icc_dir = dat_dir / 'icc'",
                  "icc_dir = Path('../data/rehearsal/icc')")
    replace_in_nb(nb, 'nperms = 1000', 'nperms = 20')
    replace_in_nb(nb, 'nboots = 1000', 'nboots = 20')
    return nb


def post_checks():
    import pandas as pd
    ok = True
    cfa = SANDBOX / 'cfa'
    expected = [
        cfa / 'orig_cfa_res.csv',
        cfa / 'stepwise.pkl',
        cfa / 'stepwise_scalar.pkl',
        cfa / 'final_cores_strict_report.csv',
        cfa / 'exhaustive.pkl',
        cfa / 'other_orig_cfa_res.csv',
        cfa / 'other_scales_exhaustive.pkl',
        cfa / 'consolidated_cores.pkl',
        SANDBOX / 'icc' / 'cores.pkl',
        SANDBOX / 'icc' / 'result_ICC_origscales_combined.csv',
        SANDBOX / 'icc' / 'result_ICC_invariantonly_combined.csv',
        SANDBOX / 'convdiv' / 'conv_res.pkl',
        SANDBOX / 'convdiv' / 'divergent_perm_res.pkl',
        SANDBOX / 'convdiv' / 'divergent_boot_res.pkl',
    ]
    print(f"\n{'='*64}\nARTIFACT CHECKS\n{'='*64}")
    for path in expected:
        exists = path.exists()
        print(f"  {'OK ' if exists else 'MISSING'}  {path.relative_to(SANDBOX.parent)}")
        ok = ok and exists

    fc_path = cfa / 'stepwise_scalar.pkl'
    if fc_path.exists():
        fc = pd.read_pickle(fc_path)
        print(f"\nfinal cores ({len(fc)} rows; expected {len(SCALES)}):")
        cols = [c for c in ('scale', 'core_level', 'item_nos', 'error')
                if c in fc.columns]
        print(fc[cols].to_string(index=False))
        ok = ok and len(fc) == len(SCALES)
        bad_levels = set(fc.core_level.dropna()) - {'scalar', 'metric'}
        if bad_levels:
            print(f"  BAD core_level values: {bad_levels}")
            ok = False

    err_log = cfa / 'run_errors.log'
    if err_log.exists():
        print(f"\n!!! run_errors.log is non-empty:\n{err_log.read_text()}")
        ok = False
    else:
        print("\nno run_errors.log (no per-scale errors recorded)")
    return ok


def main():
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)
    print(f"sandbox: {SANDBOX}")
    print(f"scales: {SCALES}, num_iter: {NUM_ITER}")

    stages = [
        ('NB_2_cfa_as_reg.ipynb', patch_as_reg),
        ('NB_2_cfa_exploratory.ipynb', patch_exploratory),
        ('NB_invariance_plot.ipynb', patch_invariance_plot),
        ('NB_3_ICC.ipynb', patch_nb3),
        ('NB_icc_plots.ipynb', patch_icc_plots),
        ('NB_4_convdiv.ipynb', patch_nb4),
    ]
    timings = []
    for name, patcher in stages:
        ok, mins = write_and_execute(patcher(), name)
        timings.append((name, ok, mins))
        if not ok:
            break

    print(f"\n{'='*64}\nREHEARSAL SUMMARY\n{'='*64}")
    for name, ok, mins in timings:
        print(f"  {'OK ' if ok else 'FAIL'}  {name:<32} {mins:6.1f} min")

    all_executed = all(ok for _, ok, _ in timings) and len(timings) == len(stages)
    artifacts_ok = post_checks() if all_executed else False

    if all_executed and artifacts_ok:
        print("\nREHEARSAL PASSED: every notebook executed top-to-bottom and "
              "the artifact chain is intact.")
        return 0
    print("\nREHEARSAL FAILED -- fix before launching the overnight runs.")
    return 1


if __name__ == '__main__':
    sys.exit(main())
