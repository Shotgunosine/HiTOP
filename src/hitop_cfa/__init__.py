"""CFA measurement-invariance machinery shared by the HiTOP validation notebooks.

Importing this package starts the embedded R session (via hitop_cfa.r_env),
so the environment must provide R with lavaan and the patched semTools.
"""
from .r_env import (RRuntimeError, lavaan, rbase, ro, semtools, set_seeds,
                    silence_r, utils)
from .lookup import build_luts, check_hitop_ids, load_item_lookup
from .fit import (build_cfa_cmd, cfa_helper_func, cfa_levels,
                  check_secondary_criteria, extract_p, nafloat,
                  print_problematic_items, print_short_summary, print_summary,
                  run_specific_cfa)
from .stepwise_metric import (cfa_test_metric_with_mi,
                              do_three_way_cfa_stepwise_mi,
                              extract_item_mis_from_metric, find_worst_item)
from .stepwise_scalar import (cfa_test_scalar_with_mi,
                              do_three_way_cfa_stepwise_scalar,
                              extract_item_mis_from_scalar)
from .exhaustive import exhaustive_cfa_ablations
