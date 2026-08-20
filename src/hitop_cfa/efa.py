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


def dimensionality_effect_sizes(scalename, list_of_items, data_group,
                                temp_path, verbose=True):
    """Effect sizes of a unidimensionality violation for ONE group,
    from the 2-factor geomin EFA (requires >= 5 items and convergence).

    Uses the exact Schmid-Leiman identity for two correlated factors
    (general paths a1 = a2 = sqrt(phi) reproduce Lambda*Phi*Lambda'
    exactly): g_i = sqrt(phi) * (l_i1 + l_i2), s_ik = l_ik * sqrt(1-phi).
    All quantities are on the standardized latent-response scale
    (polychoric metric) -- comparative effect sizes, not raw-score
    reliabilities.

    Returns dict:
        phi, phi_lo, phi_hi : inter-factor correlation (+95% CI from
            lavaan's post-rotation SE)
        ecv       : explained common variance of the general factor
        omega_h   : general-factor share of the (latent) sum's variance
        omega_t   : total common share
        attenuation : sqrt(omega_h) -- multiplier on any criterion
            correlation that runs through the general factor when the
            sum score is used
        n_inflation : 1 / omega_h -- required-sample multiplier vs a
            perfectly unidimensional scale for such correlations
        r_sum_f1, r_sum_f2 : model-implied corr(sum, factor k) -- the
            conflation range of what the sum measures
        converged : False when the 2-factor EFA is unavailable
    """
    items = list(list_of_items)
    if (len(items) - 2) ** 2 < len(items) + 2:
        return dict(converged=False, reason='2-factor EFA not identified')
    set_seeds(12345)
    data_group[items].to_csv(temp_path, index=False)
    ro.r(f'gdat <- read.csv("{temp_path}")')
    ro.r('for (cc in names(gdat)) gdat[[cc]] <- ordered(gdat[[cc]])')
    ro.globalenv['model2'] = ('efa("b1")*f1 + efa("b1")*f2 =~ '
                              + ' + '.join(items))
    ro.r('e2 <- try(lavaan::cfa(model2, data = gdat, ordered = names(gdat), '
         'estimator = "WLSMV", parameterization = "theta", std.lv = TRUE, '
         'rotation = "geomin"), silent = TRUE)')
    ok = bool(ro.r('!inherits(e2, "try-error") && '
                   'lavaan::lavInspect(e2, "converged")')[0])
    if not ok:
        return dict(converged=False, reason='2-factor EFA did not converge')

    lam = _loadings('e2').values  # p x 2, standardized
    with localconverter(ro.default_converter + pandas2ri.converter):
        pe = ro.conversion.rpy2py(ro.r(
            'lavaan::parameterEstimates(e2, standardized = TRUE)'))
    phirow = pe[(pe.op == '~~') & (pe.lhs == 'f1') & (pe.rhs == 'f2')].iloc[0]
    phi = float(phirow['std.all'])
    se = float(phirow['se']) if pd.notna(phirow['se']) else np.nan
    phi_lo, phi_hi = phi - 1.96 * se, phi + 1.96 * se

    aphi = abs(phi)
    # if geomin returns a negative phi, flip factor 2's sign so the
    # general factor is well-defined
    l1, l2 = lam[:, 0], (lam[:, 1] if phi >= 0 else -lam[:, 1])
    g = np.sqrt(aphi) * (l1 + l2)
    s1, s2 = l1 * np.sqrt(1 - aphi), l2 * np.sqrt(1 - aphi)

    ecv = float((g ** 2).sum() / ((g ** 2).sum() + (s1 ** 2).sum()
                                  + (s2 ** 2).sum()))
    # implied latent-response correlation matrix and (unit-weight) sum
    Phi = np.array([[1, aphi], [aphi, 1]])
    L = np.column_stack([l1, l2])
    R = L @ Phi @ L.T
    np.fill_diagonal(R, 1.0)
    var_sum = float(R.sum())
    omega_h = float(g.sum() ** 2 / var_sum)
    omega_t = float((g.sum() ** 2 + s1.sum() ** 2 + s2.sum() ** 2) / var_sum)
    r_sum_f1 = float((l1 + aphi * l2).sum() / np.sqrt(var_sum))
    r_sum_f2 = float((l2 + aphi * l1).sum() / np.sqrt(var_sum))

    out = dict(converged=True, n=len(data_group), phi=phi,
               phi_lo=phi_lo, phi_hi=phi_hi, ecv=ecv,
               omega_h=omega_h, omega_t=omega_t,
               attenuation=float(np.sqrt(omega_h)),
               n_inflation=float(1 / omega_h),
               r_sum_f1=r_sum_f1, r_sum_f2=r_sum_f2)
    if verbose:
        print(f'  phi = {phi:.3f} [{phi_lo:.3f}, {phi_hi:.3f}]  '
              f'ECV = {ecv:.3f}  omegaH = {omega_h:.3f}  '
              f'omegaT = {omega_t:.3f}')
        print(f'  criterion-correlation attenuation = {np.sqrt(omega_h):.3f}'
              f'  required-n inflation = {1/omega_h:.2f}x')
        print(f'  corr(sum, F1) = {r_sum_f1:.3f}, '
              f'corr(sum, F2) = {r_sum_f2:.3f}')
    return out
