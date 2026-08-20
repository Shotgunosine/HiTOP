#!/usr/bin/env python
"""Status table for the exploratory exhaustive search.

Reads the per-scale progress pickles (data/cfa/exhaustive_progress_*.pkl,
atomically updated after EVERY combination -- unlike the buffered log,
these never lag) and prints one row per scale.

Usage (from notebooks/):  pixi run python exploratory_status.py
Optionally pass a different cfa dir as the first argument.
Watch live with:          watch -n 30 pixi run python exploratory_status.py
"""
import math
import sys
import time
from pathlib import Path

import pandas as pd

cfa = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('../data/cfa')
paths = sorted(cfa.glob('exhaustive_progress_*.pkl'))
if not paths:
    sys.exit(f'no exhaustive_progress_*.pkl in {cfa} yet')

print(f"{'scale':<24}{'tested':>7}{'at size':>8}{'size done':>12}"
      f"{'succ':>6}{'state':>10}{'s/combo':>9}{'last update':>14}")
for p in paths:
    st = pd.read_pickle(p)
    tested = st['tested']
    scale = st.get('scale', p.stem.replace('exhaustive_progress_', ''))
    sizes = sorted({k[0] for k in tested}, reverse=True)
    cur = min(sizes) if sizes else None
    if cur is not None:
        # n inferred from the union of items seen (exact once a size's
        # combos have cycled through every item; '?' until then)
        all_items = {i for k in tested for i in k[1]}
        n = len(all_items)
        total = math.comb(n, cur) if n > cur else None
        done = sum(1 for k in tested if k[0] == cur)
        size_done = f'{done}/{total}' if total else f'{done}/?'
    else:
        size_done = '-'
    secs = [r['seconds'] for r in tested.values()
            if isinstance(r.get('seconds'), (int, float))]
    s_per = f'{pd.Series(secs).median():.0f}' if secs else '-'
    n_succ = len(st.get('successes', {}))
    state = ('DONE' if st.get('complete') else 'running')
    if st.get('complete') and st.get('success_size'):
        state = f"DONE@{st['success_size']}"
    age = time.time() - p.stat().st_mtime
    upd = (f'{age:.0f}s ago' if age < 120 else
           f'{age/60:.0f}m ago' if age < 7200 else f'{age/3600:.1f}h ago')
    print(f"{scale:<24}{len(tested):>7}{str(cur):>8}{size_done:>12}"
          f"{n_succ:>6}{state:>10}{s_per:>9}{upd:>14}")
