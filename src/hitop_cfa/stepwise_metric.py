# =============================================================================
# Stepwise CFA targeting metric invariance (v8, measEq):
#   - Every model is a Wu & Estabrook (2016) model from
#     semTools::measEq.syntax (ID.cat = "Wu.Estabrook.2016",
#     ID.fac = "std.lv"); plain group.equal shortcuts are vacuous for
#     ordinal indicators (see measeq.py / HANDOFF_measeq_fix.md).
#   - Per-pair test ladder: configural -> thresholds -> metric
#     (metric = thresholds + loadings). assert_level_adds_df runs before
#     every permuteMeasEq delta test.
#   - Under std.lv there is NO marker item (factor variance fixed in the
#     reference group), so every item has a testable loading MI and no item
#     is excluded from MI candidacy or ablation.
#   - Removal tiers:
#       configural failure -> bounded combinatorial ablation. Find smallest
#         k such that some k-item ablation achieves 3-way configural
#         invariance; within that k, pick by CFI -> TLI -> RMSEA cascade
#         (all_config_passed filter first). If no combo at any
#         k <= n_items - min_items passes, stop and report failure.
#       thresholds failure (config OK) -> single-item threshold-MI removal
#         (extract_item_mis_from_thresholds; max MI per item over its
#         threshold constraints).
#       metric failure (thresholds OK) -> single-item loading-MI removal.
# =============================================================================
from itertools import combinations

import numpy as np
import pandas as pd

from .r_env import localconverter, pandas2ri, ro, set_seeds
from .fit import (check_secondary_criteria, extract_p,
                  permute_measeq_with_retry, push_model_to_r)
from .measeq import (WU_ESTABROOK_LEVELS, assert_level_adds_df,
                     extract_item_mis_from_thresholds, fit_is_converged,
                     fit_measeq_level)

DEFAULT_CFI_TIE_TOLERANCE = 0.001
DEFAULT_TLI_TIE_TOLERANCE = 0.001

_GROUP_EQUAL = dict(WU_ESTABROOK_LEVELS)


def cfa_test_metric_with_mi(scalename, list_of_items, mydata_python, mydata_temp_path,
                            num_iter, cpus_to_use, configural_only=False,
                            parameterization="theta"):
    """Test one dataset pair configural -> thresholds -> metric with
    Wu-Estabrook measEq models, stopping at the first failed level.

    Returns a dict with per-level p-values / pass flags, configural fit
    indices, and (when the corresponding level failed) per-item MI dicts:
    ``thresholds_item_mis`` (threshold-equality MIs, op "|") and
    ``item_mis`` (loading MIs, op "=~").
    """
    set_seeds(12345)

    push_model_to_r(scalename, list_of_items, mydata_python, mydata_temp_path)

    fit_config = fit_measeq_level(list_of_items, group_equal=None,
                                  parameterization=parameterization,
                                  r_fit_name='fit_config')
    if not fit_is_converged('fit_config'):
        # non-convergent fits crash permuteMeasEq/fitMeasures; treat as a
        # configural failure so the search moves on instead of dying
        print("  [WARN] configural model did not converge -- treated as "
              "configural failure")
        config_p, config_passed_primary, config_passed = np.nan, False, False
        cfi = tli = rmsea = np.nan
    else:
        out_config = permute_measeq_with_retry(num_iter, cpus_to_use,
                                               con=fit_config)
        config_p = extract_p(out_config)
        config_passed_primary = (config_p >= 0.05)
        config_passed_secondary, cfi, tli, rmsea = check_secondary_criteria(fit_config)
        config_passed = config_passed_primary or config_passed_secondary

    result = {
        'config_p':              config_p,
        'config_passed':         config_passed,
        'config_passed_primary': config_passed_primary,
        'config_cfi':            cfi,
        'config_tli':            tli,
        'config_rmsea':          rmsea,
        'thresholds_p':          None,
        'thresholds_passed':     None,
        'thresholds_item_mis':   None,
        'metric_p':              None,
        'metric_passed':         None,
        'item_mis':              None,
    }
    if configural_only or not config_passed:
        return result

    # ----- Thresholds (ordinal analog of the location constraint) -----
    fit_thresholds = fit_measeq_level(list_of_items,
                                      group_equal=_GROUP_EQUAL['thresholds'],
                                      parameterization=parameterization,
                                      r_fit_name='fit_thresholds')
    if not fit_is_converged('fit_thresholds'):
        print("  [WARN] thresholds model did not converge -- treated as "
              "thresholds failure")
        result['thresholds_p'] = np.nan
        result['thresholds_passed'] = False
        return result
    assert_level_adds_df('fit_config', 'fit_thresholds',
                         'configural', 'thresholds')
    out_thresholds = permute_measeq_with_retry(
        num_iter, cpus_to_use, uncon=fit_config, con=fit_thresholds,
        param="thresholds")
    ro.globalenv['out_thresholds'] = out_thresholds
    thresholds_p = extract_p(out_thresholds)
    thresholds_passed = (thresholds_p >= 0.05)
    result['thresholds_p'] = thresholds_p
    result['thresholds_passed'] = thresholds_passed
    if not thresholds_passed:
        result['thresholds_item_mis'] = extract_item_mis_from_thresholds(
            list_of_items)
        return result

    # ----- Metric (thresholds + loadings) -----
    fit_metric = fit_measeq_level(list_of_items,
                                  group_equal=_GROUP_EQUAL['metric'],
                                  parameterization=parameterization,
                                  r_fit_name='fit_metric')
    if not fit_is_converged('fit_metric'):
        print("  [WARN] metric model did not converge -- treated as "
              "metric failure")
        result['metric_p'] = np.nan
        result['metric_passed'] = False
        return result
    assert_level_adds_df('fit_thresholds', 'fit_metric',
                         'thresholds', 'metric')
    out_metric = permute_measeq_with_retry(
        num_iter, cpus_to_use, uncon=fit_thresholds, con=fit_metric,
        param="loadings")
    ro.globalenv['out_metric'] = out_metric
    metric_p = extract_p(out_metric)
    metric_passed = (metric_p >= 0.05)
    result['metric_p'] = metric_p
    result['metric_passed'] = metric_passed
    if not metric_passed:
        result['item_mis'] = extract_item_mis_from_metric(list_of_items)
    return result


def extract_item_mis_from_metric(item_list):
    try:
        ro.r('''
            mi_obs <- out_metric@MI.obs
            pt     <- out_metric@PT
            mi_obs$par_name <- pt$par[ match(mi_obs$lhs, pt$plabel) ]
            mi_loadings <- mi_obs[grepl("=~", mi_obs$par_name), ]
            if (nrow(mi_loadings) > 0) {
                mi_loadings$item <- sub(".*=~", "", mi_loadings$par_name)
            }
        ''')
        mi_df_r = ro.r('mi_loadings')
        with localconverter(ro.default_converter + pandas2ri.converter):
            mi_df = ro.conversion.rpy2py(mi_df_r)

        if mi_df is None or len(mi_df) == 0:
            return None
        mi_df = mi_df[mi_df['item'].isin(item_list)]
        if len(mi_df) == 0:
            return None
        item_mis = mi_df.groupby('item')['X2'].max().to_dict()
        return {k: float(v) for k, v in item_mis.items()}
    except Exception as e:
        print(f"  [WARN] Could not extract MIs from metric model: {e}")
        return None


def find_worst_item(mi_dicts_failing, excluded_item, current_items):
    """
    Aggregate MIs across failing comparisons and return the item with the
    highest sum. excluded_item is dropped from candidacy; under std.lv
    identification there is no marker item, so callers pass
    excluded_item=None (the parameter is kept for API compatibility).
    """
    aggregated = {}
    for item in current_items:
        if item == excluded_item:
            continue
        total = 0.0
        for mi_dict in mi_dicts_failing:
            if mi_dict and item in mi_dict:
                total += mi_dict[item]
        aggregated[item] = total
    if not aggregated or max(aggregated.values()) == 0.0:
        return None, aggregated
    worst_item = max(aggregated, key=aggregated.get)
    return worst_item, aggregated


def _test_all_pairs(scalename, items, datasets, temp_path, num_iter, cpus_to_use,
                    configural_only=False, parameterization="theta"):
    results = {}
    for name, data in datasets.items():
        results[name] = cfa_test_metric_with_mi(
            scalename, items, data, temp_path,
            num_iter=num_iter, cpus_to_use=cpus_to_use,
            configural_only=configural_only,
            parameterization=parameterization)
    return results


def _build_history_row(iteration, phase, items, candidate_dropped,
                       pair_results, action=None, removed_items=None,
                       removal_reason=None, mis_used=None,
                       cfi_tied_count=None, tli_tied_count=None,
                       ablation_level=None):
    row = {
        'iteration':         iteration,
        'phase':             phase,
        'candidate_dropped': candidate_dropped,
        'n_items':           len(items),
        'items':             tuple(items),
        'ablation_level':    ablation_level,
    }
    cfis, tlis, rmseas = [], [], []
    all_config_passed = True
    all_thresholds_passed = True
    all_metric_passed = True
    thresholds_evaluable = True
    metric_evaluable = True

    for name, r in pair_results.items():
        row[f'{name}_config_p']              = r['config_p']
        row[f'{name}_config_passed']         = r['config_passed']
        row[f'{name}_config_passed_primary'] = r['config_passed_primary']
        row[f'{name}_config_cfi']            = r['config_cfi']
        row[f'{name}_config_tli']            = r['config_tli']
        row[f'{name}_config_rmsea']          = r['config_rmsea']
        row[f'{name}_thresholds_p']          = r['thresholds_p']
        row[f'{name}_thresholds_passed']     = r['thresholds_passed']
        row[f'{name}_metric_p']              = r['metric_p']
        row[f'{name}_metric_passed']         = r['metric_passed']

        cfis.append(r['config_cfi'])
        tlis.append(r['config_tli'])
        rmseas.append(r['config_rmsea'])
        if not r['config_passed']:
            all_config_passed = False
            thresholds_evaluable = False
            metric_evaluable = False
        if r['thresholds_passed'] is None:
            thresholds_evaluable = False
            metric_evaluable = False
        elif not r['thresholds_passed']:
            all_thresholds_passed = False
            metric_evaluable = False
        if r['metric_passed'] is None:
            metric_evaluable = False
        elif not r['metric_passed']:
            all_metric_passed = False

    row['min_config_cfi']       = min(cfis) if cfis else None
    row['min_config_tli']       = min(tlis) if tlis else None
    row['max_config_rmsea']     = max(rmseas) if rmseas else None
    row['all_config_passed']    = all_config_passed
    row['all_thresholds_passed'] = (all_thresholds_passed
                                    if thresholds_evaluable else None)
    row['all_metric_passed']    = (all_metric_passed if metric_evaluable else None)
    row['action']               = action
    row['removed_items']        = removed_items
    row['removal_reason']       = removal_reason
    row['cfi_tied_count']       = cfi_tied_count
    row['tli_tied_count']       = tli_tied_count
    row['mis_used']             = mis_used
    return row


def _pick_by_cascade(passing_entries, cfi_tie_tolerance, tli_tie_tolerance):
    """CFI -> TLI -> RMSEA. Entries: (combo, min_cfi, min_tli, max_rmsea, all_passed)."""
    max_cfi = max(r[1] for r in passing_entries)
    cfi_tied = [r for r in passing_entries if r[1] >= max_cfi - cfi_tie_tolerance]
    cfi_tied_count = len(cfi_tied)

    if cfi_tied_count == 1:
        return cfi_tied[0], 'cfi_max_min', cfi_tied_count, None

    max_tli = max(r[2] for r in cfi_tied)
    tli_tied = [r for r in cfi_tied if r[2] >= max_tli - tli_tie_tolerance]
    tli_tied_count = len(tli_tied)

    if tli_tied_count == 1:
        return tli_tied[0], 'tli_tiebreaker', cfi_tied_count, tli_tied_count

    best = min(tli_tied, key=lambda r: r[3])
    return best, 'rmsea_tiebreaker', cfi_tied_count, tli_tied_count


def _search_combo_ablation(whichscale, current, min_items, iteration,
                           cfi_tie_tolerance, tli_tie_tolerance, history_rows,
                           datasets, temp_path, num_iter, cpus_to_use,
                           parameterization="theta"):
    """
    Search the smallest combo size k such that some k-item ablation
    achieves 3-way configural invariance. ALL items in `current` are
    candidates (there is no marker under std.lv identification).
    """
    candidates_pool = list(current)  # everything is fair game
    max_level = len(current) - min_items
    if max_level < 1:
        return None, None, None, None, None

    for level in range(1, max_level + 1):
        n_combos = sum(1 for _ in combinations(candidates_pool, level))
        print(f"  -- Ablation level {level} ({n_combos} combos) --")

        passing = []
        n_evaluated = 0
        for combo in combinations(candidates_pool, level):
            test_items = [i for i in current if i not in combo]

            combo_label = combo if len(combo) > 1 else combo[0]
            print(f"  Trying drop of {combo_label} -> {len(test_items)} items")
            cand_results = _test_all_pairs(whichscale, test_items, datasets,
                                           temp_path, num_iter, cpus_to_use,
                                           configural_only=True,
                                           parameterization=parameterization)
            cand_row = _build_history_row(
                iteration, 'ablation_candidate', test_items, combo_label,
                cand_results, action='ablation_candidate_tested',
                ablation_level=level)
            cmc = cand_row['min_config_cfi']
            cmt = cand_row['min_config_tli']
            cmr = cand_row['max_config_rmsea']
            acp = cand_row['all_config_passed']
            history_rows.append(cand_row)
            print(f"    min_cfi={cmc:.4f} min_tli={cmt:.4f} "
                  f"max_rmsea={cmr:.4f} all_config_passed={acp}")

            n_evaluated += 1
            if acp:
                passing.append((combo, cmc, cmt, cmr, acp))

        if passing:
            print(f"  Level {level}: {len(passing)} of {n_evaluated} combos "
                  f"achieve 3-way configural invariance.")
            best, reason, cfi_tc, tli_tc = _pick_by_cascade(
                passing, cfi_tie_tolerance, tli_tie_tolerance)
            return best[0], reason, level, cfi_tc, tli_tc

        print(f"  Level {level}: no combo achieves 3-way configural invariance. "
              f"Expanding to level {level+1}...")

    return None, None, None, None, None


def _mi_removal_step(level_label, failing_mis, current, removed, history_rows,
                     it, main_results, fail_action, removal_action,
                     removal_reason, build_row):
    """Shared single-item MI-removal step for the thresholds/metric tiers.

    Returns True if an item was removed, False if no worst item could be
    identified (caller should stop)."""
    worst, aggregated = find_worst_item(failing_mis,
                                        excluded_item=None,
                                        current_items=current)

    if worst is None:
        print(f"  Could not identify a worst item from {level_label} MIs. "
              f"Stopping.")
        row = build_row(it, 'main', current, None, main_results,
                        action=fail_action, mis_used=aggregated)
        history_rows.append(row)
        return False

    print(f"  Aggregated {level_label} MIs (summed over failing comparisons):")
    for item, mi in sorted(aggregated.items(), key=lambda kv: -kv[1]):
        print(f"    {item}: {mi:.3f}")
    print(f"  -> Removing: {worst}")

    row = build_row(it, 'main', current, None, main_results,
                    action=removal_action,
                    removed_items=(worst,),
                    removal_reason=removal_reason,
                    mis_used=aggregated)
    history_rows.append(row)

    removed.append(worst)
    current.remove(worst)
    return True


def do_three_way_cfa_stepwise_mi(whichscale, orig_items, datasets, temp_path,
                                 num_iter, cpus_to_use,
                                 min_items=3,
                                 max_iter=None,
                                 drop_idx=None,
                                 cfi_tie_tolerance=DEFAULT_CFI_TIE_TOLERANCE,
                                 tli_tie_tolerance=DEFAULT_TLI_TIE_TOLERANCE,
                                 parameterization="theta"):
    """
    Stepwise CFA targeting 3-way metric invariance under the Wu-Estabrook
    ladder (configural -> thresholds -> metric), with multi-level
    combinatorial ablation for configural failures and MI-based single-item
    removal for thresholds and metric failures.

    Under std.lv identification there is no marker item: every item has a
    testable loading MI and every item is an ablation candidate.

    Parameters
    ----------
    orig_items : dict
        scale name -> lavaan formula string ('scale =~item1 + item2 + ...').
    datasets : dict
        pair label -> dataframe for each pairwise comparison, e.g.
        {'val_gp': ..., 'val_en': ..., 'gp_en': ...}.

    Returns
    -------
    final_items : list[str] or None
    removed_in_order : list[str]
    history : pd.DataFrame
        Columns include `ablation_level` (int, when from ablation),
        `removed_items` (tuple of strings), `removal_reason` in
        {'cfi_max_min', 'tli_tiebreaker', 'rmsea_tiebreaker',
         'thresholds_mi_worst', 'mi_worst', None}.
    """
    print(f"\n{'='*60}\nSTEPWISE CFA: {whichscale.upper()}\n{'='*60}")

    items_str   = orig_items[whichscale]
    items_only  = items_str.split("=~", 1)[1].strip()
    current     = [s.strip() for s in items_only.split("+")]

    removed = []
    history_rows = []

    if drop_idx is not None:
        removed_item = current.pop(drop_idx)
        removed.append(removed_item)
        print(f"Pre-dropping item at index {drop_idx}: {removed_item}")

    if max_iter is None:
        max_iter = len(current) - min_items

    for it in range(max_iter + 1):
        print(f"\n--- Iteration {it}: {len(current)} items ---")
        print(f"Current: {current}")

        if len(current) < min_items:
            print(f"Below minimum of {min_items} items. Stopping.")
            history_rows.append({
                'iteration': it, 'phase': 'final', 'n_items': len(current),
                'items': tuple(current), 'action': 'failed_min_items',
            })
            return None, removed, pd.DataFrame(history_rows)

        print("Testing current item set...")
        main_results = _test_all_pairs(whichscale, current, datasets,
                                       temp_path, num_iter, cpus_to_use,
                                       configural_only=False,
                                       parameterization=parameterization)
        all_config = all(r['config_passed'] for r in main_results.values())
        all_thresholds = all(r['thresholds_passed'] is True
                             for r in main_results.values()) if all_config else False
        all_metric = all(r['metric_passed'] is True
                         for r in main_results.values()) if all_thresholds else False

        if all_config and all_thresholds and all_metric:
            print(f"\n*** 3-way metric invariance achieved with {len(current)} items ***")
            row = _build_history_row(it, 'main', current, None, main_results,
                                     action='success')
            history_rows.append(row)
            return current, removed, pd.DataFrame(history_rows)

        # ----- Configural failure: combinatorial ablation -----
        if not all_config:
            print("Configural failed for at least one comparison; running "
                  "combinatorial ablation search (all items)...")
            row = _build_history_row(it, 'main', current, None, main_results,
                                     action='configural_ablation_starting')
            history_rows.append(row)
            main_row_idx = len(history_rows) - 1

            best_combo, reason, level, cfi_tc, tli_tc = _search_combo_ablation(
                whichscale, current, min_items, it,
                cfi_tie_tolerance, tli_tie_tolerance, history_rows,
                datasets, temp_path, num_iter, cpus_to_use,
                parameterization=parameterization)

            if best_combo is None:
                print("  No combo at any level achieves 3-way configural "
                      "invariance. Stopping.")
                history_rows[main_row_idx]['action'] = 'failed_no_combo_passes'
                history_rows.append({
                    'iteration': it, 'phase': 'final',
                    'n_items': len(current), 'items': tuple(current),
                    'action': 'failed_no_combo_passes',
                })
                return None, removed, pd.DataFrame(history_rows)

            print(f"  -> Removing combo {best_combo} "
                  f"(ablation_level={level}, reason={reason})")
            history_rows[main_row_idx]['removed_items']    = tuple(best_combo)
            history_rows[main_row_idx]['removal_reason']   = reason
            history_rows[main_row_idx]['ablation_level']   = level
            history_rows[main_row_idx]['cfi_tied_count']   = cfi_tc
            history_rows[main_row_idx]['tli_tied_count']   = tli_tc

            for item in best_combo:
                removed.append(item)
                current.remove(item)
            continue

        # ----- Configural OK, thresholds failed: threshold-MI removal -----
        if not all_thresholds:
            print("Configural OK but thresholds failed; running "
                  "threshold-MI-based removal...")
            failing_mis = [r['thresholds_item_mis']
                           for r in main_results.values()
                           if r['thresholds_passed'] is False
                           and r['thresholds_item_mis']]
            if not _mi_removal_step('threshold', failing_mis, current, removed,
                                    history_rows, it, main_results,
                                    fail_action='failed_no_thresholds_mi',
                                    removal_action='thresholds_mi_removal',
                                    removal_reason='thresholds_mi_worst',
                                    build_row=_build_history_row):
                return None, removed, pd.DataFrame(history_rows)
            continue

        # ----- Thresholds OK, metric failed: single-item loading-MI removal -----
        print("Thresholds OK but metric failed; running loading-MI-based "
              "removal...")
        failing_mis = [r['item_mis'] for r in main_results.values()
                       if r['metric_passed'] is False and r['item_mis']]
        if not _mi_removal_step('loading', failing_mis, current, removed,
                                history_rows, it, main_results,
                                fail_action='failed_no_mi',
                                removal_action='metric_mi_removal',
                                removal_reason='mi_worst',
                                build_row=_build_history_row):
            return None, removed, pd.DataFrame(history_rows)

    print(f"\nHit max_iter ({max_iter}) without convergence.")
    history_rows.append({
        'iteration': max_iter + 1, 'phase': 'final',
        'n_items': len(current), 'items': tuple(current),
        'action': 'failed_max_iter',
    })
    return None, removed, pd.DataFrame(history_rows)
