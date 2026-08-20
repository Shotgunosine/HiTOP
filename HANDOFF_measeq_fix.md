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

## PROGRESS -- round 2 (2026-08-18, after author decisions)

AUTHOR DECISIONS (recorded): finding-B option 1 -- scalar/strict delta
tests via param-free omnibus permutation, scalar removal via
lavaan::modindices() group-2 intercept MIs; extract_p fixed by reading
the permuteMeasEq object directly; check_secondary_criteria converted to
fitMeasures; NB_3's cores workflow rewired now with HiTOP cores and
other-scale (PHQ/GAD/BAARS) cores handled through one unified derivation;
exploratory exhaustive searches switched to whichcfa='scalar'.

### Code (commit a3ffc82)
- LEVEL_NEW_PARAMS[scalar/strict] = None -> cfa_helper_func and
  cfa_test_scalar_with_mi run those delta tests param-free (omnibus).
- extract_item_mis_from_scalar rewritten on lavaan::modindices
  (op "~1", group > 1 rows = score test for freeing each fixed group-2
  intercept; unscaled `mi`, matching the X2 convention of the
  threshold/loading extractors; unadjusted -- MIs only rank items for
  removal).
- extract_p now returns the exact float from the permuteMeasEq object's
  AFI.pval["chisq"] slot (the value summary() prints, unrounded). The
  old text parse matched the permutation line only via R grep's case
  sensitivity and died when semTools' MI summary errored. NOTE: p-values
  and fit indices are now exact rather than the printed roundings, so
  borderline pass/fail can differ from what the old rounded strings
  would have produced (all results regenerate from scratch, so there is
  no mixed-provenance risk).
- check_secondary_criteria reads cfi.robust/tli.robust/rmsea.robust via
  fitMeasures (same quantities, exact).
- exhaustive_cfa_ablations now gates success on the REQUESTED whichcfa
  level's p on every pair (NaN fails). BEHAVIOR CHANGE FLAG: the
  pre-measEq code gated on the metric flag even when whichcfa='scalar'
  (the other-scales searches), so old "successes" included
  metric-passing/scalar-failing combos; under the new gating they do
  not.
- All cfa_helper_func call sites audited: package (fit.run_specific_cfa,
  exhaustive) and the two NB_2_cfa_exploratory cells; all use the
  max_level signature and 6-value unpack.

### Notebooks (commits 59c7e73, 1ac83da; edited only, not executed)
- NB_2_cfa_as_reg: the scalar-continuation loop now derives each scale's
  deliverable explicitly -- load_metric_run (FileNotFoundError -> full
  item set, i.e. the baseline-verified metric core), scalar search, and
  core_level in {'scalar','metric',None} with removals recorded relative
  to the original scale. stepwise_scalar.pkl is the final-cores table.
  New report-only section runs every final core up the ladder to STRICT
  on all three pairs -> final_cores_strict_report.csv (+ log file).
- NB_2_cfa_exploratory: HiTOP exhaustive loop -> whichcfa='scalar'.
- NB_3_ICC: unified core assembly replaces the hardcoded orig_scales
  rows and the stepwise/exhaustive patchwork. HiTOP cores come from
  stepwise_scalar.pkl; HiTOP exhaustive alternates
  (hitop_{scale}__ex_invcore, confirmatory=False) and PHQ/GAD/BAARS
  exhaustive cores ({scale}__invcore, confirmatory=False, gp_en-only
  evidence) flow through the same code path with the same columns
  (core_level / confirmatory / inv / reduced). Downstream naming
  conventions preserved: reduced HiTOP cores are
  hitop_{scale}__invcore; full-scale cores keep bare names and their
  ICCs come from section 1's precomputed columns. Sum-score construction
  (and measures_for_icc_invcores) keys off the explicit `reduced` flag.
- NB_invariance_plot: highest-level-passed computed explicitly from the
  p-values over the 5-level ladder (the old null-count broke with
  pthresholds and credited a tested-but-failed last level); heatmap adds
  a Thresholds band (6 categories).
- NB_4_convdiv: sum-score cell keys off `reduced`; prominent note that
  the hypothesis functions' hardcoded __invcore/__ex_invcore/full-scale
  column names are pre-measEq outcomes -- REBUILD from the new cores.pkl
  after the overnight runs (mean-comparison-style claims restricted to
  core_level == 'scalar' per the reporting rule).
- NB_5_compare_to_archived: marked as the pre-measEq comparison harness;
  its equality assertions are expected to fail against measEq-era
  results by design.

### Smoke test -- PASSED end-to-end (log: notebooks/log/smoke_measeq_stdout_v3.txt)
- df ladders: +4/+3/+3/+4 exactly, all three pairs (k=4).
- run_specific_cfa GP_EN (num_iter=50): config 0.38, thresholds 0.6,
  metric 0.12, scalar 0.02 (genuine fail, matches parametric 0.018),
  strict NA. All values numeric via the slot-based extract_p.
- Metric stepwise: 3-way metric invariance with all 4 insomnia items.
- Scalar continuation (resume + skip-lower): scalar failed at val_en
  (0.00) and gp_en (0.02), passed val_gp (0.10); aggregated modindices
  intercept MIs {hitop261: 22.26, hitop268: 6.94, hitop254: 5.89,
  hitop160: 2.41} -> removed hitop261 (the same item the standalone
  modindices diagnostic ranked first) -> 3-item core
  [hitop160, hitop254, hitop268] passes the FULL ladder on all pairs
  (gp_en: 0.66/0.38/0.48/0.08). MI dict keys verified as item names.
- Warnings: the semTools "not yet optimized for testing thresholds"
  warning still fires on every param="thresholds" test (behavior
  verified sane); lavaan prints a note that modindices() ignores
  equality constraints -- expected and benign here (we read MIs for
  FIXED group-2 intercepts; the loading/threshold equality constraints
  are not what is being tested).

### For your review before the overnight runs
- The exact-vs-rounded p change (extract_p / check_secondary_criteria)
  and the exhaustive target-level gating are deliberate behavior
  changes; both are flagged above for the corrections note.
- NB_4's hypothesis-to-core-name mapping is the one remaining manual
  step after results exist (flagged in the notebook itself).
- gp_en scalar p for the 3-item insomnia core was 0.08 at 50
  permutations -- close to threshold; expect finer resolution (and
  possibly different outcomes) at num_iter=1000.

## PROGRESS -- round 3 (2026-08-18): outcome-coupled subscale lists derived

Author request: replace hardcoded subscale lists with generated ones
(commit 978efe7). Every list encoding an analysis OUTCOME is now derived
from pipeline outputs; only substantive definitions stay literal
(orig_items / other_scales formulas, the depression-vs-anxiety domain
grouping in NB_4, instrument-total names, display-name exceptions).

- NB_2_cfa_exploratory: noninvariant_scales derived from orig_cfa_res.csv
  (full set fails 3-way scalar); other-scales baseline collects
  other_orig_cfa_res.csv and the failing list is derived from it; item
  luts keyed by scale name (other_luts dict); excluded-subsets formulas
  derived from stepwise_scalar.pkl removed_nos (>= 3 items); the
  interpretation item-id dict generated from orig_items (the old copy had
  drifted: indecisiveness missing, items 240/159 dropped).
- NB_3_ICC: per-subscale measures_for_icc entries generated from the
  final-cores table.
- NB_4_convdiv: programmatic core resolution from cores.pkl per scale
  (confirmatory __invcore > full-scale > __ex_invcore > full scale with a
  no-invariant-core warning per the prereg's enriched-only rule), exposed
  as canonical hitop_{scale}__core alias columns used by ALL hypothesis
  code (dep/anx lists, HiTOP sums, cols_for_d, calc_dhs); a resolution
  table (column, path, core_level) is printed for review. The divergent
  computed columns are renamed hitop_all_depression__core /
  hitop_all_anxiety__core. The dead commented-out pre-refactor hypothesis
  function was removed (git history keeps it). This supersedes round 2's
  "re-map NB_4 by hand after results" flag -- the mapping is now
  automatic; what remains manual is only reviewing the printed resolution
  table and applying the enriched-only rule if any scale ends up with no
  core.
- NB_icc_plots: measure_dict/order_dict generated (order = ascending
  full-scale ICC within HiTOP/BAARS/totals blocks, matching how the old
  hand orderings were built); block-header bolding by label text, not
  positional index; suffix-splitting made robust to the new PHQ/GAD/BAARS
  core rows. Outcome-specific presentation tweaks that CANNOT be derived
  are flagged in place: footnote asterisks (re-add via DISPLAY_OVERRIDES
  after review) and the panic exhaustive-core suppression.

Run-order dependency made explicit: the exploratory notebook's derived
lists read orig_cfa_res.csv / stepwise_scalar.pkl, so NB_2_cfa_as_reg's
baseline and scalar-continuation sections must run first.

## PROGRESS -- round 4 (2026-08-18): overnight-readiness hardening + dress rehearsal

Author asked for maximum assurance the overnight runs succeed. Two
tracks: latent-bug hunting/hardening, and a full DRESS REHEARSAL that
executes patched copies of all six production notebooks end-to-end.

### Latent bugs found and fixed (commits edf4407, f6a498e)
1. load_metric_run raised KeyError (not FileNotFoundError) on an empty
   metric summary pickle -- which happens if NO scale fails metric under
   the corrected models -- bypassing the notebook's fallback handler.
2. astype(float, errors='ignore') is a silent no-op under pandas 3
   (this env is 3.0.3): the baseline p columns stayed strings. Replaced
   with explicit pd.to_numeric.
3. Stale review-note (scale, ssix) pairs merge into exhaustive.pkl as
   rows with exhaustive_choice=True but no item set and crashed NB_3's
   sum-score loops. NB_3 now drops them with a loud warning.
4. float('NA') in the exploratory manual-inattention cell would crash
   mid-notebook if any level failed; now nan-tolerant. Empty exhaustive
   results (zero successes) now produce schema-complete DataFrames so
   the review-note merges survive.
5. NON-CONVERGENT candidate models crash permuteMeasEq ("fit measures
   not available if model did not converge") and the retry fallbacks
   can't help (not a fork crash). FOUND LIVE by the rehearsal: the
   3-item insomnia subset (hitop160, hitop254, hitop261) does not
   converge at configural on the val_en pair. New
   measeq.fit_is_converged() is checked after EVERY fit in
   cfa_helper_func and both stepwise testers; a non-convergent model is
   recorded as a failed level (p = NaN) and the search moves on.

### Overnight fault tolerance in NB_2_cfa_as_reg (commit edf4407)
- All four long loops (baseline, stepwise metric, scalar continuation,
  strict report) wrap per-scale work in try/except; failures are
  printed and appended with tracebacks to cfa_dir/run_errors.log and
  the run continues.
- Baseline and strict report persist incrementally
  (orig_cfa_res_in_progress.csv, final_cores_strict_report_in_progress
  .csv), so a late crash cannot lose completed scales. Stepwise loops
  already had in-progress pickles.
- The scalar loop's full-scale fallback now requires the scale to be a
  VERIFIED baseline metric passer; a scale whose upstream stage errored
  gets an explicit 'upstream_error' row, never a silently assumed core.
  A scalar-search exception falls back to the verified metric core with
  an 'error' flag (carried through NB_3 for review).
- A final run-summary cell prints core counts and every recorded error.

### Dress rehearsal (notebooks/rehearse_overnight.py, commit 9ac4143)
Executes PATCHED COPIES of the production notebooks in run order with
num_iter=50, 3 small scales (insomnia, appetite_loss, shame_guilt),
other scales restricted to gad_sum, NB_4 perms/boots=20, and all output
paths redirected to data/rehearsal/ (production data untouched).
Re-run any time: `cd notebooks && pixi run python rehearse_overnight.py`.

Result (second run, after the convergence-guard fix): PASSED.
  NB_2_cfa_as_reg 2.5 min / NB_2_cfa_exploratory 2.1 min /
  NB_invariance_plot 0.1 / NB_3_ICC 0.3 / NB_icc_plots 0.1 /
  NB_4_convdiv 0.1 min. All 14 artifact hand-offs present; no
  run_errors.log. The mini final-cores exercised ALL THREE core_level
  outcomes through the full chain: insomnia -> scalar core
  [hitop160, hitop254, hitop268]; shame_guilt -> metric fallback;
  appetite_loss -> no core (3-item scale failed a level; no search
  space at min_items=3) -- NB_3 excluded it and NB_4's resolver fell
  back to the full scale with the printed enriched-only warning.
A separate synthetic-artifact pre-test also executed NB_invariance_plot
/NB_3/NB_icc_plots/NB_4 against fabricated pickles covering the nasty
edges (orphan review notes, NaN levels, every core_level case): PASSED.

### Runtime advisory for the real overnight run
Mini NB_2 (3 small scales, 50 iters) = 2.5 min. The real run is 14
scales (up to 10 items), 1000 iters, and the new ladder runs up to 5
permutation tests per scale-pair (the old pipeline ran at most 4, and
effectively 2 for most scales). Extrapolation is rough (larger models
fit slower; the stepwise/ablation search space dominates for 10-item
scales), but NB_2 alone could plausibly take on the order of 8-15 h.
Mitigations already in place: everything persists incrementally, so
progress can be checked mid-run (watch orig_cfa_res_in_progress.csv,
stepwise_in_progress.pkl, stepwise_scalar_in_progress.pkl grow) and the
notebook can be split across nights at any section boundary -- the
scalar continuation resumes from the metric pickles by design. Also
note: a permuteMeasEq LAPACK fork crash triggers the serial fallback,
which at 1000 iters is ~10x slower for that one test (pre-existing
behavior, now at least survivable).

### Leftovers to know about
- Rehearsal artifacts: data/rehearsal/, data/rehearsal2/ (synthetic
  pre-test), notebooks/zz_rehearsal_*.ipynb (executed copies with
  outputs, gitignored) -- inspect or delete freely.
- The rehearsal overwrote two stale pre-measEq scratch logs in
  notebooks/log/ (mylog_3wayCFA_origscales..., mylog_3wayCFA_lookingforinv...);
  both were gitignored scratch from the deleted-results era.

## PROGRESS -- round 5 (2026-08-19): parametric pre-screen calibration

Author asked whether a permissive-alpha parametric pre-screen could
accelerate the exhaustive ablation while guaranteeing no permutation-
passing core is missed. Calibration: all 954 permutation tests recorded
by the overnight run (594 item-set x pair ladders; baseline + stepwise
histories + strict report) were refit and paired with their parametric
analogs (configural: pvalue.scaled; deltas: Satorra-2000 lavTestLRT).
Scripts: notebooks/calibrate_screen.py, notebooks/analyze_calibration.py;
data: notebooks/log/calibration_pairs.csv. Zero refit failures.

VERDICT (two parts):
1. CONFIGURAL CANNOT BE SCREENED PARAMETRICALLY. Spearman rho = 0.38;
   at alpha=.005 the screen would discard 257 true permutation passers,
   including ladders with permutation p = 1.0 (e.g. anhedonic full set
   gp_en: parametric p ~ 0 vs permutation p = .144). Root cause is
   conceptual: permuteMeasEq's configural test asks whether the groups
   fit EQUALLY well (observed chisq vs group-permuted chisq null),
   while the parametric p tests ABSOLUTE fit -- different hypotheses.
   (Also: 3-item configural models are saturated; no parametric p at
   all.) The configural permutation test is unavoidable per candidate.
2. DELTA LEVELS SCREEN CLEANLY BUT SAVE LITTLE. thresholds/metric/
   scalar: rho = .98-.99; ZERO permutation passers lost at any alpha up
   to .02 across all 342 recorded delta tests (min passer parametric
   p = .0444). Proposed alpha_screen = .005 (9x margin). But because
   the ladder is already failure-gated and the unscreenable configural
   permute dominates (546/906 usable tests), the screen avoids only
   ~13-16% of delta permutes = ~5-6% of total permutation work.
   (Strict: one passer at parametric p = .0101 -- strict is report-only
   and outside the search, but do NOT screen strict at .05-ish alphas.)

CONCLUSION: the pre-screen is safe at the delta levels but is NOT the
order-of-magnitude lever hoped for; the top-down exhaustive's cost
lives in the per-candidate configural permutation, which tests a
hypothesis with no cheap parametric analog. The remaining levers, in
increasing order of methods-change weight: (a) delta screen at .005
(free, zero observed cost); (b) stepwise-certificate size caps and
reuse of recorded configural passers at certified sizes; (c) the
bottom-up triple-first search (bounded 120-combo screen per 10-item
scale, kill-switch when no triple passes); (d) sequential early-stopping
permutation counts (Besag-Clifford style) for clear-cut configural
cases -- the only direct attack on the dominant cost, and a methods
change requiring the author's sign-off.

## PROGRESS -- round 6 (2026-08-19): exhaustive search rebuilt (author decisions)

Author decisions implemented in exhaustive.py (screened_ladder_test,
exhaustive_search_scale, stepwise_configural_cap) and the exploratory
notebook:
- EARLY ABANDON: pairs tested in datasets-dict order with val_gp first
  (the most-lethal pair: 63% candidate configural failure rate); a
  combination is dropped at its first failing pair/level. Result-
  identical (success requires all pairs); measured ~46% fewer candidate
  configural permutes, ~69% fewer full-ladder permutes. Note: simulated
  configural-first / level-first orderings were WORSE (+17% / +23% on
  the 49 recorded ladders; the insured-against event -- late-pair
  configural failure after an earlier full-ladder pass -- occurred
  2/49) and were not adopted.
- CALIBRATED DELTA PRE-SCREEN: alpha_screen = .005 on thresholds/
  metric/scalar (Satorra-2000 lavTestLRT); configural NEVER screened
  (round-5 calibration). Screened-out combos are recorded with their
  parametric p for the audit trail.
- SIZE CAPS: stepwise_configural_cap reads each scale's iteration-0
  ablation certificate (anhedonic 8, social_anxiety 8, well_being 9;
  None where the full set passed configural; 0 = ablation refuted
  everything).
- ORDER: scales searched smallest-first.
- RESUMABILITY: per-combination progress persisted atomically to
  cfa_dir/exhaustive_progress_{scale}.pkl; a killed run resumes where
  it stopped; completed scales short-circuit and re-print their '!!!!!'
  result lines so the parsed log stays complete after a resume rewrite.
  Delete a scale's progress file to force a fresh search.

Validation: functional test (insomnia, 25 iters) exercised fresh run /
completed short-circuit / partial resume with identical results, and
the printed successes dict round-trips ast.literal_eval (parse cells
safe). Notably the search found exactly the stepwise scalar core
(hitop160/254/268) and screened out the two emphatic failures at
parametric p ~ .0002-.0004. Dress rehearsal v3 PASSED end-to-end with
the new machinery (exploratory 1.4 min vs 2.1 pre-redesign).

Overnight-run bookkeeping: the author stopped the old exploratory run
at 07:25 after ~4 h on anhedonic (117 complete combos, no successes,
sizes 9/8/partial 7). Those seed-identical results were parsed from the
log and SEEDED into data/cfa/exhaustive_progress_anhedonic_depression
.pkl as failed entries, so the relaunch skips them.

RELAUNCH: NB_2_cfa_as_reg is complete and must NOT be rerun (it would
recompute everything); launch only the exploratory notebook:
    caffeinate -i ./notebooks/run_overnight.sh NB_2_cfa_exploratory.ipynb
Rough expectation with caps+abandon+screen at 1000 iters: small scales
in minutes-to-an-hour total; worst case remains the 10-item scales if
no subset passes until deep sizes (order 10-20 h each), but the search
is now resumable at combination granularity.

## PROGRESS -- round 7 (2026-08-19): containerized HPC path for the exhaustive searches

Author request: run the larger exhaustive searches on HPC. Delivered
(commit below); the container IMAGE itself was NOT built here (no
docker/apptainer on this machine) -- build it per HPC.md and run the
verification cross-check before trusting it.

- pixi.toml/pixi.lock: linux-64 added and solved; the existing
  osx-arm64/osx-64 sections are byte-identical (0/213 entries changed),
  and the linux-64 solve pins r-base 4.2.3 / rpy2 3.5.1 / python 3.11,
  matching the local pipeline (pandas 3.0.5 vs local 3.0.3 -- patch-
  level drift, acceptable).
- hpc/Dockerfile + hpc/hitop_cfa.def (Apptainer, buildable without
  Docker): pixi 0.69.0 base, `pixi install --locked`, then
  hpc/install_r_libraries.R installs pinned lavaan 0.7-2 and the
  patched semTools fork @db294f2 with build-time version assertions.
  BLAS pinned to 1 thread in the image. Data is NOT baked; bind-mount.
- src/hitop_cfa/scales.py: ORIG_ITEMS / OTHER_SCALES formulas as the
  single source for headless runs (the notebooks keep their own copies
  -- keep in sync; future cleanup could point the notebooks here).
- notebooks/run_exhaustive_scale.py: headless per-scale entry point
  (unit of HPC parallelism). Same machinery and progress-pickle
  convention as the notebook; per-scale temp csv so array tasks sharing
  a cfa dir never collide. Tested locally: fresh run + resume
  short-circuit both reproduce the known insomnia result.
- hpc/exhaustive_array.sbatch: SLURM array template (one task per
  scale, --cpus-per-task=14).
- HPC.md: build / verify / ship data / run / monitor / bring results
  home. The transfer currency is cfa/exhaustive_progress_{scale}.pkl:
  copied back into local data/cfa, the exploratory notebook
  short-circuits every HPC-completed scale and regenerates its log
  lines, so the parse/consolidation pipeline is unchanged.

REPRODUCIBILITY NOTE (important): permuteMeasEq splits its L'Ecuyer RNG
streams by worker count, so permutation p-values are bit-identical to
the local pipeline ONLY at 14 workers. The runner defaults to
--cpus 14 and the sbatch template requests exactly 14 CPUs; more cores
would be statistically valid but not reproducible against local runs.

## PROGRESS -- round 8 (2026-08-19): GP-vs-EN two-way variant notebook

Author request: notebooks/NB_2_as_reg_gp_en.ipynb searches for scalar
invariance between the general-population and enriched samples only
(single gp_en pair; validation sample unused). Derived programmatically
from NB_2_cfa_as_reg so all hardening carries over (fault tolerance,
incremental persistence, derived failing lists, scalar continuation
with metric fallback, strict report, run summary). All outputs isolated
in data/cfa_gp_en/ (histories, stepwise/scalar pickles, strict report,
run_errors.log) -- nothing touches the 3-way pipeline's data/cfa/.
Distinct log names (mylog_2wayCFA_gp_en_*). Validated by a sandboxed
end-to-end execution (3 small scales, 50 iters): all stages ran, all
three got gp_en scalar cores, strict report intact, no errors.
Downstream note: NB_3/NB_4 consume data/cfa (the 3-way results) only;
the gp_en results are a separate analysis until the author decides how
to consolidate them.

### Round 8 addendum: gp_en baseline reused from the 3-way run

Author question prompted two confirmations: (1) do_three_way_cfa_
stepwise_mi (and the scalar/strict machinery) iterate whatever datasets
dict they receive -- "three-way" is historical naming, so with
{'gp_en': ...} they genuinely test only that pair; (2) the gp_en
baseline ladder need not be recomputed: cfa_helper_func reseeds per
scale x pair call, so the 3-way run's GP_EN rows are bit-identical to
a fresh gp_en run. NB_2_as_reg_gp_en now reuses those rows from
data/cfa/orig_cfa_res.csv and runs the ladder fresh only for scales
missing from that record (self-sufficient if the 3-way baseline never
ran). Stepwise stages always run fresh -- the 3-way removal paths were
steered by the validation pairs and do not transfer. Sandbox execution
confirmed: 3/3 baselines reused (1000-iter values), 0 fresh, stepwise
and scalar stages fresh at 50 iters, no errors.

## PROGRESS -- round 9 (2026-08-19): remaining two-way notebooks + other-scales pipeline

- The author created NB_2_cfa_as_reg_gp_val / _en_val as copies of the
  gp_en variant (and renamed that to NB_2_cfa_as_reg_gp_en); the copies
  were retargeted: pair V_GP/val_gp (resp. V_EN/val_en) with the 3-way
  labels kept so reused baseline rows and history columns line up;
  outputs isolated in data/cfa_gp_val/ and data/cfa_en_val/; distinct
  logs; baseline rows reused from the 3-way orig_cfa_res.csv. The data
  concat keeps the 3-way order (val first) -- permutation draws depend
  on row order, so this preserves seed-identity of reused and fresh
  tests alike. Sandbox executions (3 small scales, 50 iters): both
  PASSED with pair-specific cores and no errors.
- NB_2_cfa_as_reg_other_gp_en: full stepwise pipeline for the six
  PHQ/GAD/BAARS scales. AUTHOR DECISION: gp_en only -- the validation
  sample contains none of these measures (confirmed against
  dat_val.csv), so the requested triple/pairwise design is impossible;
  a recontact-wave longitudinal design was offered and declined.
  Formulas come from hitop_cfa.scales.OTHER_SCALES; item texts from the
  combined instrument luts; baseline rows reused from the exploratory's
  other_orig_cfa_res.csv when present (seed-identical), fresh
  otherwise; outputs in data/cfa_other_gp_en/. Sandbox execution
  (2 BAARS subscales, 50 iters): PASSED, both full-set scalar at gp_en,
  no errors.
- Six pipeline variants now exist (3-way, gp_en, gp_val, en_val,
  other_gp_en, plus the exploratory exhaustive); each owns its output
  dir; pipeline_status.py works on any of them.

## PROGRESS -- round 10 (2026-08-19): wave-comparison notebooks for the other measures

Author request: four more stepwise pipelines for PHQ/GAD/BAARS using the
recontact wave. Data fact discovered en route: the gridall_full files
ARE the recontact cohort -- every row has both waves (GP n=398,
EN n=255), smaller than the grid1st samples used by the main pipelines.
Notebooks (each derived from NB_2_cfa_as_reg_other_gp_en; outputs
isolated per notebook in data/cfa_other_{tag}/; wave-2 frames take the
*_recontact item columns renamed to plain ids with an explicit
whichdata group label; self-resuming baselines):
  - NB_2_cfa_as_reg_other_gp1_gp2 (GP wave1 vs GP wave2)  [PAIRED]
  - NB_2_cfa_as_reg_other_en1_en2 (EN wave1 vs EN wave2)  [PAIRED]
  - NB_2_cfa_as_reg_other_gp1_en2 (GP wave1 vs EN wave2)  [independent]
  - NB_2_cfa_as_reg_other_gp2_en1 (GP wave2 vs EN wave1)  [independent]
The two within-sample notebooks compare the SAME subjects across waves;
their intros carry a prominent caveat that multigroup CFA and the
permutation test treat groups as independent, so those runs test
exchangeability of the wave label (parameter stability over time)
rather than a standard two-sample contrast (test-retest reliability
proper lives in NB_3's ICCs). Sandbox executions (2 BAARS subscales,
50 iters) of gp1_gp2 and gp2_en1: PASSED end-to-end with the expected
group sizes (398/398, 398/255), full-set scalar cores, no errors.

## PROGRESS -- round 11 (2026-08-19): PHQ-8 gp_en follow-up notebook

notebooks/NB_phq8_gp_en_followup.ipynb (outputs: data/cfa_phq8_followup/):
A) conventional-criteria screen (scaled CFI/RMSEA deltas; robust variants
are undefined on constrained measEq fits), B) per-group PHQ-8 EFAs,
C) DIF effect sizes correctly decomposed (metric-model group-2
intercepts vs the scalar-model latent mean: d_i = nu_i - lambda_i*alpha;
the naive configural-curve version conflated the real severity gap with
bias and was discarded), D) exhaustive scalar search for a PHQ-8 subset
on gp_en (capped at size 6 by the stepwise certificate; resumable).

Sections A-C are fit-based -- their sandbox outputs ARE the production
numbers:
- A: under conventional delta-CFI (<=.01) / delta-RMSEA (<=.015)
  criteria the full PHQ-8 PASSES every level (max |dCFI| = .0012);
  configural absolute fit mixed (CFI .980, RMSEA .104). The
  non-invariance is invisible to the field's usual yardstick and
  detected only by the exact permutation test.
- B: genpop is near-unidimensional (eigenvalues 5.62, 0.62, ...);
  enriched less so (4.51, 0.98, ...) with a 2-factor geomin split of
  somatic (sleep/fatigue/appetite) vs affective/cognitive items
  (2-factor CFI .975 in enriched) -- the structural difference behind
  the configural failure.
- C: real severity gap alpha = +1.14 latent SD (= +7.03 expected sum
  points); per-item non-uniform DIF is small (|d| .04-.31, dMACS
  .03-.20, "small" by Nye-Drasgow benchmarks) and largely CANCELS at
  the sum level: net measurement bias -0.05 of 24 points. The earlier
  naive +7.37 figure decomposes into the real gap plus ~0 net DIF.
INTERPRETATION SHIFT: statistically real but small, mutually-cancelling
item-level DIF atop a structural (dimensionality) difference; pooled
sum-score analyses are far less threatened than the raw configural
failure suggested, though the cancellation is item-profile-dependent
and the structure difference stands. Section D (exhaustive) runs at
1000 iters via the runner.

## PROGRESS -- round 12 (2026-08-20): DIF effect sizes with CIs for all pairwise violations

New: hitop_cfa.dif_effect_sizes (src/hitop_cfa/effect_size.py) -- for one
scale on one 2-group pair, decomposes non-invariance from the single
METRIC-model fit: uniform severity shift alpha = GLS projection of the
free group-2 intercepts on the loadings (weights = robust vcov block;
numerically close to the scalar-model MLE, validated on the PHQ anchor:
+1.112 vs +1.142), non-uniform DIF d_i = nu_i - lambda_i*alpha, signed
item bias / dMACS / net & gross sum-score bias integrated over
N(alpha, psi2), with 95% CIs by simulating the free parameters from the
fit's robust covariance (single-model formulation keeps CIs coherent;
this is why alpha is a projection rather than the scalar-fit MLE).

notebooks/NB_invariance_effect_sizes.ipynb (executed; outputs in
data/effect_sizes/: pairwise_dif_summary.csv + per-item csv + forest
plot) covers every full-original-scale violation across HiTOP x
{val_gp, val_en, gp_en} and PHQ/GAD/BAARS x {gp_en + 4 wave pairs}:
49 violations, all converged.

HEADLINE: item-level DIF is real -- 109 of 328 item x pair DIF
estimates have 95% CIs excluding zero (largest: situational_phobia
hitop225 val_gp dMACS .49; phq_8 gp1_en2 .39; hyposomnia hitop231 .35
REPLICATED across val_en and gp_en) -- but it CANCELS at the sum level:
only 1 of 49 violations has a net sum-bias CI excluding zero
(situational_phobia val_gp, -0.29 points [-0.46, -0.05]), and gross
|bias| ceilings are <= ~5% of scale range everywhere. Real severity
gaps dwarf measurement bias on the gp_en-type contrasts (e.g.
anhedonic_depression gp_en: +8.4 points real vs +0.2 [-0.1, 0.8] bias).
Manuscript framing: exact permutation tests detect genuine but small,
mutually-cancelling item DIF; sum-score comparisons are barely
distorted, though item-level/reweighted uses do not inherit the
cancellation.
