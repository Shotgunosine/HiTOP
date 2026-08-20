"""Effect sizes of measurement non-invariance, with uncertainty.

Quantifies how much a scale's non-invariance distorts observed scores
between two groups, from the Wu-Estabrook METRIC model (common loadings
and thresholds; group-2 item intercepts free). Everything is a function
of that single fit, so confidence intervals are coherent:

- alpha  : the uniform severity shift -- the precision-weighted (GLS)
           projection of the free group-2 intercepts nu on the loadings
           lambda, using the robust vcov block of nu as weights. This is
           what a fully invariant instrument would report as the latent
           mean difference (numerically close to the scalar-model MLE).
- d_i    : nu_i - lambda_i * alpha, the item's intercept shift BEYOND
           the severity difference (non-uniform DIF).
- curves : expected item score E[Y|t] = sum_k Phi(lambda*t + d_i - tau_k)
           (theta parameterization) vs the invariance-implied d_i = 0,
           integrated over the group-2 latent distribution N(alpha, psi2):
           signed item bias, dMACS (Nye & Drasgow 2011; RMS curve
           difference / pooled observed item SD), and the net sum-score
           measurement bias.
- CIs    : free parameters are simulated from N(theta_hat, V_robust)
           (lavaan's vcov for the WLSMV fit) and every quantity is
           recomputed per draw; intervals are percentile-based.

Caveat: when configural invariance already fails, the metric model is an
approximation and these are order-of-magnitude quantifications.
"""
import numpy as np
import pandas as pd
from scipy import stats

from .r_env import localconverter, pandas2ri, ro, set_seeds
from .fit import push_model_to_r
from .measeq import WU_ESTABROOK_LEVELS, fit_is_converged, fit_measeq_level

_GE = dict(WU_ESTABROOK_LEVELS)


def dif_effect_sizes(scalename, list_of_items, data_pair, temp_path,
                     parameterization="theta", n_draws=1000, seed=12345,
                     grid_points=401, ci=95.0):
    """Compute non-invariance effect sizes for one scale on one 2-group
    dataset (``data_pair`` must contain both groups and the 'whichdata'
    column; group 1 = first group encountered, the reference).

    Returns (per_item : pd.DataFrame, summary : dict). per_item columns:
    item, lambda, nu2, d (+ d_lo/d_hi), signed_bias (+ CI), dMACS (+ CI).
    summary keys: group_labels, alpha (+ CI), psi2, real_gap_points
    (+ CI), net_sum_bias_points (+ CI), gross_abs_bias_points,
    scale_max_points, converged, ci_ok.
    """
    set_seeds(seed)
    push_model_to_r(scalename, list(list_of_items), data_pair, temp_path)
    fit_measeq_level(list(list_of_items), _GE['metric'],
                     parameterization=parameterization,
                     r_fit_name='fit_metric_es')
    if not fit_is_converged('fit_metric_es'):
        return None, dict(converged=False)
    group_labels = list(ro.r('lavaan::lavInspect(fit_metric_es, "group.label")'))
    with localconverter(ro.default_converter + pandas2ri.converter):
        pt = ro.conversion.rpy2py(ro.r('lavaan::parameterTable(fit_metric_es)'))
        V = np.asarray(ro.r('lavaan::lavInspect(fit_metric_es, "vcov")'))
    theta = np.asarray(ro.r('lavaan::coef(fit_metric_es)'))

    items = list(list_of_items)

    def free_idx(rows):
        # lavaan 'free' is 1-based into coef()/vcov(); equality-constrained
        # parameters share one index
        fr = rows.free.values
        assert (fr > 0).all(), 'expected free parameters'
        return (fr - 1).astype(int)

    lam_ix = {i: int(free_idx(pt[(pt.op == '=~') & (pt.rhs == i)
                                 & (pt.group == 1)])[0]) for i in items}
    thr_ix = {i: free_idx(pt[(pt.op == '|') & (pt.lhs == i)
                             & (pt.group == 1)].sort_values('rhs'))
              for i in items}
    nu_ix = {i: int(free_idx(pt[(pt.op == '~1') & (pt.lhs == i)
                                & (pt.group == 2)])[0]) for i in items}
    psi_rows = pt[(pt.op == '~~') & (pt.lhs == scalename)
                  & (pt.rhs == scalename) & (pt.group == 2)]
    psi_ix = int(free_idx(psi_rows)[0])

    nu_indices = np.array([nu_ix[i] for i in items])
    W = V[np.ix_(nu_indices, nu_indices)]
    try:
        Winv = np.linalg.inv(W)
    except np.linalg.LinAlgError:
        Winv = np.linalg.pinv(W)

    pooled_sd = {i: float(data_pair[i].std()) for i in items}
    n_cats = {i: len(thr_ix[i]) + 1 for i in items}
    scale_max = float(sum(n_cats[i] - 1 for i in items))

    def compute(vec):
        lam = np.array([vec[lam_ix[i]] for i in items])
        nu = np.array([vec[nu_ix[i]] for i in items])
        psi2 = max(float(vec[psi_ix]), 1e-4)
        alpha = float(lam @ Winv @ nu) / float(lam @ Winv @ lam)
        d = nu - lam * alpha
        sd2 = np.sqrt(psi2)
        t = np.linspace(min(-4.0, alpha - 4 * sd2),
                        max(4.0, alpha + 4 * sd2), grid_points)
        w2 = stats.norm.pdf(t, loc=alpha, scale=sd2); w2 = w2 / w2.sum()
        w1 = stats.norm.pdf(t); w1 = w1 / w1.sum()
        signed = np.empty(len(items)); dmacs = np.empty(len(items))
        e_inv_sum = np.zeros_like(t)
        for j, item in enumerate(items):
            taus = np.array([vec[k] for k in thr_ix[item]])
            e_dif = stats.norm.cdf(lam[j] * t[:, None] + d[j]
                                   - taus[None, :]).sum(axis=1)
            e_inv = stats.norm.cdf(lam[j] * t[:, None]
                                   - taus[None, :]).sum(axis=1)
            e_inv_sum += e_inv
            diff = e_dif - e_inv
            signed[j] = float(diff @ w2)
            dmacs[j] = float(np.sqrt((diff ** 2) @ w2) / pooled_sd[item])
        real_gap = float(e_inv_sum @ w2 - e_inv_sum @ w1)
        return dict(alpha=alpha, psi2=psi2, d=d, signed=signed,
                    dmacs=dmacs, net=float(signed.sum()),
                    gross=float(np.abs(signed).sum()), real_gap=real_gap)

    point = compute(theta)

    ci_ok = True
    try:
        rng = np.random.default_rng(seed)
        try:
            draws = rng.multivariate_normal(theta, V, size=n_draws,
                                            method='cholesky')
        except np.linalg.LinAlgError:
            evals, evecs = np.linalg.eigh((V + V.T) / 2)
            evals = np.clip(evals, 0, None)
            draws = (rng.standard_normal((n_draws, len(theta)))
                     * np.sqrt(evals)) @ evecs.T + theta
        sims = [compute(v) for v in draws]
    except Exception:
        ci_ok = False
        sims = []

    lo, hi = (100 - ci) / 2, 100 - (100 - ci) / 2

    def pct(key, j=None):
        if not ci_ok:
            return (np.nan, np.nan)
        vals = np.array([s[key] if j is None else s[key][j] for s in sims])
        return (float(np.percentile(vals, lo)), float(np.percentile(vals, hi)))

    rows = []
    for j, item in enumerate(items):
        d_lo, d_hi = pct('d', j)
        s_lo, s_hi = pct('signed', j)
        m_lo, m_hi = pct('dmacs', j)
        rows.append(dict(item=item, lam=float(theta[lam_ix[item]]),
                         nu2=float(theta[nu_ix[item]]),
                         d=float(point['d'][j]), d_lo=d_lo, d_hi=d_hi,
                         signed_bias=float(point['signed'][j]),
                         signed_lo=s_lo, signed_hi=s_hi,
                         dMACS=float(point['dmacs'][j]),
                         dMACS_lo=m_lo, dMACS_hi=m_hi))
    per_item = pd.DataFrame(rows)

    summary = dict(group_labels=group_labels, converged=True, ci_ok=ci_ok,
                   alpha=point['alpha'], alpha_ci=pct('alpha'),
                   psi2=point['psi2'],
                   real_gap_points=point['real_gap'],
                   real_gap_ci=pct('real_gap'),
                   net_sum_bias_points=point['net'], net_ci=pct('net'),
                   gross_abs_bias_points=point['gross'],
                   gross_ci=pct('gross'),
                   scale_max_points=scale_max, n_draws=n_draws)
    return per_item, summary
