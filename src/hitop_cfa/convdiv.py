"""Preregistered convergent (C1-C7) and divergent (D1-D5) validity tests.

Faithful extraction of the analysis code embedded in
notebooks/NB_4_convdiv.ipynb so other notebooks (NB_core_effects) can run
the identical tests against different invariant-core sets. Function bodies
match the NB_4 cells; the only changes are parameterization (a cores frame,
column lists, and an rng are passed in instead of read from notebook
globals). Statistical behavior -- Spearman via pingouin, logistic GLM for
C7, mutual_info_classif with the fixed random_state, sample_type-stratified
permutations, frac=.8 no-replacement bootstraps -- is unchanged.
"""
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.feature_selection import mutual_info_classif
import pingouin as pg
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Substantive domain groupings (theory, not analysis outcomes): which HiTOP
# scales count as depression vs anxiety. well_being is in neither and is
# excluded from the HiTOP sum per the prereg.
DEP_SCALES = ['anhedonic_depression', 'appetite_gain', 'appetite_loss',
              'cognitive_problems', 'hyposomnia', 'indecisiveness',
              'insomnia', 'shame_guilt']
ANX_SCALES = ['anxious_worry', 'panic', 'separation_insecurity',
              'situational_phobia', 'social_anxiety']
HITOP_SUM_SCALES = DEP_SCALES + ANX_SCALES          # excludes well_being
ALL_HITOP_SCALES = HITOP_SUM_SCALES + ['well_being']


def resolve_core_col(scale, core_names, core_level_by_name):
    """Column holding this scale's core sum score, plus how it was resolved.

    Priority: confirmatory stepwise core > full-scale confirmatory core >
    exhaustive alternate > full scale with no invariant core (prereg:
    enriched-sample-only hypotheses for these)."""
    invcore = f'hitop_{scale}__invcore'
    ex_invcore = f'hitop_{scale}__ex_invcore'
    if invcore in core_names:
        return invcore, 'confirmatory_reduced', core_level_by_name[invcore]
    if scale in core_names:  # full-scale core rows keep the bare scale name
        return f'hitop_{scale}', 'confirmatory_full_scale', core_level_by_name[scale]
    if ex_invcore in core_names:
        return ex_invcore, 'exhaustive_alternate', core_level_by_name[ex_invcore]
    return f'hitop_{scale}', 'no_invariant_core', None


def resolve_cores(cores, scales=ALL_HITOP_SCALES):
    """Resolution table mapping every scale to its core sum-score column.

    `cores` follows the cores.pkl convention: reduced cores carry scale
    names like 'hitop_{scale}__invcore', full-scale cores the bare scale
    name; columns scale / core_level / item_nos / reduced.
    Returns (core_resolution dict, core_resolution_df)."""
    core_names = set(cores.scale)
    core_level_by_name = dict(zip(cores.scale, cores.core_level))
    core_resolution = {}
    for scale in scales:
        col, how, level = resolve_core_col(scale, core_names,
                                           core_level_by_name)
        core_resolution[scale] = dict(column=col, resolution=how,
                                      core_level=level)
    core_resolution_df = pd.DataFrame(core_resolution).T
    no_core = core_resolution_df.index[
        core_resolution_df.resolution == 'no_invariant_core'].tolist()
    if no_core:
        print(f"\nWARNING: no invariant core for {no_core} -- the full scale "
              f"is used; per the prereg, hypotheses involving these scales "
              f"should be tested in the enriched sample only.")
    return core_resolution, core_resolution_df


def add_core_sum_columns(data_frames, cores):
    """Sum scores for the REDUCED cores (full-scale cores keep the bare
    hitop_{scale} columns that already exist in the data)."""
    for data in data_frames:
        for row in cores.loc[cores.reduced, :].itertuples():
            tmp_items = list(row.item_nos)
            data[row.scale] = data.loc[:, tmp_items].sum(axis=1)
            tmp_recontact = [f'{ti}_recontact' for ti in tmp_items]
            if all(c in data.columns for c in tmp_recontact):
                data[f'{row.scale}_recontact'] = (
                    data.loc[:, tmp_recontact].sum(axis=1))


def add_core_aliases(data_frames, core_resolution):
    """Canonical alias columns: all hypothesis code uses hitop_{scale}__core."""
    for data in data_frames:
        for scale, info in core_resolution.items():
            data[f'hitop_{scale}__core'] = data[info['column']]


def do_correlation(col1, col2):
    corr_result = pg.corr(col1, col2, method='spearman')
    my_r = corr_result.iloc[0]['r']
    my_r = "{:.2f}".format(float(my_r))
    my_ci = corr_result.iloc[0]['CI95']
    my_ci_1 = my_ci[0]
    my_ci_2 = my_ci[1]
    my_p = corr_result.iloc[0]['p_val']
    my_p = "{:.3f}".format(float(my_p))
    return (my_p, my_r, my_ci_1, my_ci_2)


def check_convergent_hypotheses(mydata, hitop_sum_cols):
    '''
    tests convergent hypotheses; for hitop scales we use inv cores when
    appropriate (mydata must carry the hitop_{scale}__core alias columns)

    Returns
    -------
    pd.DataFrame
        One row per test with columns:
        hypothesis, test_type, variables, statistic, p_value,
        ci_lower, ci_upper, significant, supported
    '''
    results = []  # collect one dict per test

    def record_correlation(hypothesis, var1_name, var2_name, p, r, ci1, ci2,
                           expected_direction):
        '''Helper: store a correlation test result and determine support.'''
        significant = float(p) < 0.05
        if not significant:
            supported = False
        elif expected_direction == 'positive':
            supported = float(r) > 0
        elif expected_direction == 'negative':
            supported = float(r) < 0
        else:  # any direction
            supported = True
        results.append({
            'hypothesis': hypothesis,
            'test_type': 'spearman_correlation',
            'variables': f'{var1_name} ~ {var2_name}',
            'statistic': float(r),
            'p_value': float(p),
            'ci_lower': float(ci1),
            'ci_upper': float(ci2),
            'significant': significant,
            'supported': supported,
        })
        return significant, supported

    print('\n --- CONV ANALYSIS START --- \n')

    print('\n-----> HYPOTHESIS C1 <-----\n')
    (p, r, ci1, ci2) = do_correlation(mydata.hitop_anhedonic_depression__core,
                                      mydata.phq_sum)
    sig, sup = record_correlation('C1', 'hitop_anhedonic_depression__core',
                                  'phq_sum', p, r, ci1, ci2,
                                  expected_direction='positive')
    print(f"p-val = {p} and r = {r}({ci1}, {ci2}); "
          f"significant={sig}, supported={sup}")

    print('\n-----> HYPOTHESIS C2 <-----\n')
    (p, r, ci1, ci2) = do_correlation(mydata.hitop_well_being__core,
                                      mydata.phq_sum)
    sig, sup = record_correlation('C2', 'hitop_well_being__core', 'phq_sum',
                                  p, r, ci1, ci2,
                                  expected_direction='negative')
    print(f"p-val = {p} and r = {r}({ci1}, {ci2}); "
          f"significant={sig}, supported={sup}")

    print('\n-----> HYPOTHESIS C3 <-----\n')
    (p, r, ci1, ci2) = do_correlation(mydata.hitop_anxious_worry__core,
                                      mydata.gad_sum)
    sig, sup = record_correlation('C3', 'hitop_anxious_worry__core',
                                  'gad_sum', p, r, ci1, ci2,
                                  expected_direction='positive')
    print(f"p-val = {p} and r = {r}({ci1}, {ci2}); "
          f"significant={sig}, supported={sup}")

    print('\n-----> HYPOTHESIS C4 <-----\n')
    mydata['hitop_appetite_sum'] = (mydata['hitop_appetite_gain__core']
                                    + mydata['hitop_appetite_loss__core'])
    (p, r, ci1, ci2) = do_correlation(mydata.hitop_appetite_sum, mydata.phq_5)
    sig, sup = record_correlation('C4', 'hitop_appetite_sum', 'phq_5',
                                  p, r, ci1, ci2,
                                  expected_direction='positive')
    print(f"p-val = {p} and r = {r}({ci1}, {ci2}); "
          f"significant={sig}, supported={sup}")

    print('\n-----> HYPOTHESIS C5 <-----\n')
    (p, r, ci1, ci2) = do_correlation(mydata.hitop_cognitive_problems__core,
                                      mydata.phq_7)
    sig, sup = record_correlation('C5', 'hitop_cognitive_problems__core',
                                  'phq_7', p, r, ci1, ci2,
                                  expected_direction='positive')
    print(f"p-val = {p} and r = {r}({ci1}, {ci2}); "
          f"significant={sig}, supported={sup}")

    print('\n-----> HYPOTHESIS C6 <-----\n')
    (p, r, ci1, ci2) = do_correlation(mydata.hitop_insomnia__core,
                                      mydata.phq_3)
    sig, sup = record_correlation('C6', 'hitop_insomnia__core', 'phq_3',
                                  p, r, ci1, ci2,
                                  expected_direction='positive')
    print(f"p-val = {p} and r = {r}({ci1}, {ci2}); "
          f"significant={sig}, supported={sup}")

    print('\n-----> HYPOTHESIS C7 <-----\n')
    mydata['hitop_sum_new'] = mydata.loc[:, hitop_sum_cols].sum(axis=1)
    mydata['moodanxiety_bothered_int'] = (
        mydata.moodanxiety_bothered.astype(int))
    formula = 'moodanxiety_bothered_int ~ hitop_sum_new'
    model = smf.glm(formula=formula, data=mydata,
                    family=sm.families.Binomial())
    result = model.fit()
    print(result.summary())
    coef = result.params.iloc[1]
    z_stat = result.tvalues.iloc[1]
    p_val_hitop_sum_float = result.pvalues.iloc[1]
    conf_int = result.conf_int()
    significant_c7 = p_val_hitop_sum_float < 0.05
    results.append({
        'hypothesis': 'C7',
        'test_type': 'logistic_regression',
        'variables': formula,
        'statistic': float(z_stat),  # z-statistic for hitop_sum_new coef
        'p_value': float(p_val_hitop_sum_float),
        'ci_lower': float(conf_int.iloc[1, 0]),  # CI on the coefficient
        'ci_upper': float(conf_int.iloc[1, 1]),
        'significant': significant_c7,
        'supported': significant_c7 and coef > 0,
    })
    print(f"C7 p-val = {p_val_hitop_sum_float:.6f}; "
          f"significant={significant_c7}")

    print('some exploratory C7 tests')
    for sample_label, sample_query in [
            ('C7_exploratory_sample1', 'sample_type==1'),
            ('C7_exploratory_sample2', 'sample_type==2')]:
        model = smf.glm(formula=formula, data=mydata.query(sample_query),
                        family=sm.families.Binomial())
        result = model.fit()
        print(result.summary())
        conf_int = result.conf_int()
        results.append({
            'hypothesis': sample_label,
            'test_type': 'logistic_regression',
            'variables': f'{formula} [{sample_query}]',
            'statistic': float(result.tvalues.iloc[1]),
            'p_value': float(result.pvalues.iloc[1]),
            'ci_lower': float(conf_int.iloc[1, 0]),
            'ci_upper': float(conf_int.iloc[1, 1]),
            'significant': result.pvalues.iloc[1] < 0.05,
            'supported': (result.pvalues.iloc[1] < 0.05
                          and result.params.iloc[1] > 0),
        })

    print('\n --- CONV ANALYSIS DONE ---')
    return pd.DataFrame(results)


def calc_dhs(df, pid=0, random_state=2342393490, cols_to_z=None):
    if cols_to_z is None:
        cols_to_z = [
            'gad_phq_sum',
            'hitop_sum_invcores',
            'baars_sum',
            'baars_sum_d3',
            'hitop_all_depression__core',
            'hitop_all_anxiety__core'
        ]
    df = df.copy()
    for cc in cols_to_z:
        df[cc] = (df[cc] - df[cc].mean()) / df[cc].std()
    # -------------------------------------------------------------------
    # D1: stronger correlation of HiTOP sum with GAD-7+PHQ-8 than BAARS-IV
    gad_phq_v_hitop = stats.spearmanr(df.gad_phq_sum,
                                      df.hitop_sum_invcores)[0]
    baars_v_hitop = stats.spearmanr(df.baars_sum, df.hitop_sum_invcores)[0]
    d1 = gad_phq_v_hitop - baars_v_hitop
    # -------------------------------------------------------------------
    # D2: HiTOP sum better predicts moodanxiety_bothered than
    # attention_bothered
    hitop_v_mab = mutual_info_classif(
        df.hitop_sum_invcores.values.reshape((-1, 1)),
        df.moodanxiety_bothered.values, random_state=random_state)[0]
    hitop_v_ab = mutual_info_classif(
        df.hitop_sum_invcores.values.reshape((-1, 1)),
        df.attention_bothered.values, random_state=random_state)[0]
    d2 = hitop_v_mab - hitop_v_ab
    # -------------------------------------------------------------------
    # D3: BAARS-IV total better predicts attention_bothered than
    # moodanxiety_bothered
    baars_v_ab = mutual_info_classif(
        df.baars_sum_d3.values.reshape((-1, 1)),
        df.attention_bothered.values, random_state=random_state)[0]
    baars_v_mab = mutual_info_classif(
        df.baars_sum_d3.values.reshape((-1, 1)),
        df.moodanxiety_bothered.values, random_state=random_state)[0]
    d3 = baars_v_ab - baars_v_mab
    # -------------------------------------------------------------------
    # D4: HiTOP mood-scale sum better predicts mood_bothered than
    # anxiety_bothered
    hitopdep_v_mb = mutual_info_classif(
        df.hitop_all_depression__core.values.reshape((-1, 1)),
        df.mood_bothered.values, random_state=random_state)[0]
    hitopdep_v_ab = mutual_info_classif(
        df.hitop_all_depression__core.values.reshape((-1, 1)),
        df.anxiety_bothered.values, random_state=random_state)[0]
    d4 = hitopdep_v_mb - hitopdep_v_ab
    # exploratory 4, just use the anhedonic depression core
    hitopanhdep_v_mb = mutual_info_classif(
        df.hitop_anhedonic_depression__core.values.reshape((-1, 1)),
        df.mood_bothered.values, random_state=random_state)[0]
    hitopanhdep_v_ab = mutual_info_classif(
        df.hitop_anhedonic_depression__core.values.reshape((-1, 1)),
        df.anxiety_bothered.values, random_state=random_state)[0]
    exd4 = hitopanhdep_v_mb - hitopanhdep_v_ab
    # -------------------------------------------------------------------
    # D5: HiTOP anxiety-scale sum better predicts anxiety_bothered than
    # mood_bothered
    hitopanx_v_ab = mutual_info_classif(
        df.hitop_all_anxiety__core.values.reshape((-1, 1)),
        df.anxiety_bothered.values, random_state=random_state)[0]
    hitopanx_v_mb = mutual_info_classif(
        df.hitop_all_anxiety__core.values.reshape((-1, 1)),
        df.mood_bothered.values, random_state=random_state)[0]
    d5 = hitopanx_v_ab - hitopanx_v_mb
    # exploratory 5, just use the anxious worry core
    hitopanxwor_v_ab = mutual_info_classif(
        df.hitop_anxious_worry__core.values.reshape((-1, 1)),
        df.anxiety_bothered.values, random_state=random_state)[0]
    hitopanxwor_v_mb = mutual_info_classif(
        df.hitop_anxious_worry__core.values.reshape((-1, 1)),
        df.mood_bothered.values, random_state=random_state)[0]
    exd5 = hitopanxwor_v_ab - hitopanxwor_v_mb

    return dict(
        pid=pid,
        gad_phq_v_hitop=gad_phq_v_hitop,
        baars_v_hitop=baars_v_hitop,
        d1=d1,
        hitop_v_mab=hitop_v_mab,
        hitop_v_ab=hitop_v_ab,
        d2=d2,
        baars_v_ab=baars_v_ab,
        baars_v_mab=baars_v_mab,
        d3=d3,
        hitopdep_v_mb=hitopdep_v_mb,
        hitopdep_v_ab=hitopdep_v_ab,
        d4=d4,
        hitopanx_v_ab=hitopanx_v_ab,
        hitopanx_v_mb=hitopanx_v_mb,
        d5=d5,
        hitopanhdep_v_mb=hitopanhdep_v_mb,
        hitopanhdep_v_ab=hitopanhdep_v_ab,
        exd4=exd4,
        hitopanxwor_v_ab=hitopanxwor_v_ab,
        hitopanxwor_v_mb=hitopanxwor_v_mb,
        exd5=exd5
    )


DH_NAMES = ['d1', 'd2', 'd3', 'd4', 'd5', 'exd4', 'exd5']

COLS_FOR_D = [
    'gad_phq_sum',
    'hitop_sum_invcores',
    'baars_sum',
    'baars_sum_d3',
    'moodanxiety_bothered',
    'mood_bothered',
    'anxiety_bothered',
    'attention_bothered',
    'hitop_all_depression__core',
    'hitop_all_anxiety__core',
    'hitop_anhedonic_depression__core',
    'hitop_anxious_worry__core'
]
PERMED_COLS = [
    'gad_phq_sum',
    'baars_sum',
    'moodanxiety_bothered',
    'attention_bothered',
    'mood_bothered',
    'anxiety_bothered'
]


def prepare_divergent_data(data_combined, hitop_sum_cols, dep_scales,
                           anx_scales):
    """Derived sums NB_4 builds before the divergent tests (mydata cell)."""
    mydata = data_combined.reset_index(drop=True)
    mydata['gad_phq_sum'] = mydata['gad_sum'] + mydata['phq_sum']
    mydata['hitop_sum_invcores'] = mydata.loc[:, hitop_sum_cols].sum(axis=1)
    mydata['hitop_all_depression__core'] = (
        mydata.loc[:, dep_scales].sum(axis=1))
    mydata['hitop_all_anxiety__core'] = mydata.loc[:, anx_scales].sum(axis=1)
    # doubling baars_sum because it needs to be permuted for d1, but not d3
    mydata['baars_sum_d3'] = mydata.baars_sum.copy()
    return mydata


def run_divergent(mydata, rng, nperms=1000, nboots=1000):
    """Observed D statistics + stratified permutation p's + bootstrap CIs.

    Returns (perm_res, bootdf, pvals) where perm_res row 0 (pid=-1) is the
    observed statistics and pvals maps d1..exd5 to one-sided permutation
    p-values, exactly as in NB_4."""
    nonpermed_cols = [cc for cc in COLS_FOR_D if cc not in PERMED_COLS]
    ogddat = mydata.loc[:, ['caseid', 'sample_type'] + COLS_FOR_D].copy()
    ddat = mydata.loc[:, ['caseid', 'sample_type'] + COLS_FOR_D].copy()
    ddat['pid'] = -1

    perm_res = [calc_dhs(ogddat, pid=-1)]
    for pid in range(nperms):
        permed_data = pd.concat(
            (ddat.loc[:, nonpermed_cols],
             ddat.loc[:, ['sample_type'] + PERMED_COLS]
             .groupby("sample_type")
             .sample(frac=1, replace=False, random_state=rng)
             .reset_index(drop=True)),
            axis=1)
        perm_res.append(calc_dhs(permed_data, pid=pid))
    perm_res = pd.DataFrame(perm_res)

    pvals = {}
    for dh in DH_NAMES:
        pvals[dh] = (perm_res.loc[0, dh] <= perm_res[dh]).mean()
        print(f"{dh}:{pvals[dh]}")

    bootdf = []
    for bid in range(nboots):
        boot_data = (ddat.groupby('sample_type')
                     .sample(frac=0.8, replace=False, random_state=rng)
                     .reset_index())
        bootdf.append(calc_dhs(boot_data, pid=bid))
    bootdf = pd.DataFrame(bootdf).rename(columns={'pid': 'bid'})
    return perm_res, bootdf, pvals


def divergent_results_table(perm_res, bootdf, pvals):
    """Tidy one-row-per-hypothesis frame: observed stat, permutation p,
    bootstrap 2.5/97.5 percentiles, significance."""
    qs = bootdf.quantile([0.025, 0.975])
    rows = []
    for dh in DH_NAMES:
        rows.append(dict(
            hypothesis=dh.upper() if not dh.startswith('ex') else dh,
            statistic=float(perm_res.loc[0, dh]),
            p_value=float(pvals[dh]),
            ci_lower=float(qs.loc[0.025, dh]),
            ci_upper=float(qs.loc[0.975, dh]),
            significant=bool(pvals[dh] < 0.05),
            supported=bool(pvals[dh] < 0.05 and perm_res.loc[0, dh] > 0),
        ))
    return pd.DataFrame(rows)
