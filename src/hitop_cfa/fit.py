"""Single-model CFA fitting, permutation invariance testing, and fit-criteria helpers."""
import numpy as np

from .r_env import ro, semtools, set_seeds


def build_cfa_cmd(ordered, parameterization="theta", group_equal=None):
    """Build the R ``cfa(...)`` command string.

    This is the single place the lavaan call is constructed, so the two
    notebooks cannot drift apart on estimator settings again.

    Parameters
    ----------
    ordered : True or iterable of str
        True renders ``ordered = TRUE``; an iterable of item names renders
        ``ordered = c("item1", ...)``.
    parameterization : str or None
        None omits the argument entirely (lavaan defaults to delta).
    group_equal : None, str, or list of str
        Constraints for the invariance level being fit.
    """
    parts = ['cfa(testformula_r, data = rdata, group = group, estimator = "WLSMV"']
    if parameterization is not None:
        parts.append(f'parameterization = "{parameterization}"')
    if group_equal is not None:
        if isinstance(group_equal, str):
            parts.append(f'group.equal = "{group_equal}"')
        else:
            ge_str = ', '.join(f'"{g}"' for g in group_equal)
            parts.append(f'group.equal = c({ge_str})')
    if ordered is True:
        parts.append('ordered = TRUE')
    else:
        ordered_str = ', '.join(f'"{i}"' for i in ordered)
        parts.append(f'ordered = c({ordered_str})')
    return ', '.join(parts) + ')'


def push_model_to_r(scalename, list_of_items, mydata_python, mydata_temp_path):
    """Send the lavaan formula, data (via a temp csv), and group column to R."""
    myrstring = scalename + " =~ " + " + ".join(list_of_items)
    ro.globalenv['testformula_r'] = myrstring
    # transfer data from python into R by way of a csv file
    mydata_python.to_csv(mydata_temp_path)
    ro.r(f'rdata <- read.csv("{mydata_temp_path}", header = TRUE)')
    ro.globalenv['group'] = 'whichdata'


def print_summary(obj):
    rprint = ro.r('print')
    summary = ro.r('summary')
    return rprint(summary(obj))


def print_short_summary(invariance_output):
    ro.r("myoutput <- capture.output(summary(invariance_output))")
    ro.r("stringid <- grep(\"chisq\", myoutput)")
    ro.r("print(myoutput[stringid-1])")
    ro.r("print(myoutput[stringid])")
    return (0)


def print_problematic_items(invariance_output):
    ro.r("myoutput <- capture.output(summary(invariance_output))")
    print('Problematic items:')
    ro.r("stringidsig <- grep(\"may differ between Groups\", myoutput)")
    ro.r("print(myoutput[stringidsig])")
    return (0)


def extract_p(invariance_output):
    ro.globalenv['invariance_output'] = invariance_output
    ro.r("myoutput <- capture.output(summary(invariance_output))")
    ro.r("stringid <- grep(\"chisq\", myoutput)")
    ro.r('myrline <- myoutput[stringid]')
    mypline = ro.r('myrline')[0]
    my_p = mypline.split()[-1]
    return(my_p)


def nafloat(x):
    try:
        x = float(x)
    except ValueError:
        x = np.nan
    return x


def check_secondary_criteria(fit_config):
    Criteria_passed = False
    ro.r("myoutputconfig <- capture.output(summary(fit_config, fit.measures=TRUE))")
    ro.r("stringid_cfi <- grep(\"Robust.*CFI\", myoutputconfig)")
    ro.r("cfi_line <- myoutputconfig[stringid_cfi]")
    cfiline = ro.r('cfi_line')[0]
    my_cfi = cfiline.split()[-1]
    my_cfi = nafloat(my_cfi)
    ro.r("stringid_tli <- grep(\"Robust.*TLI\", myoutputconfig)")
    ro.r("tli_line <- myoutputconfig[stringid_tli]")
    tliline = ro.r('tli_line')[0]
    my_tli = tliline.split()[-1]
    my_tli = nafloat(my_tli)
    ro.r("stringid_rmsea <- grep(\"Robust.*RMSEA\", myoutputconfig)")
    ro.r("rmsea_line <- myoutputconfig[stringid_rmsea]")
    myrmsealine = ro.r('rmsea_line')[0]
    my_rmsea = myrmsealine.split('\n')[0].split()[-1]
    my_rmsea = nafloat(my_rmsea)
    if (my_cfi > 0.95) and (my_tli > 0.95) and (my_rmsea < 0.06):
        Criteria_passed = True
    return (Criteria_passed, my_cfi, my_tli, my_rmsea)


def cfa_levels(whichcfa):
    """Map a level name to the (do_metric, do_scalar, do_strict) flags."""
    if whichcfa == 'metric':
        return True, False, False
    elif whichcfa == 'scalar':
        return True, True, False
    elif whichcfa == 'strict':
        return True, True, True
    raise ValueError(f"unknown whichcfa {whichcfa!r}")


def cfa_helper_func(scalename, list_of_items, do_metric, do_scalar, do_strict,
                    mydata_python, mydata_temp_path, num_iter, cpus_to_use,
                    parameterization="theta", ordered=None):
    # Helper CFA funct
    # Inputs:
    # --> scalename - string of scale name: 'appetite_loss'
    # --> list_of_items - list of items to test, not necessarily the full list of items for the scale: ['hitop280', 'hitop283', 'hitop109']
    # --> do_metric, do_scalar, do_strict: True/False
    # --> mydata_python - python df with data (this function will feed it to R)
    # --> mydata_temp_path - path to do an intermediate step of saving from python, then reading into R
    # --> num_iter - permutations for permuteMeasEq
    # --> cpus_to_use - workers for permuteMeasEq
    # --> parameterization - "theta" or None (None -> lavaan's delta default)
    # --> ordered - True for `ordered = TRUE`, or None to use list_of_items

    # SETTING THE SEED HERE, JUST TO BE SURE IT IS SET TO THE SAME THING EVERY TIME I RUN THIS HELPER FUNCTION
    set_seeds(12345)

    if ordered is None:
        ordered = list_of_items

    push_model_to_r(scalename, list_of_items, mydata_python, mydata_temp_path)

    flag_passed_metric = False # setting flag for metric because this level is the most important one --> we return this

    # Always do CONFIGURAL:
    flag_passed_config = False # flag for configural
    fit_config = ro.r(build_cfa_cmd(ordered, parameterization))
    ro.globalenv['fit_config'] = fit_config
    out_config = semtools.permuteMeasEq(nPermute=num_iter,
                                        con=fit_config, # In the case of testing configural invariance when modelType = "mgcfa", con is the configural model (implicitly, the unconstrained model is the saturated model, so use the defaults uncon = NULL and param = NULL).
                                        parallelType="multicore", ncpus=cpus_to_use)
    config_p = extract_p(out_config)
    if float(config_p) >= 0.05:
        print('CONFIG INVARIANT chisq p = ' + str(config_p))
        flag_passed_config = True
    else:
        (flag_passed_config, my_cfi, my_tli, my_rmsea) = check_secondary_criteria(fit_config)
        if flag_passed_config:
            print('CONFIG chisq p = ' + str(config_p))
            print('PASSED SECONDARY CRITERIA WITH CFI = ' + str(my_cfi) + ' TLI = ' + str(my_tli) + ' RMSEA = ' + str(my_rmsea))
        else:
            print('CONFIG chisq p = ' + str(config_p))
            print('FAILED SECONDARY CRITERIA WITH CFI = ' + str(my_cfi) + ' TLI = ' + str(my_tli) + ' RMSEA = ' + str(my_rmsea))

    if flag_passed_config: # only do metric if configural is passed
        if do_metric:
            # ====== METRIC =====
            fit_metric = ro.r(build_cfa_cmd(ordered, parameterization, group_equal="loadings"))
            ro.globalenv['fit_metric'] = fit_metric
            out_metric = semtools.permuteMeasEq(nPermute=num_iter,
                                                        uncon=fit_config,
                                                        con=fit_metric,
                                                        param="loadings",
                                                        parallelType="multicore", ncpus=cpus_to_use)
            metric_p = extract_p(out_metric)
            if float(metric_p) >= 0.05:
                print('METRIC INVARIANT chisq p = ' + str(metric_p))
                flag_passed_metric = True

                if do_scalar: # only do scalar if metric is passed
                    # ====== SCALAR =====
                    fit_scalar = ro.r(build_cfa_cmd(ordered, parameterization, group_equal=["loadings", "intercepts"]))
                    ro.globalenv['fit_scalar'] = fit_scalar
                    out_scalar = semtools.permuteMeasEq(nPermute=num_iter,
                                                            uncon=fit_metric,
                                                            con=fit_scalar,
                                                            param=ro.StrVector(["loadings","intercepts"]),
                                                            parallelType="multicore",
                                                            ncpus=cpus_to_use)
                    scalar_p = extract_p(out_scalar)
                    if float(scalar_p) >= 0.05:
                        print('SCALAR INVARIANT chisq p = ' + str(scalar_p))

                        if do_strict: # only do strict if scalar is passed
                            # ====== STRICT =====
                            ro.globalenv['out_scalar'] = out_scalar
                            fit_strict = ro.r(build_cfa_cmd(ordered, parameterization, group_equal=["loadings", "intercepts", "residuals"]))
                            ro.globalenv['fit_strict'] = fit_strict
                            out_strict = semtools.permuteMeasEq(nPermute=num_iter,
                                                                        uncon=fit_scalar,
                                                                        con=fit_strict,
                                                                        param=ro.StrVector(["loadings","intercepts", "residuals"]),
                                                                        parallelType="multicore",
                                                                        ncpus=cpus_to_use)
                            strict_p = extract_p(out_strict)
                            if float(strict_p) >= 0.05:
                                print('STRICT INVARIANT chisq p = ' + str(strict_p))
                            else:
                                # significant:
                                print('STRICT INVARIANT NOT PASSED, chisq p = ' + str(strict_p))
                        else: # not do_strict
                            print('STRICT N/A')
                            strict_p = 'NA'
                    else: # scalar not passed
                        print('SCALAR INVARIANT NOT PASSED, chisq p = ' + str(scalar_p))
                        print('STRICT N/A')
                        strict_p = 'NA'
                else: # not do_scalar
                    print('SCALAR N/A')
                    scalar_p = 'NA'
                    print('STRICT N/A')
                    strict_p = 'NA'
            else: # metric not passed
                print('METRIC INVARIANT NOT PASSED, chisq p = ' + str(metric_p))
                print('SCALAR N/A')
                print('STRICT N/A')
                scalar_p = 'NA'
                strict_p = 'NA'
        else: # not do_metric
            print('METRIC N/A')
            print('SCALAR N/A')
            print('STRICT N/A')
            metric_p = 'NA'
            scalar_p = 'NA'
            strict_p = 'NA'
    else: # config not passed
        print('CONFIG INVARIANT NOT PASSED, chisq p = ' + str(config_p))
        print('METRIC N/A')
        print('SCALAR N/A')
        print('STRICT N/A')
        metric_p = 'NA'
        scalar_p = 'NA'
        strict_p = 'NA'

    return(flag_passed_metric, config_p, metric_p, scalar_p, strict_p)


def run_specific_cfa(whichscale, item_list, whichcfa, datasets, temp_path,
                     num_iter, cpus_to_use, return_vals=False,
                     parameterization="theta", ordered=None):
    """Run the pairwise CFA for a specific formula on each dataset pair.

    datasets : mapping of pair label -> dataframe, e.g.
        {'V_GP': data_val_genpop, 'V_EN': data_val_enriched, 'GP_EN': data_genpop_enriched}
    """
    print(f'\n\nFOR SCALE {whichscale.upper()}:')
    print(f'\nRUN ALL 3-way CFA for items: {item_list}.')

    # down to which scale to test
    doing_metric, doing_scalar, doing_strict = cfa_levels(whichcfa)

    res = []
    flags = []
    for pair, data in datasets.items():
        print(f'\n -----> {pair} <----- ')
        flag_metric, pconfig, pmetric, pscalar, pstrict = cfa_helper_func(
                        scalename=whichscale,
                        list_of_items=item_list,
                        do_metric=doing_metric,
                        do_scalar=doing_scalar,
                        do_strict=doing_strict,
                        mydata_python=data,
                        mydata_temp_path=temp_path,
                        num_iter=num_iter,
                        cpus_to_use=cpus_to_use,
                        parameterization=parameterization,
                        ordered=ordered)
        flags.append(flag_metric)
        row = dict(
            pair=pair,
            pconfig=pconfig,
            pmetric=pmetric,
            pscalar=pscalar,
            pstrict=pstrict
        )
        res.append(row)

    if all(flags):
        print("\n!!! PASSES 3-WAY INVARIANCE")

    print("DONE")
    if return_vals:
        return res
    else:
        return(0)
