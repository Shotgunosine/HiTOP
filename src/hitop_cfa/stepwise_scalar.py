# =============================================================================
# Stepwise CFA for scalar invariance (v1).
# Takes a set of metric-invariant items and searches for a scalar-invariant
# core via stepwise item removal, following the same prereg-consistent
# pattern as the metric procedure:
#   - If a lower level fails after item removal (configural or metric):
#     handle that first (CFI-ablation for configural, loading MIs for metric)
#   - At scalar level: remove items based on permuted maximum INTERCEPT
#     modification index (mirrors the loading-MI logic from metric)
#
# Returns a DataFrame with one row per test (main or ablation candidate)
# and a parallel set of columns to the metric procedure plus scalar_*
# fields.
#
# Note: this implements item removal at scalar, matching the preregistration
# ("remove items from the scale in step-wise order"). The methodologically
# more common alternative is partial scalar invariance (free a single
# intercept rather than dropping the item), which is implemented separately
# elsewhere. Item removal is more aggressive but produces a cleaner "core
# set of scalar-invariant items" that matches what the preregistration
# asked for.
# =============================================================================
import pandas as pd

from .r_env import (RRuntimeError, localconverter, pandas2ri, ro, semtools,
                    set_seeds)
from .fit import (build_cfa_cmd, check_secondary_criteria, extract_p,
                  push_model_to_r)
from .stepwise_metric import (DEFAULT_CFI_TIE_TOLERANCE,
                              DEFAULT_TLI_TIE_TOLERANCE,
                              extract_item_mis_from_metric, find_worst_item)


# -----------------------------------------------------------------------------
# Hierarchical CFA test for ONE pairwise comparison, up to scalar.
# -----------------------------------------------------------------------------
def cfa_test_scalar_with_mi(scalename, list_of_items, mydata_python, mydata_temp_path,
                            num_iter, cpus_to_use, max_level='scalar',
                            parameterization="theta", ordered=None):
    """
    Parameters
    ----------
    max_level : {'configural', 'metric', 'scalar'}
        Highest invariance level to test. Lower levels are always tested
        first; the test sequence stops at the first failure or at max_level.

    Returns
    -------
    dict with keys:
        config_p, config_passed, config_passed_primary,
        config_cfi, config_tli, config_rmsea,
        metric_p, metric_passed, metric_item_mis,
        scalar_p, scalar_passed, scalar_item_mis
    metric_item_mis is the dict of LOADING MIs (op == "=~") populated only
    when metric failed. scalar_item_mis is the dict of INTERCEPT MIs
    (op == "~1") populated only when scalar failed.
    """
    set_seeds(12345)

    if ordered is None:
        ordered = list_of_items

    push_model_to_r(scalename, list_of_items, mydata_python, mydata_temp_path)

    # ----- Configural -----
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
        'metric_item_mis':       None,
        'scalar_p':              None,
        'scalar_passed':         None,
        'scalar_item_mis':       None,
    }

    if max_level == 'configural' or not config_passed:
        return result

    # ----- Metric -----
    fit_metric = ro.r(build_cfa_cmd(ordered, parameterization, group_equal="loadings"))
    ro.globalenv['fit_metric'] = fit_metric

    try:
        out_metric = semtools.permuteMeasEq(
            nPermute=num_iter, uncon=fit_config, con=fit_metric,
            param="loadings",
            parallelType="multicore", ncpus=cpus_to_use)
    except RRuntimeError:
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
        result['metric_item_mis'] = extract_item_mis_from_metric(list_of_items)

    if max_level == 'metric' or not metric_passed:
        return result

    # ----- Scalar -----
    fit_scalar = ro.r(build_cfa_cmd(ordered, parameterization,
                                    group_equal=["loadings", "intercepts"]))
    ro.globalenv['fit_scalar'] = fit_scalar

    try:
        out_scalar = semtools.permuteMeasEq(
            nPermute=num_iter, uncon=fit_metric, con=fit_scalar,
            param=ro.StrVector(["loadings", "intercepts"]),
            parallelType="multicore", ncpus=cpus_to_use)
    except RRuntimeError:
        try:
            out_scalar = semtools.permuteMeasEq(
                nPermute=num_iter, uncon=fit_metric, con=fit_scalar,
                param=ro.StrVector(["loadings", "intercepts"]),
                parallelType="multicore", ncpus=cpus_to_use // 2)
        except RRuntimeError:
            out_scalar = semtools.permuteMeasEq(
                nPermute=num_iter, uncon=fit_metric, con=fit_scalar,
                param=ro.StrVector(["loadings", "intercepts"]),
                parallelType="no", ncpus=cpus_to_use // 2)

    ro.globalenv['out_scalar'] = out_scalar
    scalar_p = float(extract_p(out_scalar))
    scalar_passed = (scalar_p >= 0.05)
    result['scalar_p'] = scalar_p
    result['scalar_passed'] = scalar_passed
    if not scalar_passed:
        result['scalar_item_mis'] = extract_item_mis_from_scalar(list_of_items)

    return result


# -----------------------------------------------------------------------------
# Extract per-item INTERCEPT MIs from the scalar model's permuteMeasEq.
# At scalar, the new constraints added on top of metric are intercept
# equalities (op == "~1" in lavaan). The MIs of interest are these
# intercept MIs -- which item's intercept most differs across groups.
# -----------------------------------------------------------------------------
def extract_item_mis_from_scalar(item_list):
    """
    The scalar @MI.obs contains MIs for both loading and intercept
    equality constraints (because permuteMeasEq was called with
    param=c("loadings", "intercepts")). We filter to intercepts only --
    those are the new constraints whose violations characterize scalar
    misfit specifically.

    Returns dict[item -> max MI across non-reference groups], or None.
    """
    try:
        ro.r('''
            mi_obs <- out_scalar@MI.obs
            pt     <- out_scalar@PT
            mi_obs$par_name <- pt$par[ match(mi_obs$lhs, pt$plabel) ]
            mi_intercepts <- mi_obs[grepl("~1$", mi_obs$par_name), ]
            if (nrow(mi_intercepts) > 0) {
                mi_intercepts$item <- sub("~1$", "", mi_intercepts$par_name)
            }
        ''')
        mi_df_r = ro.r('mi_intercepts')
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
        print(f"  [WARN] Could not extract intercept MIs from scalar model: {e}")
        return None


def _test_all_pairs_scalar(scalename, items, datasets, temp_path,
                           num_iter, cpus_to_use, max_level='scalar',
                           parameterization="theta"):
    results = {}
    for name, data in datasets.items():
        results[name] = cfa_test_scalar_with_mi(
            scalename, items, data, temp_path,
            num_iter=num_iter, cpus_to_use=cpus_to_use,
            max_level=max_level, parameterization=parameterization)
    return results


def _build_history_row_scalar(iteration, phase, items, candidate_dropped,
                              pair_results, action=None, removed_item=None,
                              removal_reason=None, mis_used=None,
                              cfi_tied_count=None, tli_tied_count=None):
    row = {
        'iteration':         iteration,
        'phase':             phase,
        'candidate_dropped': candidate_dropped,
        'n_items':           len(items),
        'items':             tuple(items),
    }
    cfis, tlis, rmseas = [], [], []
    all_config_passed = True
    all_metric_passed = True
    all_scalar_passed = True
    metric_evaluable = True
    scalar_evaluable = True

    for name, r in pair_results.items():
        row[f'{name}_config_p']              = r['config_p']
        row[f'{name}_config_passed']         = r['config_passed']
        row[f'{name}_config_passed_primary'] = r['config_passed_primary']
        row[f'{name}_config_cfi']            = r['config_cfi']
        row[f'{name}_config_tli']            = r['config_tli']
        row[f'{name}_config_rmsea']          = r['config_rmsea']
        row[f'{name}_metric_p']              = r['metric_p']
        row[f'{name}_metric_passed']         = r['metric_passed']
        row[f'{name}_scalar_p']              = r['scalar_p']
        row[f'{name}_scalar_passed']         = r['scalar_passed']

        cfis.append(r['config_cfi'])
        tlis.append(r['config_tli'])
        rmseas.append(r['config_rmsea'])

        if not r['config_passed']:
            all_config_passed = False
            metric_evaluable = False
            scalar_evaluable = False
        if r['metric_passed'] is None:
            metric_evaluable = False
            scalar_evaluable = False
        elif not r['metric_passed']:
            all_metric_passed = False
            scalar_evaluable = False
        if r['scalar_passed'] is None:
            scalar_evaluable = False
        elif not r['scalar_passed']:
            all_scalar_passed = False

    row['min_config_cfi']    = min(cfis) if cfis else None
    row['min_config_tli']    = min(tlis) if tlis else None
    row['max_config_rmsea']  = max(rmseas) if rmseas else None
    row['all_config_passed'] = all_config_passed
    row['all_metric_passed'] = (all_metric_passed if metric_evaluable else None)
    row['all_scalar_passed'] = (all_scalar_passed if scalar_evaluable else None)
    row['action']            = action
    row['removed_item']      = removed_item
    row['removal_reason']    = removal_reason
    row['cfi_tied_count']    = cfi_tied_count
    row['tli_tied_count']    = tli_tied_count
    row['mis_used']          = mis_used
    return row


# -----------------------------------------------------------------------------
# Top-level: stepwise removal targeting scalar invariance, starting from
# a set of metric-invariant items.
# -----------------------------------------------------------------------------
def do_three_way_cfa_stepwise_scalar(whichscale,
                                     metric_invariant_items,
                                     datasets, temp_path,
                                     num_iter, cpus_to_use,
                                     marker_item=None,
                                     min_items=3,
                                     max_iter=None,
                                     cfi_tie_tolerance=DEFAULT_CFI_TIE_TOLERANCE,
                                     tli_tie_tolerance=DEFAULT_TLI_TIE_TOLERANCE,
                                     parameterization="theta"):
    """
    Search for a 3-way scalar invariant subset starting from a metric-
    invariant core, by iteratively removing the item with the largest
    aggregated permuted modification index. Handles regressions at lower
    levels (configural, metric) defensively in case item removal causes
    them to fail again.

    Parameters
    ----------
    whichscale : str
    metric_invariant_items : list[str]
        The metric-invariant core from the upstream procedure.
    datasets : dict
        pair label -> dataframe for each pairwise comparison.
    marker_item : str or None
        Item whose loading is fixed to 1 and intercept fixed to 0 (in the
        reference group). Defaults to the first item in
        metric_invariant_items, matching the original scale's marker.
    min_items : int
    max_iter : int or None
    cfi_tie_tolerance, tli_tie_tolerance : float
        Same semantics as in the metric procedure.

    Returns
    -------
    final_items : list[str] or None
    removed_in_order : list[str]
    history : pd.DataFrame
        One row per test (main or ablation candidate). Columns include
        per-pair config/metric/scalar pass-fail and p-values, aggregate
        fit indices, removal decisions, and tied-count diagnostics.
        removal_reason takes values in
        {'cfi_max_min', 'tli_tiebreaker', 'rmsea_tiebreaker',
         'metric_mi_worst', 'scalar_mi_worst', None}.
    """
    print(f"\n{'='*60}\nSTEPWISE SCALAR: {whichscale.upper()}\n{'='*60}")

    current = list(metric_invariant_items)
    if marker_item is None:
        marker_item = current[0]
    elif marker_item not in current:
        raise ValueError(f"marker_item {marker_item!r} not in input items")

    removed = []
    history_rows = []

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

        # --- Test current set up to scalar ---
        print("Testing current item set up to scalar...")
        main_results = _test_all_pairs_scalar(whichscale, current, datasets,
                                              temp_path, num_iter, cpus_to_use,
                                              max_level='scalar',
                                              parameterization=parameterization)

        all_config = all(r['config_passed'] for r in main_results.values())
        all_metric = all(r['metric_passed'] is True
                         for r in main_results.values()) if all_config else False
        all_scalar = all(r['scalar_passed'] is True
                         for r in main_results.values()) if all_metric else False

        # --- Success ---
        if all_config and all_metric and all_scalar:
            print(f"\n*** 3-way scalar invariance achieved with {len(current)} items ***")
            row = _build_history_row_scalar(it, 'main', current, None,
                                            main_results, action='success')
            history_rows.append(row)
            return current, removed, pd.DataFrame(history_rows)

        # --- Configural regression: CFI ablation ---
        # This shouldn't happen since we started from a metric-invariant
        # core (which already implies configural), but handle defensively
        # in case item removal at scalar causes some pair to regress.
        if not all_config:
            print("Configural regressed for at least one comparison; running "
                  "CFI-based ablation (configural_only for candidates)...")
            row = _build_history_row_scalar(it, 'main', current, None,
                                            main_results,
                                            action='configural_ablation_starting')
            history_rows.append(row)
            main_row_idx = len(history_rows) - 1

            candidates = [i for i in current if i != marker_item]
            ablation_results = []
            for cand in candidates:
                test_items = [i for i in current if i != cand]
                if len(test_items) < min_items:
                    continue
                print(f"  Trying drop of {cand} -> {len(test_items)} items")
                cand_results = _test_all_pairs_scalar(
                    whichscale, test_items, datasets, temp_path,
                    num_iter, cpus_to_use, max_level='configural',
                    parameterization=parameterization)
                cand_row = _build_history_row_scalar(
                    it, 'ablation_candidate', test_items, cand, cand_results,
                    action='ablation_candidate_tested')
                cmc = cand_row['min_config_cfi']
                cmt = cand_row['min_config_tli']
                cmr = cand_row['max_config_rmsea']
                history_rows.append(cand_row)
                print(f"    min_cfi={cmc:.4f} min_tli={cmt:.4f} "
                      f"max_rmsea={cmr:.4f}")
                if cmc is not None:
                    ablation_results.append((cand, cmc, cmt, cmr))

            if not ablation_results:
                print("  No viable ablation candidate. Stopping.")
                history_rows.append({
                    'iteration': it, 'phase': 'final',
                    'n_items': len(current), 'items': tuple(current),
                    'action': 'failed_no_ablation_candidate',
                })
                return None, removed, pd.DataFrame(history_rows)

            # CFI -> TLI -> RMSEA tiebreaker cascade (same as in metric procedure)
            max_cfi = max(r[1] for r in ablation_results)
            cfi_tied = [r for r in ablation_results
                        if r[1] >= max_cfi - cfi_tie_tolerance]
            cfi_tied_count = len(cfi_tied)

            if cfi_tied_count == 1:
                best = cfi_tied[0]; removal_reason = 'cfi_max_min'
                tli_tied_count = None
            else:
                max_tli = max(r[2] for r in cfi_tied)
                tli_tied = [r for r in cfi_tied
                            if r[2] >= max_tli - tli_tie_tolerance]
                tli_tied_count = len(tli_tied)
                if tli_tied_count == 1:
                    best = tli_tied[0]; removal_reason = 'tli_tiebreaker'
                else:
                    best = min(tli_tied, key=lambda r: r[3])
                    removal_reason = 'rmsea_tiebreaker'

            best_candidate = best[0]
            print(f"  -> Removing {best_candidate} (reason={removal_reason})")
            history_rows[main_row_idx]['removed_item']    = best_candidate
            history_rows[main_row_idx]['removal_reason']  = removal_reason
            history_rows[main_row_idx]['cfi_tied_count']  = cfi_tied_count
            history_rows[main_row_idx]['tli_tied_count']  = tli_tied_count
            removed.append(best_candidate)
            current.remove(best_candidate)
            continue

        # --- Metric regression: loading MI removal ---
        # Again shouldn't normally happen if we started metric-invariant,
        # but defensively handle.
        if not all_metric:
            print("Metric regressed; running loading-MI-based removal...")
            failing_mis = []
            for r in main_results.values():
                if r['metric_passed'] is False and r['metric_item_mis']:
                    failing_mis.append(r['metric_item_mis'])

            worst, aggregated = find_worst_item(failing_mis, marker_item, current)
            if worst is None:
                print("  Could not identify worst loading-MI item. Stopping.")
                row = _build_history_row_scalar(it, 'main', current, None,
                                                main_results,
                                                action='failed_no_metric_mi',
                                                mis_used=aggregated)
                history_rows.append(row)
                return None, removed, pd.DataFrame(history_rows)

            print(f"  Aggregated loading MIs (summed over failing pairs):")
            for item, mi in sorted(aggregated.items(), key=lambda kv: -kv[1]):
                print(f"    {item}: {mi:.3f}")
            print(f"  -> Removing: {worst}")

            row = _build_history_row_scalar(it, 'main', current, None,
                                            main_results,
                                            action='metric_mi_removal',
                                            removed_item=worst,
                                            removal_reason='metric_mi_worst',
                                            mis_used=aggregated)
            history_rows.append(row)
            removed.append(worst)
            current.remove(worst)
            continue

        # --- Scalar failure: intercept MI removal (the main case) ---
        print("Scalar failed; running intercept-MI-based removal...")
        failing_mis = []
        for r in main_results.values():
            if r['scalar_passed'] is False and r['scalar_item_mis']:
                failing_mis.append(r['scalar_item_mis'])

        worst, aggregated = find_worst_item(failing_mis, marker_item, current)
        if worst is None:
            print("  Could not identify worst intercept-MI item. Stopping.")
            row = _build_history_row_scalar(it, 'main', current, None,
                                            main_results,
                                            action='failed_no_scalar_mi',
                                            mis_used=aggregated)
            history_rows.append(row)
            return None, removed, pd.DataFrame(history_rows)

        print(f"  Aggregated intercept MIs (summed over failing pairs):")
        for item, mi in sorted(aggregated.items(), key=lambda kv: -kv[1]):
            print(f"    {item}: {mi:.3f}")
        print(f"  -> Removing: {worst}")

        row = _build_history_row_scalar(it, 'main', current, None, main_results,
                                        action='scalar_mi_removal',
                                        removed_item=worst,
                                        removal_reason='scalar_mi_worst',
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
