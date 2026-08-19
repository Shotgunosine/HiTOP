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
