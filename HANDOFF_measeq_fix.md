# Handoff: fix vacuous scalar/strict invariance tests (HiTOP CFA pipeline)
# v2 -- supersedes prior version; incorporates the ID.fac resolution

Repo: https://github.com/Shotgunosine/HiTOP, branch `cfas`.
Package: `src/hitop_cfa/` (fit.py, stepwise_metric.py, stepwise_scalar.py,
exhaustive.py, r_env.py, lookup.py). Main notebook: `notebooks/NB_2_cfa_as_reg.ipynb`.

State: all previous CFA results DELETED by the author; everything re-runs
from scratch under the corrected models. No salvage constraints.
Validation (task 1) is COMPLETE and ACCEPTED -- the measEq/std.lv ladder
is confirmed non-vacuous on all 14 scales. Current gate: tasks 2-3
(integration) plus the smoke test (task 6) before any full-length runs.

EXECUTION MODEL: the production pipeline runs from the notebooks
(NB_2_cfa_as_reg.ipynb primarily; NB_2_cfa_exploratory.ipynb for the
exhaustive searches). The package code in src/hitop_cfa/ is the library
the notebooks call. Therefore: update the notebook cells as needed so
they call the new measEq-based functions correctly (imports, the 5-level
ladder, the derived scales_failing_metric list, the scalar-continuation
loop) -- but do NOT execute the full-length notebook runs. The AUTHOR
kicks off the overnight runs from the notebooks once the code and
notebook updates are complete and the smoke test has passed. The smoke
test itself (one scale, num_iter=50) is the only permutation-based
execution the agent should run.

## Problem 1 (confirmed): vacuous scalar/strict under plain group.equal

For ordinal indicators, lavaan's continuous-style group.equal shortcuts do
not produce testable scalar/strict models:
- group.equal="intercepts": intercepts already fixed to 0 in all groups;
  nothing constrained; lavaan frees non-reference latent means instead.
  Empirical: scalar df = metric df - 1 (LESS constrained than metric).
- group.equal="residuals": residual variances already fixed to 1 under
  theta. strict df == scalar df, delta-chisq == 0, permutation p = 1.0
  for every scale (the symptom that exposed this).
Verified on all 14 scales (df ladder, check_invariance_dfs.py).
Fix: Wu & Estabrook (2016) models via semTools::measEq.syntax
(ID.cat="Wu.Estabrook.2016"). Level ladder for ordinal data:
configural -> thresholds -> metric(thr+load) -> scalar(+intercepts)
-> strict(+residuals). permuteMeasEq param= per delta test:
"thresholds", "loadings", "intercepts", "residuals" (all supported
keywords in semTools 0.5-8).

## Problem 2 (confirmed, resolved): ID.fac misconfiguration

First measEq attempt used ID.fac="auto.fix.first" to preserve the
project's marker convention. RESULT: underidentified models.
- Uniform +2 npar / -2 df vs plain at configural across all 14 scales
  (latent means freed in both groups with nothing to identify them --
  categorical items have no free intercepts to anchor against).
- semTools warns explicitly: "For factors measured only by categorical
  indicators, constraints on intercepts are insufficient to identify
  latent means... recommended to instead set ID.fac = 'std.lv'."
- lavaan: vcov not positive definite (smallest eigenvalue ~4e-15).
- Diagnostic evidence: diff_configural_identification.py. Under
  --id-fac std.lv, measEq configural EXACTLY matches plain configural
  (insomnia: df 4=4, npar 32=32; loadings all free + factor variance
  fixed, i.e. pure reparameterization of the marker model).

DECISION: ID.fac = "std.lv" for ALL models. measeq.py and
check_invariance_dfs_v3.py already updated to this default.

Consequences:
- NO marker item exists under std.lv. Factor identified by variance fixed
  to 1 in reference group; freed in group 2 once loadings constrained
  (measEq handles automatically).
- Stepwise simplification: remove all marker bookkeeping. Pass
  excluded_item=None to find_worst_item (function handles None already);
  every item has a testable loading MI; ablation candidate pool is all
  items (it already was); delete "(marker = current[0])" prints and
  marker-related docstrings.
- Manuscript: the "first item of each subscale as the marker item"
  sentence (and rationale) is replaced by std.lv identification, cite
  Wu & Estabrook (2016). If the prereg specified marker identification,
  add a deviation note; justification = semTools warning + numerically
  singular vcov (forced, not discretionary).

## Files ready (drop into repo / adapt)

- measeq.py (v2, std.lv default) -> src/hitop_cfa/. Contains:
  WU_ESTABROOK_LEVELS, LEVEL_NEW_PARAMS, build_measeq_model /
  fit_measeq_level (uses R globals from fit.push_model_to_r),
  extract_item_mis_from_thresholds (op "|", item = part before "|",
  max-MI per item), assert_level_adds_df (raise if df(higher) <=
  df(lower); call before EVERY permuteMeasEq delta test).
- check_invariance_dfs_v3.py -> standalone df-ladder validation,
  --measeq flag now fits std.lv W&E models.
- diff_configural_identification.py -> the parTable diff tool that
  resolved Problem 2 (keep for the paper trail; --id-fac flag).
- stepwise_scalar.py (v3) -> resume-from-metric-run rewrite of
  src/hitop_cfa/stepwise_scalar.py. STILL NEEDS: measEq model
  construction, threshold-MI extractor instead of the ~1-based one,
  marker bookkeeping removal. NOTE: its load_metric_run /
  assume_metric_invariant features must only ever point at measEq-era
  pickles; all pre-measEq pickles are deleted, so this is currently safe
  by construction.

## Task list (revised)

1. VALIDATE -- COMPLETE (author ran check_invariance_dfs_v3.py --measeq,
   all 14 scales, gp_en pair). Result: ACCEPTED. Every consecutive level
   adds df on every scale; no identification/vcov warnings observed.
   Validated df arithmetic under std.lv W&E (k items, 2 groups, 4
   categories): config->thresholds = +k; thresholds->metric = +(k-1);
   metric->scalar = +(k-1); scalar->strict = +k. Use these as smoke-test
   ground truth. npar behavior is expected and correct: +2k at
   thresholds (group-2 intercepts + residual variances freed, thresholds
   equated via constraints), +1 at metric (group-2 latent variance
   freed), -(k-1) at scalar and -k at strict (parameters fixed back).
   NOTE: the "Expected if constraints are real" lines the script prints
   are stale marker-ID guesses -- ignore or delete them; the generic
   measEq per-pair Δdf verdict is authoritative.
   3-item scales: configural saturated (df=0, expected); thresholds and
   above are real tests (df=3+), so min_items=3 remains viable.
   Preview from scaled chisq jumps (not yet permutation-tested): scalar
   and/or strict will likely genuinely fail for several scales (e.g.
   shame_guilt, appetite_gain at scalar; indecisiveness, anxious_worry at
   strict) -- the scalar-target/metric-fallback design in task 4 will be
   exercised; budget compute for the continuation stage.
2. Integrate measeq.py into src/hitop_cfa/. Rewire fit.py's
   cfa_helper_func to the 5-level ladder via fit_measeq_level, with
   assert_level_adds_df before each permuteMeasEq call. cfa_levels()
   gains the thresholds level.
3. stepwise_metric.py: per-pair test becomes configural -> thresholds ->
   metric. New removal tier between configural-ablation and loading-MI:
   thresholds fail -> threshold-MI removal
   (extract_item_mis_from_thresholds). Remove marker bookkeeping
   (excluded_item=None). Keep: combinatorial configural ablation,
   all_config_passed filter, CFI(0.001)->TLI(0.001)->RMSEA cascade,
   removed_items tuple + ablation_level history conventions.
4. DECIDED (author, revised): the invariance target is SCALAR
   (thresholds + loadings + intercepts under W&E), with METRIC
   (thresholds + loadings) as the fallback core when no >=3-item scalar
   core exists. Rationale: the study's clinical-vs-HV latent mean
   comparisons are only valid under scalar invariance -- at the metric
   level, group-2 item intercepts are free (they absorb location
   differences item-by-item) and the group-2 latent mean is fixed, so no
   mean difference is even estimable. The intercepts level constrains
   item intercepts and frees the group-2 latent mean (net ~k-1 df; a
   real test under measEq, unlike the old vacuous pipeline). This also
   matches the prereg's literal language ("core set of scalar invariant
   items").
   Architecture: two stages. (a) Metric-targeting stepwise search as in
   task 3. (b) For each metric core, run the scalar continuation
   (stepwise_scalar.py -- ON the critical path): swap to measEq models;
   item removal at the intercepts level uses intercept MIs (op "~1" --
   the original extractor is valid again under measEq since intercepts
   are genuinely free/constrained now); threshold-MI and loading-MI
   tiers as defensive lower-level handling; marker bookkeeping removed;
   resume feature points only at measEq-era pickles. If continuation
   bottoms out above min_items, the metric core is that scale's
   deliverable.
   Reporting rule downstream: ICCs may use metric-fallback cores;
   clinical-vs-HV mean comparisons are reported ONLY for scales with
   scalar cores. Strict (+residuals) remains report-only on final cores.
5. Notebooks (UPDATE ONLY -- do not execute the full runs; the author
   launches these): edit NB_2_cfa_as_reg.ipynb so its cells are ready to
   run the new pipeline end-to-end: (a) baseline run_specific_cfa pass
   over the original scales with the 5-level ladder; (b) a cell that
   DERIVES scales_failing_metric programmatically from the baseline
   results (replace the hardcoded list -- the failure pattern may shift
   under the corrected models; handle extract_p's 'NA' strings when
   filtering); (c) the stepwise metric loop (existing persistence
   pattern: per-scale history pickles + in-progress/final summary
   pickles); (d) the scalar-continuation loop (try
   do_stepwise_scalar_from_metric_run, except FileNotFoundError ->
   do_three_way_cfa_stepwise_scalar from the full item list, for scales
   that passed metric without a stepwise run). Update
   NB_2_cfa_exploratory.ipynb's exhaustive-search calls to the measEq
   path as well. Leave the cells unexecuted with clear markdown headers
   so the author can run them top-to-bottom overnight.
6. Smoke test first: one scale, num_iter=50, full ladder end-to-end
   including assert_level_adds_df, before any overnight run.

## Environment / conventions to preserve

- pixi env; BLAS pinned to 1 thread BEFORE rpy2 loads R (r_env.py +
  pixi [activation.env]).
- set_seeds(12345) before every fit (python random + R L'Ecuyer-CMRG).
- semTools 0.5-8 pinned; extract_p parses summary() text output --
  fragile, do not upgrade semTools without checking.
- permuteMeasEq multicore LAPACK dgesdd crashes: defensive tryCatch fix
  on fork branch Shotgunosine/semTools@defend_parallel; stepwise modules
  have retry-with-fewer-cores fallbacks.

## Manuscript implications

- Methods: WLSMV + theta unchanged; identification becomes std.lv (no
  marker); level ladder becomes configural/threshold/metric/scalar/strict
  per Wu & Estabrook (2016), Psychometrika 81(4), 1014-1045, with
  threshold invariance described as the ordinal analog of location
  invariance.
- The recently revised methods paragraph needs: marker sentence replaced;
  level definitions updated; the stepwise description's marker-ablation
  clause removed (no marker to ablate).
- Corrections note: same genre as the ordered= omission -- silent
  estimator/identification-level issues caught pre-submission by
  results-level checks (p=1.0 pattern; df ladders). The
  assert_level_adds_df guard makes vacuous comparisons structurally
  impossible going forward.
