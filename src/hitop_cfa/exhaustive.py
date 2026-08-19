"""Exhaustive combination ablation search for invariant item subsets.

Unifies the notebooks' do_three_way_cfa_ablations / do_two_way_cfa_ablations:
the set of pairwise comparisons is whatever `datasets` contains, and the scale
formulas come from the caller's `orig_items` dict instead of a hardcoded copy.
"""
import math
from itertools import combinations

from .fit import cfa_helper_func, cfa_levels, nafloat


def exhaustive_cfa_ablations(whichscale, whichcfa, howmanyitems, orig_items,
                             datasets, temp_path, num_iter, cpus_to_use,
                             parameterization="theta"):
    """Check all combinations of `howmanyitems` items for `whichscale`,
    reporting the combinations that are invariant in every dataset pair.

    All models go through the measEq (Wu-Estabrook) ladder in
    cfa_helper_func; ``whichcfa`` is the highest level tested
    ('thresholds', 'metric', 'scalar', or 'strict').

    Parameters
    ----------
    orig_items : dict
        scale name -> lavaan formula string ('scale =~item1 + item2 + ...').
    datasets : dict
        pair label -> dataframe, e.g. {'gp_en': data_genpop_enriched} for a
        single-pair search or all three pairs for the 3-way search.
    """
    print(f'FOR SCALE {whichscale.upper()}:')
    print(f'RUN ALL COMBINATIONS OF {howmanyitems} ITEMS and checks if a combination is 3-way invariant.')

    flag_found_inv_in_all_pairs = False
    successful_combinations = {}

    # validate the requested level up front
    cfa_levels(whichcfa)

    mdl = orig_items[whichscale]
    print("\n")
    print(f"Running {whichscale.upper()}")
    print(f"Items: {mdl}")

    # loop to do ablations
    items_only = mdl.split("=~", 1)[1]
    list_of_items = items_only.split(" + ")

    count_success = 0
    count_comb = 1
    pair_flags = {}

    for com in combinations(list_of_items, howmanyitems):

        # number of possible combinations of x items out of n possible items
        num_combinations = math.comb(len(list_of_items), howmanyitems)
        print(f'\n+++ TESTING {count_comb}th COMBINATION out of {num_combinations} possible combinations of {howmanyitems} items +++')
        print(f'Items to test: {com}')

        pair_flags = {}
        pair_ps = {}
        for pair, data in datasets.items():
            print(f'\n -----> {pair} <----- ')
            flag_metric, pconfig, pthresholds, pmetric, pscalar, pstrict = cfa_helper_func(
                scalename=whichscale,
                list_of_items=com,
                mydata_python=data,
                mydata_temp_path=temp_path,
                num_iter=num_iter,
                cpus_to_use=cpus_to_use,
                max_level=whichcfa,
                parameterization=parameterization)
            # a combination succeeds at the REQUESTED level (whichcfa), not
            # merely at metric (the pre-measEq code gated on the metric
            # flag even for scalar searches). nafloat maps 'NA' (level
            # never reached) to NaN, and NaN >= 0.05 is False.
            level_ps = dict(zip(
                ('configural', 'thresholds', 'metric', 'scalar', 'strict'),
                (pconfig, pthresholds, pmetric, pscalar, pstrict)))
            pair_flags[pair] = bool(nafloat(level_ps[whichcfa]) >= 0.05)
            pair_ps[pair] = [pconfig, pthresholds, pmetric, pscalar, pstrict]

        if all(pair_flags.values()):
            print(f"Combination {count_comb} passes 3-way invariance!")
            flag_found_inv_in_all_pairs = True
            count_success += 1
            successful_combinations[com] = pair_ps
        count_comb += 1

    print("\nCFA DONE")
    if flag_found_inv_in_all_pairs:
        print(f'\n\nFound {count_success} combination(s) of {howmanyitems} that is 3-way invariant.')
        print(successful_combinations)
    else:
        print(f'\nCould not find a combination of {howmanyitems} for scale {whichscale} that is 3-way invariant =(')
        for pair, flag in pair_flags.items():
            print(f'{pair}: {flag}')
        print()

    return(successful_combinations)


# =============================================================================
# Screened, abandoning, resumable exhaustive search (2026-08-19 redesign;
# author decisions recorded in HANDOFF_measeq_fix.md PROGRESS rounds 5-6):
#   - pairs are tested in the order of the ``datasets`` dict and the
#     combination is ABANDONED at the first failing pair/level (success
#     requires all pairs, so the outcome is identical; put the most-lethal
#     pair -- val_gp on this data -- first). Measured saving: ~46% of
#     candidate configural permutes, ~69% of full-ladder permutes.
#   - delta levels (thresholds/metric/scalar) carry a calibrated PARAMETRIC
#     PRE-SCREEN: if the Satorra-2000 scaled-difference p is below
#     alpha_screen, the permutation test is skipped and the combination
#     abandoned. Calibrated on the 954 recorded overnight tests: at
#     alpha = .005 zero permutation passers would have been lost (closest
#     passer at parametric p = .0444, a 9x margin). Configural is NEVER
#     screened -- its permutation test (group-equivalence of fit) has no
#     parametric analog (absolute-fit p; rho = .38; 257 passers would be
#     lost). Screened-out combos are recorded with their parametric p for
#     the audit trail.
#   - per-scale progress is persisted after EVERY combination
#     (atomic write), so a killed run resumes where it stopped.
# =============================================================================
import os
import time
from pathlib import Path

import pandas as pd

from .r_env import ro, set_seeds
from .fit import (LEVEL_NAMES, check_secondary_criteria, extract_p,
                  permute_measeq_with_retry, push_model_to_r)
from .measeq import (LEVEL_NEW_PARAMS, WU_ESTABROOK_LEVELS,
                     assert_level_adds_df, fit_is_converged, fit_measeq_level)

_GE = dict(WU_ESTABROOK_LEVELS)


def screened_ladder_test(scalename, list_of_items, datasets, temp_path,
                         num_iter, cpus_to_use, whichcfa='scalar',
                         alpha_screen=0.005, parameterization="theta"):
    """Test one item combination up the Wu-Estabrook ladder on each pair
    IN DICT ORDER, abandoning at the first failing pair/level, with the
    calibrated parametric pre-screen at the delta levels.

    Returns dict with:
        passed : bool
        pair_ps : {pair: [pconfig, pthresholds, pmetric, pscalar, pstrict]}
                  (floats / 'NA'; only pairs that were tested appear)
        fail : None, or dict(pair, level, reason, param_p, perm_p) where
               reason is 'nonconverged' | 'config_fail' | 'screened' |
               'perm_fail'
        records : list of per-(pair, level) dicts for the audit trail
    """
    levels = cfa_levels(whichcfa)
    records = []
    pair_ps = {}

    for pair, data in datasets.items():
        set_seeds(12345)
        push_model_to_r(scalename, list_of_items, data, temp_path)
        ps = {name: 'NA' for name in LEVEL_NAMES}

        fit_lo = fit_measeq_level(list(list_of_items), None,
                                  parameterization=parameterization,
                                  r_fit_name='fit_configural')
        if not fit_is_converged('fit_configural'):
            records.append(dict(pair=pair, level='configural',
                                status='nonconverged', perm_p=None,
                                param_p=None))
            return dict(passed=False, pair_ps=pair_ps, records=records,
                        fail=dict(pair=pair, level='configural',
                                  reason='nonconverged', param_p=None,
                                  perm_p=None))
        out = permute_measeq_with_retry(num_iter, cpus_to_use, con=fit_lo)
        perm_p = extract_p(out)
        ps['configural'] = perm_p
        cfg_ok = perm_p >= 0.05 or check_secondary_criteria(fit_lo)[0]
        records.append(dict(pair=pair, level='configural',
                            status='pass' if cfg_ok else 'perm_fail',
                            perm_p=perm_p, param_p=None))
        if not cfg_ok:
            pair_ps[pair] = [ps[n] for n in LEVEL_NAMES]
            return dict(passed=False, pair_ps=pair_ps, records=records,
                        fail=dict(pair=pair, level='configural',
                                  reason='config_fail', param_p=None,
                                  perm_p=perm_p))

        prev_level, prev_fit = 'configural', fit_lo
        for level in levels[1:]:
            fit_hi = fit_measeq_level(list(list_of_items), _GE[level],
                                      parameterization=parameterization,
                                      r_fit_name=f'fit_{level}')
            if not fit_is_converged(f'fit_{level}'):
                records.append(dict(pair=pair, level=level,
                                    status='nonconverged', perm_p=None,
                                    param_p=None))
                pair_ps[pair] = [ps[n] for n in LEVEL_NAMES]
                return dict(passed=False, pair_ps=pair_ps, records=records,
                            fail=dict(pair=pair, level=level,
                                      reason='nonconverged', param_p=None,
                                      perm_p=None))
            assert_level_adds_df(f'fit_{prev_level}', f'fit_{level}',
                                 prev_level, level)
            # parametric pre-screen (delta levels only; NEVER configural)
            param_p = float(ro.r(
                f'lavaan::lavTestLRT(fit_{prev_level}, fit_{level})'
                f'[2, "Pr(>Chisq)"]')[0])
            if param_p < alpha_screen:
                records.append(dict(pair=pair, level=level,
                                    status='screened', perm_p=None,
                                    param_p=param_p))
                pair_ps[pair] = [ps[n] for n in LEVEL_NAMES]
                return dict(passed=False, pair_ps=pair_ps, records=records,
                            fail=dict(pair=pair, level=level,
                                      reason='screened', param_p=param_p,
                                      perm_p=None))
            new_params = LEVEL_NEW_PARAMS[level]
            permute_kwargs = {}
            if new_params is not None:
                permute_kwargs['param'] = (
                    new_params[0] if len(new_params) == 1
                    else ro.StrVector(list(new_params)))
            out = permute_measeq_with_retry(num_iter, cpus_to_use,
                                            uncon=prev_fit, con=fit_hi,
                                            **permute_kwargs)
            perm_p = extract_p(out)
            ps[level] = perm_p
            ok = perm_p >= 0.05
            records.append(dict(pair=pair, level=level,
                                status='pass' if ok else 'perm_fail',
                                perm_p=perm_p, param_p=param_p))
            if not ok:
                pair_ps[pair] = [ps[n] for n in LEVEL_NAMES]
                return dict(passed=False, pair_ps=pair_ps, records=records,
                            fail=dict(pair=pair, level=level,
                                      reason='perm_fail', param_p=param_p,
                                      perm_p=perm_p))
            prev_level, prev_fit = level, fit_hi

        pair_ps[pair] = [ps[n] for n in LEVEL_NAMES]

    return dict(passed=True, pair_ps=pair_ps, records=records, fail=None)


def stepwise_configural_cap(cfa_dir, scale, n_items):
    """Largest combination size worth testing, certified by the stepwise
    run's iteration-0 configural ablation (which exhaustively refuted every
    larger subset at 3-way configural; seed-identical tests, so the
    verdicts transfer). Returns None when no certificate applies (no
    history, or the full set passed configural so removals began with MI
    steps), and 0 when the ablation found NO passing subset at any size.
    """
    hist_path = Path(cfa_dir) / f'{scale}_history.pkl'
    if not hist_path.exists():
        return None
    h = pd.read_pickle(hist_path)
    main = h[h.phase == 'main']
    if not len(main):
        return None
    it0 = main.iloc[0]
    if int(it0['n_items']) != int(n_items):
        return None
    if it0['action'] == 'failed_no_combo_passes':
        return 0
    if it0['action'] == 'configural_ablation_starting':
        lvl = it0['ablation_level']
        if pd.isna(lvl):
            return 0
        return int(n_items - int(lvl))
    return None


def _save_progress(path, state):
    tmp = str(path) + '.tmp'
    pd.to_pickle(state, tmp)
    os.replace(tmp, str(path))


def exhaustive_search_scale(whichscale, whichcfa, orig_items, datasets,
                            temp_path, num_iter, cpus_to_use,
                            min_items=3, max_size=None, alpha_screen=0.005,
                            progress_path=None, parameterization="theta"):
    """Exhaustive invariant-subset search for one scale, descending from
    the largest viable size and stopping at the first size with >= 1
    success (same semantics as the original search), with pair-order early
    abandon, the calibrated delta pre-screen, an optional size cap, and
    per-combination progress persistence for resumability.

    Returns (successful_combinations, success_size):
        successful_combinations : {items_tuple: {pair: [p, ...5 levels]}}
        success_size : int or None
    """
    items_only = orig_items[whichscale].split("=~", 1)[1].strip()
    items = [s.strip() for s in items_only.split("+")]
    n = len(items)
    top = n - 1 if max_size is None else min(int(max_size), n - 1)

    state = None
    if progress_path is not None and Path(progress_path).exists():
        state = pd.read_pickle(progress_path)
        print(f"[resume] loaded progress for {whichscale}: "
              f"{len(state['tested'])} combinations already tested")
    if state is None:
        state = dict(scale=whichscale, whichcfa=whichcfa,
                     alpha_screen=alpha_screen, tested={},
                     complete=False, successes={}, success_size=None)
    if state['complete']:
        print(f"[resume] {whichscale} already complete: "
              f"{len(state['successes'])} success(es) at size "
              f"{state['success_size']}")
        return state['successes'], state['success_size']
    tested = state['tested']

    if top < min_items:
        print(f"{whichscale}: no viable sizes (cap {max_size}, "
              f"min_items {min_items}) -- nothing to search")
        state['complete'] = True
        if progress_path is not None:
            _save_progress(progress_path, state)
        return {}, None

    if max_size is not None and max_size < n - 1:
        print(f"{whichscale}: stepwise certificate caps the search at "
              f"{top} items (sizes above were exhaustively refuted at "
              f"configural)")

    for size in range(top, min_items - 1, -1):
        combos = list(combinations(items, size))
        print(f"\n--- {whichscale}: size {size} "
              f"({len(combos)} combinations) ---")
        successes = {com: tested[(size, com)]['pair_ps']
                     for com in combos
                     if (size, com) in tested
                     and tested[(size, com)]['status'] == 'success'}
        for ci, com in enumerate(combos):
            key = (size, com)
            if key in tested:
                continue
            print(f"[{ci + 1}/{len(combos)}] testing {com}")
            t0 = time.time()
            res = screened_ladder_test(
                whichscale, com, datasets, temp_path, num_iter,
                cpus_to_use, whichcfa=whichcfa, alpha_screen=alpha_screen,
                parameterization=parameterization)
            rec = dict(status='success' if res['passed'] else 'failed',
                       pair_ps=res['pair_ps'], fail=res['fail'],
                       records=res['records'],
                       seconds=round(time.time() - t0, 1))
            tested[key] = rec
            if progress_path is not None:
                _save_progress(progress_path, state)
            if res['passed']:
                successes[com] = res['pair_ps']
                print(f"    PASSES {whichcfa} on all pairs")
            else:
                f = res['fail']
                extra = (f" param_p={f['param_p']:.4g}"
                         if f['reason'] == 'screened' else '')
                print(f"    abandoned: {f['pair']} {f['level']} "
                      f"{f['reason']}{extra}")
        if successes:
            print(f"{whichscale}: {len(successes)} success(es) at size {size}")
            state.update(complete=True, successes=successes,
                         success_size=size)
            if progress_path is not None:
                _save_progress(progress_path, state)
            return successes, size

    print(f"{whichscale}: no invariant subset found at any size")
    state['complete'] = True
    if progress_path is not None:
        _save_progress(progress_path, state)
    return {}, None
