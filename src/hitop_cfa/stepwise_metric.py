# =============================================================================
# Stepwise CFA with two-tier removal (v7):
#   - Marker is now ablatable; when removed, the new first item in the
#     remaining list implicitly becomes the marker for subsequent fits.
#   - Configural failure -> bounded combinatorial ablation. Find smallest k
#     such that some k-item ablation achieves 3-way configural invariance.
#     Within that k, pick by CFI -> TLI -> RMSEA cascade. If no combo at
#     any k <= n_items - min_items passes, stop and report failure.
#   - Metric failure with configural OK -> permuted-MI removal (one item).
#     The current marker (first item) is still excluded here since its
#     loading is fixed and has no MI; this exclusion is purely local to
#     the model being fit, not a fixed assignment.
# =============================================================================
from itertools import combinations

import pandas as pd

from .r_env import (RRuntimeError, localconverter, pandas2ri, ro, semtools,
                    set_seeds)
from .fit import (build_cfa_cmd, check_secondary_criteria, extract_p,
                  push_model_to_r)

DEFAULT_CFI_TIE_TOLERANCE = 0.001
DEFAULT_TLI_TIE_TOLERANCE = 0.001


def cfa_test_metric_with_mi(scalename, list_of_items, mydata_python, mydata_temp_path,
                            num_iter, cpus_to_use, configural_only=False,
                            parameterization="theta", ordered=None):
    set_seeds(12345)

    if ordered is None:
        ordered = list_of_items

    push_model_to_r(scalename, list_of_items, mydata_python, mydata_temp_path)

    fit_config = ro.r(build_cfa_cmd(ordered, parameterization))
    ro.globalenv['fit_config'] = fit_config
    out_config = semtools.permuteMeasEq(
        nPermute=num_iter, con=fit_config,
        parallelType="multicore", ncpus=cpus_to_use)
    config_p = float(extract_p(out_config))
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
        'metric_p':              None,
        'metric_passed':         None,
        'item_mis':              None,
    }
    if configural_only or not config_passed:
        return result

    fit_metric = ro.r(build_cfa_cmd(ordered, parameterization, group_equal="loadings"))
    ro.globalenv['fit_metric'] = fit_metric

    try:
        out_metric = semtools.permuteMeasEq(
            nPermute=num_iter, uncon=fit_config, con=fit_metric,
            param="loadings",
            parallelType="multicore", ncpus=cpus_to_use)
    except RRuntimeError:
        # sometimes this fit fails in forked workers; retry with fewer
        # workers, then serially
        try:
            out_metric = semtools.permuteMeasEq(
                nPermute=num_iter, uncon=fit_config, con=fit_metric,
                param="loadings",
                parallelType="multicore", ncpus=cpus_to_use // 2)
        except RRuntimeError:
            out_metric = semtools.permuteMeasEq(
                nPermute=num_iter, uncon=fit_config, con=fit_metric,
                param="loadings",
                parallelType="no", ncpus=cpus_to_use // 2)

    ro.globalenv['out_metric'] = out_metric
    metric_p = float(extract_p(out_metric))
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
    highest sum. excluded_item is dropped from candidacy (typically the
    current model's marker, whose loading is fixed and has no MI).
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
    all_metric_passed = True
    metric_evaluable = True

    for name, r in pair_results.items():
        row[f'{name}_config_p']              = r['config_p']
        row[f'{name}_config_passed']         = r['config_passed']
        row[f'{name}_config_passed_primary'] = r['config_passed_primary']
        row[f'{name}_config_cfi']            = r['config_cfi']
        row[f'{name}_config_tli']            = r['config_tli']
        row[f'{name}_config_rmsea']          = r['config_rmsea']
        row[f'{name}_metric_p']              = r['metric_p']
        row[f'{name}_metric_passed']         = r['metric_passed']

        cfis.append(r['config_cfi'])
        tlis.append(r['config_tli'])
        rmseas.append(r['config_rmsea'])
        if not r['config_passed']:
            all_config_passed = False
            metric_evaluable = False
        if r['metric_passed'] is None:
            metric_evaluable = False
        elif not r['metric_passed']:
            all_metric_passed = False

    row['min_config_cfi']    = min(cfis) if cfis else None
    row['min_config_tli']    = min(tlis) if tlis else None
    row['max_config_rmsea']  = max(rmseas) if rmseas else None
    row['all_config_passed'] = all_config_passed
    row['all_metric_passed'] = (all_metric_passed if metric_evaluable else None)
    row['action']            = action
    row['removed_items']     = removed_items
    row['removal_reason']    = removal_reason
    row['cfi_tied_count']    = cfi_tied_count
    row['tli_tied_count']    = tli_tied_count
    row['mis_used']          = mis_used
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
    candidates -- the marker is now ablatable; when removed, the new
    first item implicitly becomes the marker for the resulting model.
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


def do_three_way_cfa_stepwise_mi(whichscale, orig_items, datasets, temp_path,
                                 num_iter, cpus_to_use,
                                 min_items=3,
                                 max_iter=None,
                                 drop_idx=None,
                                 cfi_tie_tolerance=DEFAULT_CFI_TIE_TOLERANCE,
                                 tli_tie_tolerance=DEFAULT_TLI_TIE_TOLERANCE,
                                 parameterization="theta"):
    """
    Stepwise CFA with multi-level combinatorial ablation for configural
    failures and MI-based single-item removal for metric failures.

    The marker is ablatable: any item (including the first in the original
    scale) can be removed during configural ablation. After a marker
    removal, the new first item of the remaining list becomes the marker
    for subsequent model fits (lavaan's default behavior). At metric-MI
    steps, the *current* marker (current[0] at that step) is excluded
    from MI consideration because its loading is fixed and has no MI.

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
        {'cfi_max_min', 'tli_tiebreaker', 'rmsea_tiebreaker', 'mi_worst',
         None}.
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
        print(f"\n--- Iteration {it}: {len(current)} items "
              f"(marker = {current[0]}) ---")
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
        all_metric = all(r['metric_passed'] is True
                         for r in main_results.values()) if all_config else False

        if all_config and all_metric:
            print(f"\n*** 3-way metric invariance achieved with {len(current)} items ***")
            row = _build_history_row(it, 'main', current, None, main_results,
                                     action='success')
            history_rows.append(row)
            return current, removed, pd.DataFrame(history_rows)

        # ----- Configural failure: combinatorial ablation (marker ablatable) -----
        if not all_config:
            print("Configural failed for at least one comparison; running "
                  "combinatorial ablation search (all items, incl. marker)...")
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

        # ----- Configural OK, metric failed: single-item MI removal -----
        # The marker for the *current* fit is current[0]; exclude it from
        # MI candidacy (its loading is fixed). If a prior ablation step
        # changed who current[0] is, that change naturally carries through.
        print(f"Configural OK but metric failed; running MI-based removal "
              f"(excluding current marker {current[0]})...")
        failing_mis = []
        for r in main_results.values():
            if r['metric_passed'] is False and r['item_mis']:
                failing_mis.append(r['item_mis'])

        worst, aggregated = find_worst_item(failing_mis,
                                            excluded_item=current[0],
                                            current_items=current)

        if worst is None:
            print("  Could not identify a worst item from MIs. Stopping.")
            row = _build_history_row(it, 'main', current, None, main_results,
                                     action='failed_no_mi', mis_used=aggregated)
            history_rows.append(row)
            return None, removed, pd.DataFrame(history_rows)

        print(f"  Aggregated MIs (summed over failing comparisons):")
        for item, mi in sorted(aggregated.items(), key=lambda kv: -kv[1]):
            print(f"    {item}: {mi:.3f}")
        print(f"  -> Removing: {worst}")

        row = _build_history_row(it, 'main', current, None, main_results,
                                 action='metric_mi_removal',
                                 removed_items=(worst,),
                                 removal_reason='mi_worst',
                                 mis_used=aggregated)
        history_rows.append(row)

        removed.append(worst)
        current.remove(worst)

    print(f"\nHit max_iter ({max_iter}) without convergence.")
    history_rows.append({
        'iteration': max_iter + 1, 'phase': 'final',
        'n_items': len(current), 'items': tuple(current),
        'action': 'failed_max_iter',
    })
    return None, removed, pd.DataFrame(history_rows)
