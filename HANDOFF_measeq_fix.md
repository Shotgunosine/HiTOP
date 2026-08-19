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

## PROGRESS
(agent session, 2026-08-18; tasks 2-6. Commits 38d4e74..c2fdb79 on `cfas`,
plus the PROGRESS commit itself.)

### Task 2 -- measeq.py integration (commit e4fc320, then 9b1d9e3)
- measeq.py moved to src/hitop_cfa/measeq.py; exports added to __init__
  (WU_ESTABROOK_LEVELS, LEVEL_NEW_PARAMS, build_measeq_model,
  fit_measeq_level, extract_item_mis_from_thresholds, assert_level_adds_df,
  plus load_metric_run / do_stepwise_scalar_from_metric_run /
  permute_measeq_with_retry).
- fit.py: cfa_helper_func climbs configural -> thresholds -> metric ->
  scalar -> strict, every level via fit_measeq_level, with
  assert_level_adds_df before EVERY permuteMeasEq delta test.
  permuteMeasEq's `param` is what the level newly adds. Signature change:
  do_metric/do_scalar/do_strict replaced by max_level; returns
  (flag_passed_metric, config_p, thresholds_p, metric_p, scalar_p,
  strict_p). cfa_levels(name) now returns the ordered level list.
  New permute_measeq_with_retry centralizes the full->half->serial
  multicore fallbacks for all callers. build_cfa_cmd kept for
  configural-only use with an explicit vacuity warning.
- run_specific_cfa rows gain a `pthresholds` column (see review flags).

### Task 3 -- stepwise_metric.py (commit c04ddc4)
- Per-pair test is configural -> thresholds -> metric on measEq models,
  df-guard before each delta test.
- New removal tier between configural ablation and loading-MI removal:
  thresholds fail -> extract_item_mis_from_thresholds -> remove max-MI item
  (action 'thresholds_mi_removal', removal_reason 'thresholds_mi_worst').
- Marker bookkeeping removed (excluded_item=None; no "(marker = ...)"
  prints). Preserved: combinatorial configural ablation with
  all_config_passed filter, CFI(0.001)->TLI(0.001)->RMSEA cascade,
  removed_items tuple + ablation_level history conventions, retry
  fallbacks. History rows add per-pair thresholds_p/thresholds_passed and
  all_thresholds_passed.

### Task 4 -- stepwise_scalar.py (commit 730c6f9)
- Package copy replaced with the repo-root v3 (they were byte-identical;
  root staging copy deleted) and updated per the DECIDED block: measEq
  models at every level; target SCALAR continuing from each metric core;
  intercept-MI (op "~1") removal at scalar; threshold-MI and loading-MI
  tiers as defensive lower-level handling; marker bookkeeping removed;
  load_metric_run documented as measEq-era-pickles-only (all old pickles
  deleted; kept that way). skip_lower iterations still fit all lower
  models and still assert the df ladder; only the redundant permutation
  tests are skipped. NOTE: the intercept-MI extractor turned out to be
  structurally impossible under W&E -- see task 6 finding B; the scalar
  stage is BLOCKED on your decision.

### Task 5 -- notebooks (commit b6d2101; EDITED ONLY, nothing executed)
- NB_2_cfa_as_reg: (a) baseline 5-level run_specific_cfa pass documented
  under a new measEq header; (b) new cell DERIVES scales_failing_metric
  from orig_cfa_res (pd.to_numeric(..., errors='coerce') handles
  extract_p's 'NA' strings; a scale is failing unless every pair has
  numeric pmetric >= .05); (c) stepwise metric loop now consumes the
  derived list, same persistence pattern; (d) new scalar-continuation
  section: try do_stepwise_scalar_from_metric_run, except
  FileNotFoundError -> do_three_way_cfa_stepwise_scalar from the full
  item list; saves {scale}_scalar_history.pkl,
  stepwise_scalar_in_progress.pkl, stepwise_scalar.pkl.
- NB_2_cfa_exploratory: cfa_helper_func calls updated to
  (max_level='strict', 6-value unpack incl. pthresholds); inv_levels
  gains 'thresholds'; manual inattention row records gp_en__thresholds;
  markdown note that its hardcoded noninvariant_scales list is
  pre-measEq and must be replaced with the derived list before running.
- Stale pre-measEq outputs cleared from both notebooks (they were
  records of the vacuous pipeline).

### Task 1 cleanup
- Stale "Expected if constraints are real" lines deleted from
  check_invariance_dfs_v3.py (commit 38d4e74, which also commits this
  handoff + the diagnostic scripts as the paper trail).

### Task 6 -- smoke test (notebooks/smoke_test_measeq.py, commit c2fdb79)
Insomnia (k=4), num_iter=50, all three pairs. Re-run with:
`cd notebooks && pixi run python smoke_test_measeq.py`
(outputs in notebooks/log/smoke_measeq*, transcript in
notebooks/log/smoke_measeq_stdout_v2.txt).

df ladders -- PASSED, all three pairs, exactly the validated formulas:
```
configural=4  thresholds=8  metric=11  scalar=14  strict=18
config->thresholds +4 (+k)   thresholds->metric +3 (+(k-1))
metric->scalar     +3 (+(k-1))   scalar->strict  +4 (+k)
```

FINDING A (bug, FIXED, commit 9b1d9e3): the first smoke run returned
permutation p = 0 at thresholds on EVERY pair (and metric, on direct
test) while the parametric Satorra-2000 tests inside the same
permuteMeasEq objects were unremarkable (gp_en thresholds: perm p=0 vs
parametric p=0.49). The permuted null was degenerate -- all 50 permuted
delta-chisq values exactly 0. Root cause was ours: permuteMeasEq refits
con/uncon per permutation via lavaan::update(), which re-evaluates the
original call; our call was cfa(measeq_mod_str, ...) with ONE shared R
global for the model string, so both refits resolved to the last-built
model (identical models -> delta == 0). Fixed by storing each level's
syntax under a fit-specific global (<r_fit_name>_mod_str). This is the
mirror image of the p=1.0 bug and is why the smoke-test gate existed;
task-1 validation could not have caught it (no permutations there).
Post-fix (gp_en, 50 iters): thresholds perm p=0.60 (parametric 0.49),
metric perm p=0.10-0.12 (parametric 0.15), nulls non-degenerate.

Post-fix smoke results:
- STEP 2 run_specific_cfa GP_EN: CONFIG p=0.38, THRESHOLDS p=0.6,
  METRIC p=0.12, then CRASH at scalar (finding B).
- STEP 3 stepwise metric: 3-way metric invariance at iteration 0 with
  all 4 items (per-pair thresholds/metric permutation tests all passed).
  MI extractors were exercised in the pre-fix run and returned proper
  item keys (threshold MIs, e.g. {hitop160: 0.09, hitop254: 1.64,
  hitop261: 0.36, hitop268: 1.32}); no plabels/NAs seen anywhere.
- STEP 4 scalar continuation: load_metric_run resume + skip-lower path
  worked, then CRASH at the scalar permutation test (finding B).

FINDING B (STOP-AND-REPORT -- scalar/strict machinery blocked on your
decision): under Wu-Estabrook, the scalar model imposes intercept
invariance by FIXING both groups' intercepts to 0 (shared nu.* labels,
free=0) and freeing the group-2 latent mean; strict likewise fixes
group-2 residual variances back to 1. There are NO "==" equality
constraints for intercepts/residuals (only loadings and thresholds are
label-equated). Consequences, verified on insomnia/gp_en:
1. permuteMeasEq(param="intercepts") -> MI.obs is EMPTY -> semTools'
   summary() errors ("replacement has 1 row, data has 0") -> extract_p
   raises. Same applies to param="residuals" at strict. This is a
   listed stop trigger, so I did not work around it in the pipeline.
2. The op "~1" intercept-MI extractor in stepwise_scalar can never
   return anything: the handoff's DECIDED assumption ("the original
   extractor is valid again under measEq") does not hold. (The handoff's
   own npar note -- "parameters fixed back" -- already implied this.)
3. Validated alternatives (diagnostics only, not wired in):
   - Omnibus permutation with param=NULL works at scalar AND strict:
     gp_en scalar perm p=0.02 (parametric 0.018 -- insomnia genuinely
     fails scalar, consistent with the task-1 preview), strict perm
     p=0.92 (parametric 0.725); healthy non-degenerate nulls.
   - lavaan::modindices() on the scalar fit returns per-item MIs for
     the fixed group-2 "~1" rows (insomnia/gp_en: hitop261 4.77,
     hitop268 3.58, hitop160 2.35, hitop254 2.23) -- a direct "which
     item's intercept most differs" score test usable as the removal
     signal (unadjusted, i.e. no permutation Tukey correction, but MIs
     only rank items for removal).
   RECOMMENDATION (your call): scalar/strict delta tests via
   param=NULL omnibus permutation; scalar removal driven by
   modindices() group-2 intercept MIs; equivalent modindices-based
   signal at strict is unnecessary (report-only). Alternative: patch
   the Shotgunosine/semTools fork's summary() to tolerate empty MI
   tables -- fixes the crash but still yields no intercept MIs.

Warnings observed:
- semTools warns on every param="thresholds" permutation test: "This
  function is not yet optimized for testing thresholds. Necessary
  identification contraints might not be specified." Post-fix behavior
  looks sane (permutation p tracks parametric; threshold MIs keyed by
  item and matched to hitopNNN|tN parameters), but flagging since the
  thresholds tests will now gate every scale.
- The usual "No AFIs were selected, so only chi-squared will be
  permuted" notes; benign.

### Other flags for your review
- NB_invariance_plot.ipynb infers the level reached by COUNTING NULLS
  per row of orig_cfa_res.csv; the new pthresholds column shifts that
  count. Needs a small update before reuse (not in the task list, left
  untouched).
- extract_p on permuteMeasEq output parses the lowercase "chisq" summary
  line (the permutation p). R's grep is case-sensitive, so the
  parametric "Chisq diff" line is not matched -- still true post-measEq,
  verified.
- cfa_helper_func's signature changed (max_level replaces the three
  do_* flags; `ordered` dropped -- measEq.syntax requires explicit item
  names, and the item list is always used). Both notebooks updated;
  anything else calling it directly will need the same change.
- Smoke-test p-values are 50-permutation coarse; the df assertions are
  the ground truth. The metric perm p of 0.10-0.12 at gp_en will
  resolve more finely at num_iter=1000.
- semTools in the pixi env reports 0.5.8.903 (the defend_parallel fork
  build); BLAS pinning, set_seeds(12345)-before-every-fit, and the
  retry-with-fewer-cores fallbacks are preserved throughout.

### State / what's next (author)
- Tasks 2, 3, 5 complete and smoke-validated through metric. Task 4's
  code is complete but its scalar stage cannot run until you decide on
  the finding-B mechanism; the scalar-continuation notebook cells will
  crash at the first scalar permutation test as things stand. Do NOT
  launch the overnight runs before that decision; the baseline
  (NB_2_cfa_as_reg cell 'strict' ladder) would also crash at scalar for
  any scale that reaches it.
