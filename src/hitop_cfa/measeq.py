# =============================================================================
# Wu & Estabrook (2016) invariance models for ordinal indicators, generated
# via semTools::measEq.syntax.
#
# Why this module exists: lavaan's continuous-tradition ``group.equal``
# shortcuts do not produce testable scalar/strict models for ordinal
# indicators. With ordered items, intercepts are fixed to 0 in all groups,
# so ``group.equal = "intercepts"`` constrains nothing (and, per lavaan's
# convention, frees the non-reference latent means: df goes DOWN by 1).
# ``group.equal = "residuals"`` then constrains residual variances that were
# already fixed to 1 in all groups under theta: df change 0, delta-chisq
# identically 0, permutation p = 1. Empirically verified on this project's
# data (see check_invariance_dfs.py).
#
# IDENTIFICATION: ID.fac = "std.lv" (fixed factor variance), NOT marker.
# Marker identification is underidentified for categorical-only factors
# under Wu-Estabrook (latent means freed with nothing to identify them);
# empirically confirmed on this project's data (uniform +2 npar / -2 df at
# configural, non-positive-definite vcov, explicit semTools warning).
# Under std.lv, the measEq configural model is statistically equivalent to
# the plain cfa() configural (same df and npar; loadings all free, factor
# variance fixed instead of marker fixed).
#
# measEq.syntax with ID.cat = "Wu.Estabrook.2016" generates models where
# each level's constraints are real: when thresholds are constrained equal,
# the latent-response intercepts and (under theta) unique variances become
# identified in non-reference groups and are freed, so subsequent levels
# (loadings, intercepts, residuals) constrain genuinely free parameters.
#
# Level sequence for ordinal indicators (Wu & Estabrook 2016):
#   configural -> thresholds -> metric -> scalar -> strict
# where metric = thresholds + loadings, scalar = + intercepts,
# strict = + residuals. "thresholds" is the ordinal analog of the location
# (scalar) constraint in the continuous tradition; the manuscript should
# describe the mapping explicitly and cite Wu & Estabrook (2016).
#
# Reference: Wu, H., & Estabrook, R. (2016). Identification of confirmatory
# factor analysis models of different levels of invariance for ordered
# categorical outcomes. Psychometrika, 81(4), 1014-1045.
# =============================================================================
from .r_env import localconverter, pandas2ri, ro

# Cumulative group.equal sets per level, in testing order.
# Each level is nested in the previous one (same identification scheme,
# strictly more constraints), so delta-chisq comparisons are valid.
WU_ESTABROOK_LEVELS = [
    ('configural', None),
    ('thresholds', ('thresholds',)),
    ('metric',     ('thresholds', 'loadings')),
    ('scalar',     ('thresholds', 'loadings', 'intercepts')),
    ('strict',     ('thresholds', 'loadings', 'intercepts', 'residuals')),
]

# What is NEW at each level relative to the previous -- passed to
# permuteMeasEq's ``param`` argument so the max-MI distribution is computed
# over the constraints the level actually added. None means the level's
# delta test runs as the param-free OMNIBUS permutation: at scalar/strict
# the Wu-Estabrook models impose invariance by FIXING parameters back
# (group-2 intercepts to 0, group-2 residual variances to 1) rather than by
# "==" equality constraints, so there is nothing for permuteMeasEq's MI
# machinery to test (its MI table is empty and semTools' summary() errors).
# Per-item intercept MIs for the scalar level come from lavaan::modindices
# on the scalar fit instead (see stepwise_scalar.extract_item_mis_from_scalar).
LEVEL_NEW_PARAMS = {
    'thresholds': ('thresholds',),
    'metric':     ('loadings',),
    'scalar':     None,
    'strict':     None,
}


def build_measeq_model(ordered, group_equal=None, parameterization="theta",
                       id_fac="std.lv", r_syntax_name="measeq_mod_str"):
    """Generate lavaan model syntax for one invariance level via
    semTools::measEq.syntax with Wu & Estabrook (2016) identification.

    Expects the same R globals that ``fit.push_model_to_r`` sets:
    ``testformula_r`` (configural model string), ``rdata`` (data.frame),
    ``group`` (grouping column name).

    ``r_syntax_name`` is the R global the generated syntax is stored in.
    IT MUST BE UNIQUE PER LEVEL when the fitted models go to permuteMeasEq:
    permuteMeasEq refits con/uncon on each permuted dataset via
    lavaan::update(), which re-evaluates the fit's original call, so the
    model-string SYMBOL in that call is resolved again at update time. If
    two levels share one symbol, both refits resolve to whichever model was
    built last -> identical models -> every permuted delta-chisq is exactly
    0 -> permutation p = 0 for any positive observed delta (verified on
    this project's data during the task-6 smoke test; the parametric
    delta tests on the same fits were sane).

    Parameters
    ----------
    ordered : iterable of str
        Item names to declare ordered (pass the item list; ``TRUE`` is not
        supported here because measEq.syntax wants explicit names).
    group_equal : tuple/list of str or None
        Cumulative constraint set for this level (see WU_ESTABROOK_LEVELS).
        None -> configural.
    id_fac : str
        Factor identification. MUST be "std.lv" for these data: with
        factors measured only by categorical indicators, marker
        identification ("auto.fix.first") under Wu-Estabrook leaves the
        freed latent means unidentified (semTools warns explicitly; lavaan
        vcov is numerically singular -- verified on this project's data,
        see diff_configural_identification.py output in the handoff doc).
        Under std.lv there is NO marker item: the factor is identified by
        fixing its variance to 1 in the reference group (freed in other
        groups once loadings are constrained). Consequence for the
        stepwise modules: no item is excluded from MI candidacy or
        ablation (pass excluded_item=None to find_worst_item).

    Returns
    -------
    str : lavaan model syntax (store in an R global and pass to cfa()).
    """
    ordered_str = 'c(' + ', '.join(f'"{i}"' for i in ordered) + ')'
    if group_equal:
        ge_str = ('group.equal = c(' +
                  ', '.join(f'"{g}"' for g in group_equal) + '), ')
    else:
        ge_str = ''
    ro.r(f'''
        measeq_mod <- semTools::measEq.syntax(
            configural.model = testformula_r,
            data = rdata,
            group = group,
            ordered = {ordered_str},
            parameterization = "{parameterization}",
            estimator = "WLSMV",
            ID.fac = "{id_fac}",
            ID.cat = "Wu.Estabrook.2016",
            {ge_str}return.fit = FALSE)
        {r_syntax_name} <- as.character(measeq_mod)
    ''')
    return ro.r(r_syntax_name)[0]


def fit_measeq_level(ordered, group_equal=None, parameterization="theta",
                     id_fac="std.lv", r_fit_name="fit_tmp"):
    """Build the measEq.syntax model for one level and fit it with lavaan.

    The fitted object is stored in the R global ``r_fit_name`` (so callers
    can hand it to permuteMeasEq) and also returned. The model syntax is
    stored under the fit-specific global ``{r_fit_name}_mod_str`` -- this
    per-fit name is LOAD-BEARING for permuteMeasEq (see build_measeq_model:
    a shared syntax symbol makes update()-based permutation refits of
    con and uncon identical, degenerating the permutation null to all
    zeros). Callers must therefore give each level its own r_fit_name.
    """
    r_syntax_name = f'{r_fit_name}_mod_str'
    build_measeq_model(ordered, group_equal, parameterization, id_fac,
                       r_syntax_name=r_syntax_name)
    ordered_str = 'c(' + ', '.join(f'"{i}"' for i in ordered) + ')'
    fit = ro.r(
        f'{r_fit_name} <- lavaan::cfa({r_syntax_name}, data = rdata, '
        f'group = group, ordered = {ordered_str}, '
        f'parameterization = "{parameterization}", estimator = "WLSMV")')
    return fit


def extract_item_mis_from_thresholds(item_list, r_out_name="out_thresholds"):
    """Per-item MIs for threshold equality constraints from a permuteMeasEq
    object (the ordinal analog of the old intercept-MI extractor).

    Threshold parameters look like "hitop39|t1", "hitop39|t2", ... in the
    parameter table (op == "|"). Each item contributes multiple thresholds;
    aggregate to one MI per item by taking the max over that item's
    threshold constraints (consistent with the loading extractor's
    max-over-groups aggregation).

    Returns dict[item -> max MI] or None.
    """
    try:
        ro.r(f'''
            mi_obs <- {r_out_name}@MI.obs
            pt     <- {r_out_name}@PT
            mi_obs$par_name <- pt$par[ match(mi_obs$lhs, pt$plabel) ]
            mi_thr <- mi_obs[grepl("\\\\|", mi_obs$par_name), ]
            if (nrow(mi_thr) > 0) {{
                mi_thr$item <- sub("\\\\|.*$", "", mi_thr$par_name)
            }}
        ''')
        mi_df_r = ro.r('mi_thr')
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
        print(f"  [WARN] Could not extract threshold MIs: {e}")
        return None


def assert_level_adds_df(fit_lower_name, fit_higher_name, lower_label,
                         higher_label):
    """Guard against silently vacuous comparisons: raise if the more
    constrained model does not add degrees of freedom over the less
    constrained one. Cheap insurance -- call before every permuteMeasEq
    delta test.
    """
    df_lo = float(ro.r(f'lavaan::fitMeasures({fit_lower_name}, "df")')[0])
    df_hi = float(ro.r(f'lavaan::fitMeasures({fit_higher_name}, "df")')[0])
    if df_hi <= df_lo:
        raise RuntimeError(
            f"Vacuous invariance comparison: df({higher_label}) = {df_hi:.0f} "
            f"<= df({lower_label}) = {df_lo:.0f}. The higher level adds no "
            f"testable constraints; check the model syntax "
            f"(this is the failure mode that produced permutation p = 1.0).")
    return df_hi - df_lo
