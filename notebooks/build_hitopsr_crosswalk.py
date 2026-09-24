"""Build the fielded-items -> HiTOP-SR crosswalk.

Compares the 83 fielded Phase-1 HiTOP internalizing items (hitop_cfa.scales
ORIG_ITEMS) against the current HiTOP-SR item table vendored at
external/hitop/data-raw/hitopsr_items.csv (jmgirard/hitop R package,
vendored at commit e95f61b9b0f91f821b027fb68ac7d017baa38da8, 2026-09-23;
external/ itself is gitignored).
Matching is by normalized item text ONLY: the SR's `Original` HiTOP_###
numbering comes from a different master pool than the internalizing-pool
hitopNN ids used here (e.g. our hitop16 is the elevator item, SR HiTOP_16
is "center of attention").

Outputs:
    data/hitopsr_crosswalk.csv        item level; match is 'exact',
                                      'rewrite' (curated content rewrites),
                                      'none' (fielded item dropped by SR),
                                      or 'sr_only' (SR item never fielded)
    data/hitopsr_crosswalk_scales.csv scale-level summary

Run from anywhere inside pixi:  pixi run python notebooks/build_hitopsr_crosswalk.py
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, f'{ROOT}/src')
from hitop_cfa.lookup import load_item_lookup
from hitop_cfa.scales import ORIG_ITEMS

lookup = load_item_lookup(
    f'{ROOT}/data/ValSample/Internalizing-Somatoform Items_DW.xlsx',
    f'{ROOT}/data/cogmood_questions.csv',
)
lut_text = dict(zip(lookup.htid, lookup.item))

def norm(t):
    t = str(t).lower()
    t = re.sub(r'[^a-z0-9 ]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

sr = pd.read_csv(f'{ROOT}/external/hitop/data-raw/hitopsr_items.csv')
sr['ntext'] = sr['Text'].map(norm)
sr_by_ntext = {nt: i for i, nt in zip(sr.index, sr['ntext'])}

# Manually curated content-rewrites (same construct facet, new wording in the SR)
REWRITES = {
    'hitop268': 'I had trouble falling asleep.',
    'hitop124': 'I got anxious when others were watching me.',
    'hitop220': 'I was ashamed of myself.',
}
# Related but reverse-keyed SR item; not a carry-over
NOTES = {
    'hitop204': 'SR Exhibitionism item "I enjoyed being the center of attention." is a reverse-keyed relative; not counted as overlap',
}

rows = []
for sub, formula in ORIG_ITEMS.items():
    for hid in re.findall(r'hitop\d+', formula):
        text = lut_text[hid]
        note = NOTES.get(hid, '')
        i = sr_by_ntext.get(norm(text))
        if i is not None:
            kind = 'exact'
        elif hid in REWRITES:
            i = sr_by_ntext[norm(REWRITES[hid])]
            kind = 'rewrite'
        else:
            kind = 'none'
        if i is not None:
            s = sr.loc[i]
            rows.append((sub, hid, text, kind, int(s['HSR']), s['Original'],
                         s['Spectrum'], s['Scale'],
                         s['Subscale'] if pd.notna(s['Subscale']) else '', s['Text'], note))
        else:
            rows.append((sub, hid, text, kind, '', '', '', '', '', '', note))

xw = pd.DataFrame(rows, columns=[
    'our_subscale', 'htid', 'our_text', 'match', 'sr_item_num', 'sr_original_id',
    'sr_spectrum', 'sr_scale', 'sr_subscale', 'sr_text', 'note'])

# Append SR items with no counterpart in the collected pool (match = 'sr_only')
matched_hsr = set(xw.loc[xw.sr_item_num != '', 'sr_item_num'])
sr_only = []
for _, s in sr.iterrows():
    if int(s['HSR']) not in matched_hsr:
        sr_only.append(('', '', '', 'sr_only', int(s['HSR']), s['Original'],
                        s['Spectrum'], s['Scale'],
                        s['Subscale'] if pd.notna(s['Subscale']) else '', s['Text'], ''))
sr_only = pd.DataFrame(sr_only, columns=xw.columns)
sr_only = sr_only.sort_values(['sr_spectrum', 'sr_scale', 'sr_subscale', 'sr_item_num'])
xw = pd.concat([xw, sr_only], ignore_index=True)
xw.to_csv(f'{ROOT}/data/hitopsr_crosswalk.csv', index=False)

# Scale-level summary: our subscale vs its SR counterpart scale/subscale
matched_ntexts = {norm(t) for t in xw.loc[xw.match.isin(['exact', 'rewrite']), 'sr_text']}
summary = []
for sub in ORIG_ITEMS:
    d = xw[xw.our_subscale == sub]
    m = d[d.match != 'none']
    if len(m):
        # counterpart = modal SR scale/subscale among matches
        cp = m.groupby(['sr_scale', 'sr_subscale']).size().sort_values(ascending=False)
        for (cs, css), _ in cp.items():
            sr_scale_items = sr[(sr['Scale'] == cs) &
                                ((sr['Subscale'].fillna('') == css))]
            n_from_ours = sum(nt in matched_ntexts for nt in sr_scale_items['ntext'])
            summary.append((sub, len(d),
                            (d.match == 'exact').sum(), (d.match == 'rewrite').sum(),
                            cs, css, sr_scale_items['Spectrum'].iloc[0],
                            len(sr_scale_items), n_from_ours))
    else:
        summary.append((sub, len(d), 0, 0, 'DROPPED (no SR counterpart)', '', '', 0, 0))

summ = pd.DataFrame(summary, columns=[
    'our_subscale', 'our_n_items', 'n_exact_in_sr', 'n_rewrite_in_sr',
    'sr_scale', 'sr_subscale', 'sr_spectrum', 'sr_scale_n_items',
    'sr_scale_n_items_from_our_pool'])
summ.to_csv(f'{ROOT}/data/hitopsr_crosswalk_scales.csv', index=False)

print(f"item rows: {len(xw)}  exact: {(xw.match=='exact').sum()}  rewrite: {(xw.match=='rewrite').sum()}  none: {(xw.match=='none').sum()}")
print(summ.to_string(index=False))
