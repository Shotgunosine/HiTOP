# =============================================================================
# Stepwise CFA for scalar invariance (v3).
#
# New in v3:
#   - Can resume from a completed metric stepwise run. The metric notebook
#     saves per-scale histories as ``cfa_dir / f'{scale}_history.pkl'`` and a
#     summary as ``cfa_dir / 'stepwise.pkl'``; ``load_metric_run`` reads the
#     per-scale history (falling back to the summary) and returns the
#     metric-invariant core, and ``do_stepwise_scalar_from_metric_run`` wires
#     that straight into the scalar search.
#   - Because the metric run already verified configural + metric invariance
#     for the core (same data, same seeds, same parameterization), the first
#     iteration skips the configural and metric permutation tests and runs
#     only the scalar test (``assume_metric_invariant=True``). The models are
#     still fit (permuteMeasEq needs the lavaan objects); only the two
#     redundant permutation tests are skipped, saving ~6 permutation runs.
#     History rows record ``lower_levels_assumed=True`` for transparency.
#     Set ``assume_metric_invariant=False`` to re-verify everything.
#
# Also brought in line with stepwise_metric v7:
#   - Marker is ablatable during configural ablation; the current marker is
#     whichever item is first in the remaining list (lavaan's default).
#   - Configural regression is handled by bounded combinatorial multi-level
#     ablation, filtering candidates by all_config_passed before the
#     CFI -> TLI -> RMSEA cascade (imported from stepwise_metric).
#   - History rows use ``removed_items`` (tuple) and ``ablation_level``.
#
# Removal logic by level (unchanged in spirit):
#   - configural regression (defensive)  -> combinatorial ablation
#   - metric regression (defensive)      -> single-item loading-MI removal
#   - scalar failure (the main case)     -> single-item intercept-MI removal
# =============================================================================
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from .r_env import (RRuntimeError, localconverter, pandas2ri, ro, semtools,
                    set_seeds)
from .fit import (build_cfa_cmd, check_secondary_criteria, extract_p,
                  push_model_to_r)
from .stepwise_metric import (DEFAULT_CFI_TIE_TOLERANCE,
                              DEFAULT_TLI_TIE_TOLERANCE,
                              _pick_by_cascade,
                              extract_item_mis_from_metric, find_worst_item)


# -----------------------------------------------------------------------------
# Loading a completed metric stepwise run
# -----------------------------------------------------------------------------
def load_metric_run(cfa_dir, scale):
    """Load the metric-invariant core for ``scale`` from a completed metric
    stepwise run.

    Looks for ``cfa_dir / f'{scale}_history.pkl'`` first (the per-scale
    history written by the metric loop in NB_2_cfa_as_reg). If that file is
    missing, falls back to the ``stepwise.pkl`` summary (or
    ``stepwise_in_progress.pkl`` if the final summary isn't there).

    Returns
    -------
    metric_core : list[str] or None
        The metric-invariant item set, or None if the metric run did not
        find one for this scale.
    metric_history : pd.DataFrame or None
        The full metric history when loaded from the per-scale pickle;
        None when only the summary was available.
    """
    cfa_dir = Path(cfa_dir)

    hist_path = cfa_dir / f'{scale}_history.pkl'
    if hist_path.exists():
        history = pd.read_pickle(hist_path)
        success = history[history['action'] == 'success']
        if len(success) == 0:
            return None, history
        return list(success.iloc[-1]['items']), history

    for summary_name in ('stepwise.pkl', 'stepwise_in_progress.pkl'):
        summary_path = cfa_dir / summary_name
        if summary_path.exists():
            summary = pd.read_pickle(summary_path)
            row = summary[summary['scale'] == scale]
            if len(row) == 0:
                continue
            item_nos = row.iloc[-1].get('item_nos')
            if item_nos is None or (np.isscalar(item_nos) and pd.isna(item_nos)):
                return None, None
            return list(item_nos), None

    raise FileNotFoundError(
        f"No metric run found for {scale!r} in {cfa_dir} "
        f"(looked for {scale}_history.pkl, stepwise.pkl, "
        f"stepwise_in_progress.pkl)")


# -----------------------------------------------------------------------------
# Hierarchical CFA test for ONE pairwise comparison, up to scalar.
# -----------------------------------------------------------------------------
def cfa_test_scalar_with_mi(scalename, list_of_items, mydata_python, mydata_temp_path,
                            num_iter, cpus_to_use, max_level='scalar',
                            parameterization="theta", ordered=None,
                            skip_lower_tests=False):
    """
    Parameters
    ----------
    max_level : {'configural', 'metric', 'scalar'}
        Highest invariance level to test. Lower levels are always tested
        first; the test sequence stops at the first failure or at max_level.
    skip_lower_tests : bool
        If True, fit the configural and metric models but skip their
        permutation tests, treating both levels as passed. Only valid when
        the caller has already verified configural + metric invariance for
        exactly these items on exactly this data (e.g. resuming from a
        completed metric stepwise run: fixed seeds make the skipped tests
        deterministic re-runs). config_p / metric_p are recorded as NaN.

    Returns
    -------
    dict with keys:
        config_p, config_passed, config_passed_primary,
        config_cfi, config_tli, config_rmsea,
        metric_p, metric_passed, metric_item_mis,
        scalar_p, scalar_passed, scalar_item_mis,
        lower_levels_assumed
    metric_item_mis is the dict of LOADING MIs (op == "=~") populated only
    when metric failed. scalar_item_mis is the dict of INTERCEPT MIs
    (op == "~1") populated only when scalar failed.
    """
    set_seeds(12345)

    if ordered is None:
        ordered = list_of_items

    push_model_to_r(scalename, list_of_items, mydata_python, mydata_temp_path)

    # ----- Configural -----
    # The configural model must be fit even when skipping its permutation
    # test: permuteMeasEq(uncon=fit_config, ...) needs the lavaan object.
    fit_config = ro.r(build_cfa_cmd(ordered, parameterization))
    ro.globalenv['fit_config'] = fit_config

    if skip_lower_tests:
        config_p = np.nan
        config_passed_primary = True
        config_passed = True
        # fit indices are cheap (no permutations) -- keep them for the record
        _, cfi, tli, rmsea = check_secondary_criteria(fit_config)
    else:
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
        'lower_levels_assumed':  skip_lower_tests,
    }

    if max_level == 'configural' or not config_passed:
        return result

    # ----- Metric -----
    fit_metric = ro.r(build_cfa_cmd(ordered, parameterization, group_equal="loadings"))
    ro.globalenv['fit_metric'] = fit_metric

    if skip_lower_tests:
        result['metric_p'] = np.nan
        result['metric_passed'] = True
    else:
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

    if max_level == 'metric' or not result['metric_passed']:
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
                           parameterization="theta", skip_lower_tests=False):
    results = {}
    for name, data in datasets.items():
        results[name] = cfa_test_scalar_with_mi(
            scalename, items, data, temp_path,
            num_iter=num_iter, cpus_to_use=cpus_to_use,
            max_level=max_level, parameterization=parameterization,
            skip_lower_tests=skip_lower_tests)
    return results


def _build_history_row_scalar(iteration, phase, items, candidate_dropped,
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
    all_scalar_passed = True
    metric_evaluable = True
    scalar_evaluable = True
    lower_assumed = False

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
        lower_assumed = lower_assumed or r.get('lower_levels_assumed', False)

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

    row['min_config_cfi']       = min(cfis) if cfis else None
    row['min_config_tli']       = min(tlis) if tlis else None
    row['max_config_rmsea']     = max(rmseas) if rmseas else None
    row['all_config_passed']    = all_config_passed
    row['all_metric_passed']    = (all_metric_passed if metric_evaluable else None)
    row['all_scalar_passed']    = (all_scalar_passed if scalar_evaluable else None)
    row['lower_levels_assumed'] = lower_assumed
    row['action']               = action
    row['removed_items']        = removed_items
    row['removal_reason']       = removal_reason
    row['cfi_tied_count']       = cfi_tied_count
    row['tli_tied_count']       = tli_tied_count
    row['mis_used']             = mis_used
    return row


def _search_combo_ablation_scalar(whichscale, current, min_items, iteration,
                                  cfi_tie_tolerance, tli_tie_tolerance,
                                  history_rows, datasets, temp_path,
                                  num_iter, cpus_to_use,
                                  parameterization="theta"):
    """
    Search the smallest combo size k such that some k-item ablation
    achieves 3-way configural invariance. ALL items in ``current`` are
    candidates -- the marker is ablatable; when removed, the new first
    item implicitly becomes the marker for the resulting model. Candidates
    are evaluated configural-only and filtered by all_config_passed before
    the CFI -> TLI -> RMSEA cascade.
    """
    candidates_pool = list(current)
    max_level_combo = len(current) - min_items
    if max_level_combo < 1:
        return None, None, None, None, None

    for level in range(1, max_level_combo + 1):
        n_combos = sum(1 for _ in combinations(candidates_pool, level))
        print(f"  -- Ablation level {level} ({n_combos} combos) --")

        passing = []
        n_evaluated = 0
        for combo in combinations(candidates_pool, level):
            test_items = [i for i in current if i not in combo]

            combo_label = combo if len(combo) > 1 else combo[0]
            print(f"  Trying drop of {combo_label} -> {len(test_items)} items")
            cand_results = _test_all_pairs_scalar(
                whichscale, test_items, datasets, temp_path,
                num_iter, cpus_to_use, max_level='configural',
                parameterization=parameterization)
            cand_row = _build_history_row_scalar(
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


# -----------------------------------------------------------------------------
# Top-level: stepwise removal targeting scalar invariance, starting from
# a set of metric-invariant items.
# -----------------------------------------------------------------------------
def do_three_way_cfa_stepwise_scalar(whichscale,
                                     metric_invariant_items,
                                     datasets, temp_path,
                                     num_iter, cpus_to_use,
                                     min_items=3,
                                     max_iter=None,
                                     cfi_tie_tolerance=DEFAULT_CFI_TIE_TOLERANCE,
                                     tli_tie_tolerance=DEFAULT_TLI_TIE_TOLERANCE,
                                     parameterization="theta",
                                     assume_metric_invariant=True):
    """
    Search for a 3-way scalar invariant subset starting from a metric-
    invariant core, by iteratively removing the item with the largest
    aggregated permuted intercept modification index. Handles regressions
    at lower levels defensively: configural regression triggers bounded
    combinatorial ablation (marker ablatable, all_config_passed filter,
    CFI -> TLI -> RMSEA cascade); metric regression triggers single-item
    loading-MI removal.

    Parameters
    ----------
    whichscale : str
    metric_invariant_items : list[str]
        The metric-invariant core from the upstream procedure (e.g. loaded
        via ``load_metric_run``).
    datasets : dict
        pair label -> dataframe for each pairwise comparison.
    min_items : int
    max_iter : int or None
    cfi_tie_tolerance, tli_tie_tolerance : float
        Same semantics as in the metric procedure.
    assume_metric_invariant : bool
        If True (default), the first iteration skips the configural and
        metric permutation tests, since the metric stepwise run already
        verified them for exactly this item set on this data with the same
        seeds. Later iterations (after any removal) always run full tests.
        Set False to re-verify everything from scratch.

    Returns
    -------
    final_items : list[str] or None
    removed_in_order : list[str]
    history : pd.DataFrame
        One row per test (main or ablation candidate). Columns include
        per-pair config/metric/scalar pass-fail and p-values, aggregate
        fit indices, ``lower_levels_assumed``, ``removed_items`` (tuple),
        ``ablation_level``, and removal decisions. removal_reason takes
        values in {'cfi_max_min', 'tli_tiebreaker', 'rmsea_tiebreaker',
        'metric_mi_worst', 'scalar_mi_worst', None}.
    """
    print(f"\n{'='*60}\nSTEPWISE SCALAR: {whichscale.upper()}\n{'='*60}")

    current = list(metric_invariant_items)
    removed = []
    history_rows = []

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

        # Skip config/metric permutation tests only on the untouched core:
        # the metric run verified exactly these items on this data.
        skip_lower = assume_metric_invariant and it == 0 and not removed
        if skip_lower:
            print("Testing current item set (configural + metric assumed "
                  "from completed metric run; scalar test only)...")
        else:
            print("Testing current item set up to scalar...")
        main_results = _test_all_pairs_scalar(whichscale, current, datasets,
                                              temp_path, num_iter, cpus_to_use,
                                              max_level='scalar',
                                              parameterization=parameterization,
                                              skip_lower_tests=skip_lower)

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

        # --- Configural regression (defensive): combinatorial ablation ---
        # Can't occur on a skip_lower iteration (config assumed True there);
        # only reachable after an item removal has changed the set.
        if not all_config:
            print("Configural regressed; running combinatorial ablation "
                  "search (all items, incl. marker)...")
            row = _build_history_row_scalar(it, 'main', current, None,
                                            main_results,
                                            action='configural_ablation_starting')
            history_rows.append(row)
            main_row_idx = len(history_rows) - 1

            best_combo, reason, level, cfi_tc, tli_tc = _search_combo_ablation_scalar(
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
            history_rows[main_row_idx]['removed_items']   = tuple(best_combo)
            history_rows[main_row_idx]['removal_reason']  = reason
            history_rows[main_row_idx]['ablation_level']  = level
            history_rows[main_row_idx]['cfi_tied_count']  = cfi_tc
            history_rows[main_row_idx]['tli_tied_count']  = tli_tc

            for item in best_combo:
                removed.append(item)
                current.remove(item)
            continue

        # --- Metric regression (defensive): single-item loading-MI removal ---
        if not all_metric:
            print(f"Metric regressed; running loading-MI-based removal "
                  f"(excluding current marker {current[0]})...")
            failing_mis = []
            for r in main_results.values():
                if r['metric_passed'] is False and r['metric_item_mis']:
                    failing_mis.append(r['metric_item_mis'])

            worst, aggregated = find_worst_item(failing_mis,
                                                excluded_item=current[0],
                                                current_items=current)
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
                                            removed_items=(worst,),
                                            removal_reason='metric_mi_worst',
                                            mis_used=aggregated)
            history_rows.append(row)
            removed.append(worst)
            current.remove(worst)
            continue

        # --- Scalar failure: intercept MI removal (the main case) ---
        print(f"Scalar failed; running intercept-MI-based removal "
              f"(excluding current marker {current[0]})...")
        failing_mis = []
        for r in main_results.values():
            if r['scalar_passed'] is False and r['scalar_item_mis']:
                failing_mis.append(r['scalar_item_mis'])

        worst, aggregated = find_worst_item(failing_mis,
                                            excluded_item=current[0],
                                            current_items=current)
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
                                        removed_items=(worst,),
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


# -----------------------------------------------------------------------------
# Convenience wrapper: load a completed metric run and continue to scalar.
# -----------------------------------------------------------------------------
def do_stepwise_scalar_from_metric_run(whichscale, cfa_dir,
                                       datasets, temp_path,
                                       num_iter, cpus_to_use,
                                       **kwargs):
    """Load the metric-invariant core for ``whichscale`` from a completed
    metric stepwise run (see ``load_metric_run``) and continue searching
    for a scalar-invariant core from there.

    Any additional keyword arguments (min_items, max_iter, tolerances,
    parameterization, assume_metric_invariant) are forwarded to
    ``do_three_way_cfa_stepwise_scalar``.

    Returns
    -------
    final_items : list[str] or None
        None either when the metric run found no invariant core for this
        scale (nothing to continue from) or when the scalar search failed.
    removed_in_order : list[str]
    history : pd.DataFrame
        A one-row DataFrame with action 'no_metric_core' when the metric
        run had no core for this scale; otherwise the scalar history.
    """
    metric_core, _metric_history = load_metric_run(cfa_dir, whichscale)

    if metric_core is None:
        print(f"[{whichscale}] Metric run found no invariant core; "
              f"nothing to continue from.")
        history = pd.DataFrame([{
            'iteration': 0, 'phase': 'final', 'n_items': 0,
            'items': tuple(), 'action': 'no_metric_core',
        }])
        return None, [], history

    print(f"[{whichscale}] Loaded metric-invariant core "
          f"({len(metric_core)} items): {metric_core}")

    return do_three_way_cfa_stepwise_scalar(
        whichscale, metric_core, datasets, temp_path,
        num_iter, cpus_to_use, **kwargs)