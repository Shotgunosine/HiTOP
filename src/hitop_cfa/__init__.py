"""CFA measurement-invariance machinery shared by the HiTOP validation notebooks.

Importing this package starts the embedded R session (via hitop_cfa.r_env),
so the environment must provide R with lavaan and the patched semTools.

Invariance models follow Wu & Estabrook (2016) via semTools::measEq.syntax
(ID.cat = "Wu.Estabrook.2016", ID.fac = "std.lv"); see measeq.py and
HANDOFF_measeq_fix.md for the rationale.
"""
from .r_env import (RRuntimeError, lavaan, rbase, ro, semtools, set_seeds,
                    silence_r, utils)
from .lookup import build_luts, check_hitop_ids, load_item_lookup
from .measeq import (LEVEL_NEW_PARAMS, WU_ESTABROOK_LEVELS,
                     assert_level_adds_df, build_measeq_model,
                     extract_item_mis_from_thresholds, fit_measeq_level)
from .fit import (build_cfa_cmd, cfa_helper_func, cfa_levels,
                  check_secondary_criteria, extract_p, nafloat,
                  permute_measeq_with_retry, print_problematic_items,
                  print_short_summary, print_summary, run_specific_cfa)
from .stepwise_metric import (cfa_test_metric_with_mi,
                              do_three_way_cfa_stepwise_mi,
                              extract_item_mis_from_metric, find_worst_item)
from .stepwise_scalar import (cfa_test_scalar_with_mi,
                              do_three_way_cfa_stepwise_scalar,
                              do_stepwise_scalar_from_metric_run,
                              extract_item_mis_from_scalar,
                              load_metric_run)
from .effect_size import dif_effect_sizes
from .convdiv import (ALL_HITOP_SCALES, ANX_SCALES, DEP_SCALES,
                      HITOP_SUM_SCALES, add_core_aliases,
                      add_core_sum_columns, calc_dhs,
                      check_convergent_hypotheses, divergent_results_table,
                      prepare_divergent_data, resolve_cores, run_divergent)
from .efa import (configural_efa_report, dimensionality_effect_sizes,
                  polychoric_efa)
from .exhaustive import (exhaustive_cfa_ablations,
                         exhaustive_search_scale,
                         screened_ladder_test,
                         stepwise_configural_cap)
