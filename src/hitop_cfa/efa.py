"""Per-group exploratory structure diagnostics for configural failures.

When configural invariance fails, the informative question is WHAT differs
structurally between the groups. For each group separately this module
computes: polychoric eigenvalues (scree), the 1-factor WLSMV solution
(fit, standardized loadings, and the largest residual polychoric
correlations -- where the unidimensional misfit concentrates), and, when
identified (>= 5 items), a 2-factor geomin EFA.

Factor-count identification: a k-factor EFA on p ordinal items needs
((p - k)^2 - (p + k)) / 2 >= 0, so 2 factors require p >= 5.
"""
import numpy as np
import pandas as pd

from .r_env import localconverter, pandas2ri, ro, set_seeds


def _fitmeasures(r_name):
    vals = ro.r(f'lavaan::fitMeasures({r_name}, c("chisq.scaled", "df", '
                f'"pvalue.scaled", "cfi.robust", "rmsea.robust"))')
    keys = ('chisq_scaled', 'df', 'pvalue_scaled', 'cfi_robust',
            'rmsea_robust')
    return {k: float(v) for k, v in zip(keys, vals)}


def _loadings(r_name):
    ro.r(f'lmat <- lavaan::inspect({r_name}, "std")$lambda')
    mat = np.asarray(ro.r('lmat'))
    rows = list(ro.r('rownames(lmat)'))
    cols = list(ro.r('colnames(lmat)'))
    return pd.DataFrame(mat, index=rows, columns=cols).round(3)


def polychoric_efa(scalename, list_of_items, data_group, temp_path,
                   max_factors=2, n_residuals=5, verbose=True):
    """Structure diagnostics for ONE group's data on one scale.

    Returns dict with keys: n, eigenvalues, one_factor (fit, loadings,
    worst_residuals), two_factor (fit, loadings; None when < 5 items or
    max_factors < 2), converged flags per solution.
    """
    items = list(list_of_items)
    set_seeds(12345)
    data_group[items].to_csv(temp_path, index=False)
    ro.r(f'gdat <- read.csv("{temp_path}")')
    ro.r('for (cc in names(gdat)) gdat[[cc]] <- ordered(gdat[[cc]])')

    ro.r('pc <- lavaan::lavCor(gdat)')
    eig = np.asarray(ro.r('eigen(pc)$values')).round(3)

    out = dict(n=len(data_group), eigenvalues=eig,
               one_factor=None, two_factor=None)

    ro.globalenv['model1'] = f'{scalename} =~ ' + ' + '.join(items)
    ro.r('f1 <- try(lavaan::cfa(model1, data = gdat, ordered = names(gdat), '
         'estimator = "WLSMV", parameterization = "theta", std.lv = TRUE), '
         'silent = TRUE)')
    ok1 = bool(ro.r('!inherits(f1, "try-error") && '
                    'lavaan::lavInspect(f1, "converged")')[0])
    if ok1:
        ro.r('res <- lavaan::lavResiduals(f1)$cov; '
             'res[upper.tri(res, diag = TRUE)] <- NA')
        k = int(min(n_residuals, len(items) * (len(items) - 1) / 2))
        ro.r(f'ord <- order(abs(res), decreasing = TRUE, na.last = NA)[1:{k}]; '
             'worst <- data.frame(item1 = rownames(res)[row(res)[ord]], '
             'item2 = colnames(res)[col(res)[ord]], '
             'resid = round(res[ord], 3))')
        with localconverter(ro.default_converter + pandas2ri.converter):
            worst = ro.conversion.rpy2py(ro.r('worst'))
        out['one_factor'] = dict(fit=_fitmeasures('f1'),
                                 loadings=_loadings('f1'),
                                 worst_residuals=worst)

    two_ok = max_factors >= 2 and (len(items) - 2) ** 2 >= len(items) + 2
    if two_ok:
        ro.globalenv['model2'] = ('efa("b1")*f1 + efa("b1")*f2 =~ '
                                  + ' + '.join(items))
        ro.r('e2 <- try(lavaan::cfa(model2, data = gdat, '
             'ordered = names(gdat), estimator = "WLSMV", '
             'parameterization = "theta", std.lv = TRUE, '
             'rotation = "geomin"), silent = TRUE)')
        ok2 = bool(ro.r('!inherits(e2, "try-error") && '
                        'lavaan::lavInspect(e2, "converged")')[0])
        if ok2:
            out['two_factor'] = dict(fit=_fitmeasures('e2'),
                                     loadings=_loadings('e2'))

    if verbose:
        print(f'  n = {out["n"]}; polychoric eigenvalues: {eig}')
        if out['one_factor']:
            f = out['one_factor']['fit']
            print(f'  1-factor: chisq {f["chisq_scaled"]:.1f} '
                  f'(df {f["df"]:.0f}, p {f["pvalue_scaled"]:.3f}), '
                  f'CFI {f["cfi_robust"]:.3f}, RMSEA {f["rmsea_robust"]:.3f}')
            print('  loadings:', dict(out['one_factor']['loadings']
                                      .iloc[:, 0]))
            print('  worst residual correlations:')
            print(out['one_factor']['worst_residuals']
                  .to_string(index=False))
        else:
            print('  1-factor model did not converge')
        if out['two_factor']:
            f = out['two_factor']['fit']
            print(f'  2-factor geomin: chisq {f["chisq_scaled"]:.1f} '
                  f'(df {f["df"]:.0f}), CFI {f["cfi_robust"]:.3f}, '
                  f'RMSEA {f["rmsea_robust"]:.3f}')
            print(out['two_factor']['loadings'].to_string())
        elif two_ok:
            print('  2-factor EFA did not converge')
        else:
            print('  2-factor EFA skipped (not identified for '
                  f'{len(items)} items)')
    return out


def configural_efa_report(scalename, list_of_items, data_pair, temp_path,
                          group_col='whichdata', max_factors=2,
                          n_residuals=5, verbose=True):
    """Run polychoric_efa for each group in a 2-group pair dataframe
    (groups in order of appearance). Returns {group_label: result}."""
    results = {}
    for label in pd.unique(data_pair[group_col]):
        if verbose:
            print(f'----- {scalename} | group: {label} -----')
        results[label] = polychoric_efa(
            scalename, list_of_items,
            data_pair[data_pair[group_col] == label], temp_path,
            max_factors=max_factors, n_residuals=n_residuals,
            verbose=verbose)
    return results
