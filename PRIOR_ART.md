# Prior art and framing notes for the manuscript

This document consolidates five literature searches run between 2026-09-23 and
2026-10-01 to position the manuscript described in `RESULTS.md` for submission
to *Assessment*. It is written for a reader who has not followed the
measurement-invariance methods literature: each section first explains the
idea in plain terms, then walks through what the prior papers established, and
ends with what the manuscript can and cannot claim as a result.

**How the evidence was gathered.** Each search fanned out web queries across
several angles, fetched the primary sources, extracted falsifiable claims, and
put every claim through three independent adversarial verification passes
against the source text (a claim survived only with at least two of three
votes). Claims that were refuted are listed in §11 so they are not
accidentally used. Two limits apply throughout: (1) several searches hit their
web budget before completing contradiction searches, so statements of the form
"no prior paper does X" were *absence from the verified set*; a dedicated
contradiction search for each such claim was run on 2026-10-01
(`PRIOR_ART_contradiction_report.md`: cited-by walks, PubMed/Europe PMC
full-text queries, two adversarial deep-research runs) and sections 3–12 now
reflect its verdicts — four claims were contradicted in whole or in part (end-
to-end consequences, the HiTOP-SR short window, reanalysis reversals, first
`permuteMeasEq` application) and two weakened (reporting-window design,
exhaustive search), so re-check the survivors at submission; (2) several abstracts were
verified via indexing services because publisher pages were blocked, so
condition-level details inside paywalled papers were not always confirmed.
Every DOI below was resolved through Crossref on 2026-10-01.

---

## 0. A short primer (skip if you know this material)

**Measurement invariance (MI)** asks whether a questionnaire measures the same
thing in the same way in two groups — or in the same group under two
administration conditions. It is tested as a ladder of increasingly
constrained multi-group factor models. For ordinal (Likert-type) items the
ladder used here, following Wu & Estabrook (2016), is:

- *configural* — the same items load on the same factor in both groups;
- *thresholds* — the cut-points that turn the latent response into observed
  categories are equal;
- *metric* — factor loadings are equal (items relate to the construct equally
  strongly), which licenses comparing correlations across groups;
- *scalar* — item intercepts are equal, which licenses comparing observed
  means or sum scores across groups;
- *strict* — residual variances are also equal.

**How a level is judged.** Each step adds constraints and the question is
whether fit got meaningfully worse. There are two families of answer:

- *Significance tests* on the change in the chi-square statistic. The
  classical likelihood-ratio test is known to be oversensitive in large
  samples and badly calibrated for ordinal data, which is why the field drifted
  away from it.
- *Fixed cutoffs on changes in approximate fit indices (ΔAFIs)*: the rule that
  the Comparative Fit Index may not drop by more than .01 (Cheung & Rensvold,
  2002) and that RMSEA may not rise by more than .015 (Chen, 2007). These are
  the "conventional criteria" throughout. They are overwhelmingly what applied
  papers use (Putnick & Bornstein, 2016, found ΔCFI reported in 73% of tests).
- *Permutation tests* (Jorgensen, Kite, Chen & Short, 2018; Kite, Jorgensen &
  Chen, 2018): shuffle the group labels many times, refit, and build the null
  distribution of the change statistic *from the data at hand*. This gives a
  significance test whose false-positive rate is correct for the actual sample
  size, model size and item distribution. The manuscript uses 1,000
  permutations at every ladder step.

**Partial invariance and "cores."** When a level fails, the usual remedy is to
free or drop the offending items until the remaining set passes. The standard
way to pick items is *stepwise*: remove the item with the largest modification
index, refit, repeat (a greedy search). The manuscript additionally runs an
*exhaustive* search — every subset of three or more items — which can prove
that no invariant subset exists at all.

**Does non-invariance matter?** Detecting a violation is not the same as
showing it distorts scores. *Differential item functioning* (DIF) effect sizes
quantify how much each item's expected score shifts between groups at equal
latent levels (dMACS, Nye & Drasgow's index; see Nye et al., 2019), and
summing signed item shifts gives the net bias in the sum score. When item
shifts point in opposite directions they *cancel*, so a scale can show real
item-level DIF with negligible sum-score bias.

**Alignment** (Asparouhov & Muthén, 2014) is a non-sequential alternative to
stepwise partial invariance that estimates the invariance pattern globally; it
assumes most parameters are invariant and is not identified in its "free" form
with only two groups.

---

## 1. The study and the framing question

A preregistered study adapted the preliminary HiTOP internalizing scales
(Watson et al., 2022) from a one-year to a two-week reporting window and
fielded them with the PHQ-8, GAD-7 and BAARS-IV in a US general-population
sample (n ≈ 497) and a sample enriched for diagnosed depression, anxiety or
ADHD (n ≈ 305), with two-week retest, comparing both to the original
validation sample. The framing question the manuscript is built around is:

> When a symptom inventory changes its reporting window and crosses population
> strata, what does rigorous invariance testing find — and does it matter?

The results that bear on framing (details in `RESULTS.md`):

1. Permutation-tested ladders fail somewhere for almost every scale and pair;
   the PHQ-8 fails at the *configural* level between the general-population
   and enriched samples.
2. Conventional ΔCFI/ΔRMSEA criteria, run on all 20 scales × 3 pairs, detect
   21 of the 40 failing scale × pair cells — 9/13 and 8/14 on the two
   time-window pairs, but only 4/13 on the population-strata pair (plus one
   false flag there) — frequently at the wrong level, and never at the
   configural level. ΔCFI alone detects 7 of 40.
3. Exhaustive subset searches find a triply invariant subset for 6 of 14
   constructs and prove none exists for 8. For social anxiety the unique
   solution contains an item the greedy search discarded first.
4. Item-level DIF is real (about a third of item CIs exclude zero) but cancels
   in sums (1 of 49 net-bias CIs excludes zero; gross bias ≤ 5% of range), and
   all preregistered validity conclusions survive core vs full-scale scoring.
5. Retest reliability is good-to-excellent and unaffected by item removal.
6. Six current HiTOP-SR (sub)scales can be reconstructed from the fielded
   items, giving the current instrument two-week-window psychometrics.

---

## 2. Journal fit: *Assessment*

**The argument.** The journal's declared scope is "applied clinical
assessment, with an emphasis on … test development, validation, and
interpretation practices," explicitly covering psychopathology. Its Registered
Report guidelines name three classes of study, the first being psychometric
evaluation of existing instruments "such as temporal consistency, factor
structure, measurement invariance," and the second being abbreviated or revised
versions of existing scales (Samuel, 2019). A completed study cannot use the RR
track, but the taxonomy shows the editors' priorities. The journal is also the
home venue of the scales themselves: Watson et al. (2022) and the HiTOP
measure-development overview (Simms et al., 2022) appeared in the same special
section. Leonard Simms, who co-leads the HiTOP measures workgroup, has been
announced as incoming Editor-in-Chief (start date and conflict-of-interest
handling unknown).

**In-journal precedents to cite.**

- Gonzalez & Pelham (2021) argue in *Assessment* that DIF testing addresses
  statistical rather than practical significance, name *DIF cancellation*
  explicitly, and insist it must be evaluated empirically rather than assumed —
  exactly the manuscript's score-level analysis.
- Ock, McAbee, Mulfinger & Oswald (2020) pair invariance tests with dMACS and
  conclude statistical non-invariance was practically negligible — a template
  for the "detectable but inconsequential" arc in this journal.
- Li, He, Waldman & Rodriguez-Seijas (2025) is a current *Assessment* HiTOP
  invariance paper using the manuscript's own estimator (WLSMV) that declared
  full invariance via ΔCFI < .01 while explicitly declining to interpret
  chi-square difference tests significant at every step. It is the natural
  foil for the criteria thread; it should be characterized fairly (they also
  reported congruence coefficients and item-level comparisons), and the tone
  should be diplomatic since the journal published it recently.
- *Added 2026-10-01.* Black, Humphrey, Panayiotou & Marquez (2024) is an
  in-journal end-to-end precedent for the consequence arc (alignment-based
  detection plus Millsap–Kwok selection effects on an adolescent
  internalizing measure; §6), and Olaru & Danner (2021) is an in-journal
  precedent for global, ACO-based selection of invariant items (§7). Both
  should be cited as the line the manuscript joins.

**What this settles.** An instrument-anchored framing fits the journal better
than a pure methods paper, and both the consequence arc and the criteria
critique have in-journal precedent.

---

## 3. Element A — invariance across reporting windows

**The idea.** Changing "in the past year" to "in the past two weeks" is a
change in what respondents are asked to recall. Whether the same items still
measure the same construct in the same way is an empirical question, and it is
rarely asked.

**What exists.**

- Schneider, Choi, Junghaenel, Schwartz & Stone (2013) compared one-day and
  seven-day recall versions of PROMIS pain-interference, fatigue and
  *depression* items in 100 US adults over 28 diary days. About a third of
  items showed uniform DIF between windows, yet scale-level impact was minor
  (maximal expected-score differences of 0.6–1.8 points on 25–33-point scales)
  — while population means still shifted 0.28–0.82 SD, invalidating norm-based
  interpretation. This is the closest ancestor of the manuscript's story and
  anticipates the "detectable but inconsequential" arc in miniature. Its
  limits: N = 100, IRT/Wald tests against a different calibration sample (so
  window and sample are confounded), no clinical strata, no subset search.
- Andrade & Rodríguez (2018) compared "right now" with "past week" POMS
  instructions in Spanish athletes (n = 350 per group): configural held but
  metric failed, and even partial-invariance models failed; they recommended
  separate norms per time frame and called for equivalence testing before
  mixing instructions. This is the citation that a window change *can* break
  invariance.
- Rawers, Mangiarulo, Shevlin & McElroy (2024) tested DASS-21 DIF across
  past-week, past-month and past-six-month recall in three student groups
  (n ≈ 134 each) via MIMIC models and found none, while explicitly naming the
  recall period as a neglected gap in harmonization research. Cite it as the
  paper that names the gap.
- Chilver, Burns, Botha & Butterworth (2023) manipulated K6 recall (7 vs 30
  days) within subjects and found no substantive effect; Kuharic et al. (2026),
  the PROMIS Physical Function 8c FDA-qualification study (1,810
  general-population adults plus 300 with cancer), found no meaningful DIF
  between no-recall and seven-day versions. Both are nulls under conventional
  methods.
- *Added by the 2026-10-01 contradiction search.* Separate-sample window
  designs predate the manuscript. Lai, Cook, Stone, Beaumont & Cella (2009)
  gave "exactly the same questions" of the FACIT-F under 7-day and 4-week
  windows to separate cancer-outpatient groups (n = 100 / 116; ordinal-logistic
  χ² and Rasch t DIF criteria). Condon et al. (2020) randomly assigned 2,400
  respondents — 1,001 with cancer and 1,399 from the general population — to
  no-recall, 24-hour or 7-day PROMIS Physical Function items and tested DIF by
  recall period with lordif (pseudo-R² ≥ .02; none flagged; the planned
  score-impact stage was therefore never run; the DIF test was pooled across
  strata). Rohlfs et al. (2023) compared "right now" and "past week" BRAMS mood
  ratings in separate athlete samples, but only at the configural level. At the
  level of diagnoses, Ringwald, Forbes & Wright (2022) found the
  internalizing/externalizing structure meta-analytically invariant across
  lifetime vs current symptoms and across samples selected vs not selected for
  psychopathology. None used a calibrated test or a dMACS/expected-score
  consequence analysis (details and quotes in the contradiction report, C1).

**What the manuscript can claim.** The window question is *rarely tested*, not
untested, and neither the separate-sample design nor the parallel-strata
design is new: Lai et al. (2009) and Condon et al. (2020) gave identical items
under different windows to separate groups, and Condon et al. (2020) and
Kuharic et al. (2026) did so with clinical (cancer) and general-population
strata. Every prior window study found used conventional criteria (lordif
pseudo-R², ordinal-logistic χ², Rasch t, fixed fit cutoffs, configural-only
CFA) or no invariance test, and none tied the detected non-invariance to
dMACS, expected-score or sum-score bias. What is new is the combination,
applied to a psychiatric symptom inventory: calibrated permutation tests at
every Wu–Estabrook level, a three-group design that includes the instrument's
original validation sample, an exhaustive subset search, and a score-level
consequence analysis. Do not say the prior window studies lack a
parallel-strata design. The intro should cite Schneider → Andrade & Rodríguez
→ Rawers, with Lai, Condon and Kuharic as the separate-sample PRO precedents.

---

## 4. Element B — invariance between clinical and community samples

**The idea.** A depression item can mean something different to someone with
a diagnosis than to someone without one. If so, comparing sum scores across
those groups compares different measurements.

**What exists.**

- Doi, Ito, Takebayashi, Muramatsu & Horikoshi (2018) found GAD-7 invariance
  held only to the *metric* level between non-diagnosed and self-reported
  anxiety-disorder respondents (N = 1,447 Japanese adults) while scalar held
  between clinical subgroups — the failure sits exactly at the stratum
  boundary the manuscript targets.
- Lee, Kang, Kang & Lee (2023) declared the PHQ-9 invariant across six
  chronic-disease comparisons and age in a Korean population sample using
  ΔCFI/ΔRMSEA, and dismissed a partial scalar failure as "not practically
  relevant" by citation rather than computation — a second foil illustrating
  the gap the manuscript fills.
- Briers, Sanders, Northam, Dadds & Hawes (2026) found metric-but-not-scalar
  invariance of the 6-item ARI across community and clinic-referred children,
  but full scalar invariance across age within the community sample. Florean
  et al. (2022) found the APQ invariant across gender but only partially
  across clinical status. Both are in the target journal family, both show
  verdicts differing by grouping variable within one study, and both attribute
  this to genuine sample differences without comparing criteria. Note that the
  Briers failure is on a 6-item, small-df model — the regime in which §5 shows
  ΔRMSEA misbehaves.
- The HiTOP-BR (2026, *Journal of Personality Assessment*) achieved scalar
  invariance between German clinical and non-clinical samples under
  conventional criteria (ΔCFI = .001), with no reporting-window adaptation;
  its own discussion concedes local loading differences despite global
  invariance. It is a third foil, not a threat.
- *Added by the 2026-10-01 contradiction search.* The PHQ-9 counterpart from
  the same group — Doi, Ito, Takebayashi, Muramatsu & Horikoshi (2018, *PLOS
  ONE*; a different article from the *Frontiers* GAD-7 paper above) — compared
  non-clinical adults (n = 1,163) with MDD (n = 406) and MDD-plus-anxiety
  (n = 636) groups and adopted scalar invariance using "a difference of less
  than .01 in the Δ CFI index" as its sole model-adoption criterion (verified
  at full text). It is the most direct PHQ foil for the manuscript's PHQ-8
  result. Medical-vs-community comparisons also pass configural: PHQ-9 in
  stroke (Blake et al., 2025; scalar failed on appetite and tiredness), PHQ-8
  in an HIV clinic (Whittington et al., 2026; scalar held, residual failed),
  and PHQ-8 with vs without chronic pain (De La Rosa et al., 2026).

**What the manuscript can claim.** A dedicated contradiction search
(2026-10-01; PubMed, Europe PMC full text, and every PHQ-9 study reviewed by
Lamela et al., 2020) found no PHQ-8/9 or GAD-7 paper reporting a
*configural* failure between general-population and clinical strata; every
clinical- or medical-vs-community comparison found passed configural (e.g.,
PHQ-9 non-clinical vs MDD reached scalar under a ΔCFI < .01 rule; Doi et al.,
2018, *PLOS ONE*). The manuscript's PHQ-8 result can be stated as, to our
knowledge, the first reported configural-level failure at this boundary.
Scalar-level failures at the boundary are documented (GAD-7: Doi et al., 2018,
*Frontiers*) and should be cited as precedent.

---

## 5. Element C — conventional ΔCFI/ΔRMSEA criteria are uncalibrated

This is the methods thread, and the literature here is the strongest of any
section. The argument has four steps.

### 5.1 Where the cutoffs come from, and why they are not fixed properties

Cheung & Rensvold (2002) and Chen (2007) derived the ΔCFI ≤ .01 and ΔRMSEA ≤
.015 rules from simulations under particular models and sample sizes. Chen's
own results already show the change in fit indices depends on the pattern of
non-invariance (uniform vs mixed), the proportion of non-invariant items, and
N, and she recommends different cutoffs by N and balance. Meade, Johnson &
Braddy (2008) found that condition-specific cutoffs beat any single value and
that a ΔCFI of .002 — not .01 — performed well. Kang, McNeish & Hancock (2016)
quantified this: the null 1st percentile of ΔCFI for a metric test ranged from
about −.05 (loadings .40) to −.001 (loadings .95) with three indicators, and
the authors explicitly recommend against ΔCFI because "values suggestive of
invariance change markedly as a function of factor loading magnitude, the
number of indicators per factor, and the sample size." This is the mechanism
behind *pair-dependent* sensitivity: different pairs have different N, loading
magnitudes and violation sizes, so one fixed cutoff cannot be calibrated for
all of them.

### 5.2 ΔRMSEA misbehaves in both directions with model size

- *Small models → false alarms.* Kenny, Kaniskan & McCoach (2015) showed that
  for correctly specified models with small df, conventional RMSEA cutoffs
  "too often falsely indicate a poor fitting model," and recommended not
  computing RMSEA at all for low-df models. A single-factor three-item scale is
  just-identified at the configural level — zero df, RMSEA reported as 0 by
  convention (Czerwiński & Atroszko, 2023) — so any added constraint moves
  RMSEA off an artificial floor. McNeish (2026) demonstrates the invariance
  version: under exact invariance the 99th percentile of ΔRMSEA is .035 for a
  3-item model at N = 150 per group (more than double the cutoff), and in a
  4-df empirical example a conventional ΔRMSEA of .025 rejected metric
  invariance while model-tailored cutoffs reversed the conclusion. D'Urso, De
  Roover, Vermunt & Tijmstra (2022) found ΔRMSEA false-positive rates above
  .10 on short ordinal scales. This is exactly the manuscript's appetite_loss
  flag (χ²(3) = 3.38, p ≈ .34, yet ΔRMSEA = +.018 > .015).
- *Large models → masking.* Savalei, Brace & Fouladi (2023) show that simply
  differencing RMSEA between nested models "will often mask misfit,
  particularly in model comparisons with large initial degrees of freedom";
  the same per-df misfit produces ΔRMSEA values differing by more than a factor
  of three depending only on baseline df. They propose RMSEA_D, computed from
  the chi-square difference test. Beribisky & Hancock (2024) confirm this in
  population analyses: ΔRMSEA sensitivity to a single non-invariant loading
  fell from .044 at 4 items to .018 at 12, often below the cutoff. D'Urso et
  al. and Groskurth, Bluemke & Lechner (2023) found true-positive rates near
  zero for small loading differences on 25-item scales.

The manuscript's data show both directions: artifact flags on 3–5-item scales
in the population-strata pair, and misses on the 10-item scales. **Always say
"uncalibrated in both directions with model and violation size," never "too
lenient."**

### 5.3 Delta criteria carry no information about *which* level failed

Chen (2007) found CFI and RMSEA "equally sensitive to all types of lack of
invariance" (loadings, intercepts, residuals) and never simulated configural
failures. Joo & Kim (2019) showed that a configural-type violation
(heterogeneous error covariances), when constrained equal, transfers into the
loading estimates so that *metric* invariance is rejected despite identical
population loadings. Together these frame — by analogy, not direct
demonstration — the manuscript's observation that hyposomnia and panic first
trip the conventional rules at *strict* on the time-window pair while the
permutation ladder fails at *configural*. Configural failures are invisible to
delta criteria by construction (there is no lower level to difference
against), and at the configural level the conventional verdict depends on which
absolute-fit rule is applied (all four of the manuscript's gp_en configural
failures pass scaled CFI ≥ .95 but fail scaled RMSEA ≤ .06). The level
mislocalization result can be claimed as an applied first, cautiously. The
2026-10-01 contradiction search (cited-by Joo & Kim; Europe PMC full text for
"misattribut*/mislocaliz*/wrong level") found no applied demonstration, only
two further simulation analogues: ignored cross-loadings (a configural-type
misspecification) change what fit indices detect at the metric step (Cao &
Liang, 2024), and differential noneffortful responding inflates Type I error
"only at the metric invariance level" (Rios, 2021).

### 5.4 What applied comparisons exist

Only one applied head-to-head of conventional criteria against RMSEA_D was
found (Abulela, Nickodem & Rodriguez, 2024, five social-emotional measures,
n ≈ 626,000): the two agreed. There is no applied paper comparing criterion
sensitivity across comparison types against a calibrated benchmark, and no
paper arguing that subtle clinical-vs-community non-invariance is
systematically under-detected by ΔCFI. The 2026-10-01 contradiction search
(cited-by McNeish 2026, Savalei 2023, Kang 2016, Jorgensen 2018; Europe PMC
full text) confirmed both absences. Nearest neighbors: Lee & Chmielewski
(2026), where moderated nonlinear factor analysis found HiTOP non-invariance
"not previously detected using multigroup confirmatory factor analysis"
across sociodemographic covariates (a method contrast, not a per-grouping
calibration); Trummer et al. (2026), who reported Δχ²-based Cohen's w beside
ΔCFI/ΔRMSEA decisions for the German HiTOP-SR across sex, age and SES but
note these "complemented, but did not alter" the decisions; and Lasker (2024),
a single-dataset reversal (§9).

### 5.5 What the manuscript can claim, and how

The criteria critique should be positioned as *joining* the Kenny → Chen /
Meade → Kang → Savalei / Beribisky & Hancock → D'Urso / Groskurth → McNeish
lineage, not announcing it. The contribution is the first applied,
permutation-referenced, all-scales-all-pairs demonstration in a psychiatric
inventory, with a consequence layer that none of those papers has. The
pair-dependence claim survives only in the narrowed form: *first to show,
against a permutation benchmark, that conventional criteria's detection rate
depends on which pair is compared.* Do **not** attribute the lower
population-strata sensitivity to unequal group sizes — Chen (2007) found ΔAFIs
are *larger* with unequal N — attribute it to violation magnitude. A 2026
simulation (Chen & Chao, 2026) reports that ΔAFI cutoffs' Type I error rates
are "often too conservative" with unbalanced groups; that is a statement about
false positives, not power (abstract-level), and does not revive the
unequal-N explanation refuted in §11 — read its power results before citing it
in response to a reviewer.

Reviewers will very likely ask for McNeish's dynamic cutoffs and/or Savalei's
RMSEA_D applied to the 20 × 3 screen. That analysis decides whether
"uncalibrated" prescribes tailored cutoffs or a permutation test, and it should
be done preemptively (it requires the scaled chi-square difference statistic
from `lavTestLRT`, not a difference of the scaled χ² values in the existing
table).

---

## 6. Element D — detectable but inconsequential for sum scores

**The idea.** The manuscript's second half shows that although item-level DIF
is real, it cancels in sums and leaves validity conclusions unchanged. The
question is whether anyone has already told that story end to end.

**What exists.**

- Nye, Bradburn, Olenick, Bialko & Drasgow (2019) supply the dMACS benchmarks
  (~.40/.60/.80) for the practical importance of non-equivalence — from
  simulation and literature review, not a clinical demonstration.
- Soland (2021) showed in two education RCTs that detectable non-invariance
  changed treatment effects by ≤ .03 SD — "detectable but inconsequential" in
  an education setting.
- Gonzalez & Pelham (2021, *Assessment*) argue the principle and name DIF
  cancellation; their own CES-D example found DIF that *did* shift
  sensitivity/specificity by ~.10, which is why they insist cancellation be
  tested rather than assumed.
- Schneider et al. (2013) and Ock et al. (2020) are the applied miniatures
  (§3, §2).
- *Added by the 2026-10-01 contradiction search — the arc is occupied end to
  end.* Black, Humphrey, Panayiotou & Marquez (2024, *Assessment*) assessed
  eight adolescent mental-health and well-being measures (#BeeWell,
  N = 37,149), used alignment to identify non-invariant parameters across sex
  and age, and estimated the effect on screening with the Millsap–Kwok
  selection-accuracy method: "Effects on selection were minimal, except
  sensitivity was substantially lower in boys for the internalizing symptoms
  measure." Nilsen et al. (2024, *Psychological Medicine*) ran a Wu–Estabrook
  ordinal ladder with dynamic fit cutoffs and ΔCFI ≥ −.002 on a six-item
  depressive-mood inventory (N = 560,712), reported dMACS, and showed that the
  detected non-invariance moved latent trend estimates by "about 0.01 to 0.03
  standard deviation units" — the "detectable but inconsequential" arc on a
  depressive-symptom measure. Zheng et al. (2024, *JCPP Advances*) applied
  alignment to the CBCL/1.5-5 across child and caregiver characteristics
  (including neurodevelopmental disorders) and showed that robust item sets
  excluding high-DIF items correlate highly with the full scales — close to
  the manuscript's cores-vs-full-scales logic. All three verified at full text.

**What the manuscript can claim.** The end-to-end arc is occupied (Black et
al., 2024; Nilsen et al., 2024; Zheng et al., 2024), so the manuscript joins
this line rather than opening it, and should not say the arc has only been
told piecewise. What remains distinctive is (a) the detector — permutation
tests with calibrated Type I error at every Wu–Estabrook level, where the
prior papers used alignment or fixed (if stricter) ΔCFI cutoffs; (b) the
comparisons — a reporting-window change and clinical-vs-community strata,
where the prior papers compared sex, age, survey year or demographic groups;
and (c) the consequence layer — signed net and gross sum-score bias with
confidence intervals plus a test of whether preregistered validity
conclusions survive core vs full-scale scoring. Both halves of the
manuscript's paradox — the criteria are unreliable *and* most of what they
miss does not bias sum scores — have literature behind them.

---

## 7. Element E — exhaustive subset searches and greedy path-dependence

**The idea.** Stepwise item removal is a greedy search: it commits to the
first removal and never revisits it. The manuscript's exhaustive search
enumerates every subset, which can (a) certify that no invariant subset exists
and (b) expose cases where the greedy path was locked out of the only
solution. For social anxiety, the unique triply invariant 4-item subset
contains an item the greedy metric stage discarded in its first step.

**What exists.**

- Asparouhov & Muthén (2014) state the problem canonically: the
  modification-index approach "does not guarantee that the simplest, most
  interpretable model with the fewest noninvariant parameters is reached," and
  "even with only three groups, the simplest path of model modification might
  not be obvious." Their remedy, alignment, assumes a majority of invariant
  parameters and is not identified in its free form with two groups — so it
  is unavailable in the manuscript's setting, where 8 of 14 constructs have
  *no* invariant subset. This is a citable argument that the exhaustive search
  was necessary, not merely thorough.
- MacCallum (1986) and MacCallum, Roznowski & Necowitz (1992) are the canonical
  demonstrations that data-driven specification searches capitalize on chance
  and reach inconsistent modifications across repeated samples; they recommend
  a priori alternatives. Cite for the general point.
- The CFA simulation literature largely *endorses* sequential search under its
  simulated conditions: Yoon & Millsap (2007) found it works when few items are
  non-invariant but "rarely succeeded" when many are; Yoon & Kim (2014)
  recommend always adopting the sequential method (true-positive rate 1.00 in
  17 of 18 cells); Jung & Yoon (2016) compared forward, backward and
  factor-ratio procedures. None benchmarks against an exhaustive search, all
  free constraints rather than removing items, and all assume a minority of
  non-invariant items. The manuscript operates in the regime Yoon & Millsap
  flagged as the method's failure zone.
- The IRT anchor-selection literature supplies the cascade mechanism by
  analogy: when the reference (anchor) set is contaminated with DIF items, the
  group scales are shifted and false-alarm rates inflate (Woods, 2009; Kopf,
  Zeileis & Strobl, 2015); invariant anchors become harder to find as the DIF
  proportion rises; and a greedy iterative-removal procedure carried
  contamination risk of up to 89.5% versus ≤ 6% for a one-step global strategy
  (Kolbe & Jorgensen, 2019). These are dichotomous/continuous IRT results and
  apply to ordinal item removal only by analogy — four stronger readings of
  Kopf et al. were refuted and must not be used (§11).
- *Added by the 2026-10-01 contradiction search.* Global, combinatorial item
  selection for invariance is an established technique in the short-scale
  literature. Schultze & Eid (2018) cast invariant-item-set selection "as a
  combinatorial optimization problem" solved by an ant-colony algorithm (the
  `stuart` package); Olaru et al. (2019) used ant colony optimization (ACO) to
  select items that optimize fit and invariance across four countries, argued
  that ACO "is not affected [by] sequence effects and more likely to find the
  best model instead of optimiz[ing] the scale towards a local optimum," and,
  for a four-item version, "estimated all possible models" (81 combinations);
  Jankowsky, Olaru & Schroeders (2020) and Olaru & Danner (2021, *Assessment*)
  built invariant short scales the same way, the latter reporting better
  invariance than a traditionally built short form. Schroeders, Wilhelm &
  Olaru (2016) showed on real data that stepwise selection is "prone to local
  optima" (fit and validity, not invariance). Anchor-choice model averaging
  (Schulze, Reuter & Pohl, 2022) and regularized anchor selection (Belzak &
  Bauer, 2020) are further global alternatives. None of these enumerates every
  subset under a significance test, certifies that no invariant subset exists,
  or shows MI-guided stepwise removal discarding an item of the only invariant
  subset; the ACO searches are heuristic and cannot certify absence.

**What the manuscript can claim.** Global item selection for invariance is not
new and should be cited (Schultze & Eid, 2018; Olaru et al., 2019; Jankowsky
et al., 2020; Olaru & Danner, 2021), as should the local-optimum argument
against stepwise removal (Schroeders et al., 2016; Olaru et al., 2019). What no
paper found does — and what remains an apparent first — is (a) an exhaustive
enumeration of every subset of three or more items under a calibrated
significance test, (b) a certificate that no invariant subset exists (8 of 14
constructs here), and (c) a real-data case in which MI-guided stepwise removal
discarded an item belonging to the only invariant subset (social anxiety
here). Recommended wording: *a concrete instance of the path-dependence long
asserted for MI-guided searches, in a regime (ordinal indicators, item
removal, majority non-invariance, two groups) that the simulations endorsing
sequential search did not cover, where alignment is not available and
heuristic global searches cannot certify absence.* Do not frame it as
contradicting Yoon & Kim; it realizes their own stated boundary condition.

---

## 8. Element F — the HiTOP measures and supersession risk

Watson et al. (2022) describe the scales as preliminary Phase-1 products with
an independent validation sample of 496 adults (the manuscript's third group).
Simms et al. (2022) state that "research applications and clinical translation
of the model require measures that are specifically keyed to the model" and
describe later phases. The scale developers consider the Phase-1 scales
superseded by Phase 2 and the HiTOP-SR. The official HiTOP-SR asks about the
past year, but Mostajabi, Vize, Nielsen, Ringwald & Wright (2026,
*Psychological Assessment*) administered it with a past-month window in a
mixed clinical/community sample ("Participants were asked to rate how much
each item applied to them in the past month") and attributed an unexpected
"Rarity" factor partly to the narrower window — "This narrower timescale may
have resulted in certain experiences appearing especially 'rare'" — without
testing invariance across windows (verified at full text, PsyArXiv v3). A
short-window HiTOP-SR administration therefore exists, and the manuscript
should cite it as the paper that raises the window question for the current
instrument. What remains unoccupied is a two-week window, a formal
(calibrated) test of the window change against data collected under the
original window, and clinical-vs-community invariance of HiTOP-SR item sets:
the HiTOP-BR (2026) ran clinical-vs-non-clinical invariance under
conventional criteria with no window adaptation, and the German HiTOP-SR has
been tested only across sex, age and SES within a general-population sample,
facet by facet, with Chen cutoffs (Trummer, Wendt, Schroeders & Zimmermann,
2026, preprint, who note that "larger or enriched clinical samples would allow
more complete testing"). No short form of the internalizing scales was found
(the Brazilian HiTOP-BBS and the HiTOP-BR are separate brief instruments). A
validation of superseded scales is still not a compelling deliverable in
itself. The manuscript should treat the Phase-1 scales as a
well-characterized *testbed* (their published validation sample is what makes
a three-way, exhaustively searched design possible), and lead with the
generalizable findings. The crosswalk in `RESULTS.md` shows six current
HiTOP-SR (sub)scales are composed entirely of fielded items, which lets the
paper speak to the current instrument directly; the social-anxiety result
(SR composition fails configural, a different 4-item subset is triply
invariant) and the insomnia result (the SR retained the item the invariance
search removes) are the two consortium-facing vignettes.

---

## 9. Element G — the "audit" genre

**The idea.** A recent line of meta-research audits how psychology tests
invariance and how often scales pass. Could the manuscript present itself as
part of that genre?

**What exists.**

- Maassen, D'Urso, van Assen, Nuijten, De Roover & Wicherts (2023 online; 2025
  print) reviewed 426 open-data articles from *Psychological Science* and *PLOS
  ONE*: invariance was mentioned for only 4% of 929 scale-mean comparisons
  (nearly all demographic); none of the reported tests could be reproduced;
  the four reproducible-in-principle ones all failed at configural when re-run
  with conventional cutoffs; of 174 newly run tests, 26% reached scalar and 58%
  failed completely. Caveats: the 58% includes 61 three-item scales where
  configural was assumed, forces one-factor models, and rejects configural by
  absolute fit — a prevalence statistic under conventional rules, not a
  calibrated benchmark. (Cite with sixth author *De Roover*.)
- *Maassen et al.'s own recommendations (Discussion, accepted manuscript on
  PsyArXiv; retrieved 2026-10-01).* On criteria they hedge rather than endorse:
  "researchers—including us—often resort to commonly used and widely accepted
  fit indices and demarcation criteria (e.g., Chen, 2007; Cheung & Rensvold,
  2002). However, their suitability can differ based on the data and model
  characteristics," pointing to dynamic fit index cutoffs (McNeish & Wolf);
  they do not mention permutation tests. They recommend standardized
  non-invariance effect sizes (citing Nye et al.), warn that MI-guided partial
  invariance "capitalize[s] on chance" (citing MacCallum et al., 1992),
  recommend Putnick & Bornstein's reporting items, COSMIN and Flake & Fried's
  six questions, journal-mandated measurement sections, and FAIR data and
  code. Most usable for this manuscript: "altering an existing scale
  essentially requires a reevaluation of its underlying structure … we urge
  researchers to assess a scale's factor structure and reliability separately
  for each group they analyze, especially when using modified scales" — a
  direct rationale for testing the window-adapted scales. They do not
  recommend preregistering invariance tests (their own study was
  preregistered).
- *Added by the 2026-10-01 contradiction search — a same-data reversal exists.*
  Lasker (2024, *Applied Psychological Measurement*) reanalyzed Protzko's
  randomized "meaning in life vs nonsense items" data, where invariance had
  been concluded from ΔCFI/ΔRMSEA, and found metric and scalar non-invariance
  by χ² difference tests and AIC: "Protzko (2022) used insensitive model fit
  indices that failed to indicate measurement noninvariance where it was
  tested," and "the use of RMSEAD [RMSEA with subscript D] disconfirms the
  findings of Protzko (2022)"
  (verified at full text). Protzko's published version (2025, *EPM*) keeps its
  conclusion, so the reversal is disputed. Reversals also run the other way:
  Cieciuch et al. (2014) re-tested the same 19-value data with Bayesian
  approximate invariance and found scalar invariance for all 19 values where
  exact testing had supported 10. No many-analysts or multiverse invariance
  project was found.
- *Journal-restricted audits.* Schroeders & Gnambs (2020) recalculated df for
  302 invariance-testing sequences in 128 articles from six assessment
  journals (including *Assessment*, *Psychological Assessment* and *JPA*,
  1996–2016): about a quarter had at least one irreproducible df. They audited
  reporting correctness, not decision criteria or pass rates. Contractor et al.
  (2019) coded the decision criteria used in 96 PTSD invariance analyses (Δχ²
  86.5%, ΔCFI 31.3%) — the closest psychopathology precedent for auditing
  criteria, but construct-restricted, not journal-restricted.
- *Editorials.* A Crossref sweep of *Assessment* items 2019–2026 found no
  editorial engaging Flake & Fried (2020). The nearest in-journal piece is
  Markon & Olino's (2025) introduction to a special section on "Assessment,
  Measurement, and Registered Replication" (its eight references do not
  include Flake & Fried); two regular *Assessment* articles do cite Flake &
  Fried (Buchanan, 2025, on invariance for registered reports; Flores-Kanter
  & Alvarado, 2024). Outside the journal, De Los Reyes et al. (2025) published
  an invariance editorial in the *Journal of Clinical Child & Adolescent
  Psychology* (none of its 79 references is Flake & Fried).
- Putnick & Bornstein (2016) reviewed 126 articles from 2013–14: ΔCFI reported
  in 73.2% of tests, "full" configural in 94.4%, scalar full in 57.8%; they
  note the ΔCFI < .01 rule "has been criticized as overly liberal." General
  psychology, no clinical breakdown.
- Hussey & Hughes (2020) found only 4% of 26 scales invariant across age and
  gender in Project Implicit data, using Chen-type cutoffs they themselves
  describe as a "garden of forking paths."
- Goretzko, Siemund & Sterner (2024) audited 1,011 CFA models in *Psychological
  Assessment* against model-tailored cutoffs (0% fit well by tailored RMSEA)
  but excluded multigroup models, leaving invariance practice in that journal
  family unaudited.
- Neufeld et al. (2023, *Assessment*) concede that ΔCFI/ΔRMSEA can miss
  substantial non-invariance (citing Sass, Schmitt & Marsh, 2014) and recommend
  inspecting loading and threshold differences "irrespective of the findings
  from ΔCFI and ΔRMSEA" — the under-detection concern is already on record in
  the target journal, as a caveat rather than a demonstration.
- Lamela, Soreira, Matos & Morais (2020) found only ten PHQ-9 invariance
  studies across 18 comparisons, uniformly positive — a benchmark to contrast
  with. (The stronger "0 of 10 found a violation" gloss was refuted; do not
  use it.)
- Flake & Fried (2020) is the general "measurement schmeasurement" critique;
  no *Assessment* editorial engaging it was found (see *Editorials* above).

**What the manuscript can claim.** The audit framing is available and not
preempted, **provided it is worded as an audit of decision criteria rather
than of practice prevalence**, and provided it credits the one same-data
reversal. Every prevalence audit found measures how often invariance is tested,
whether scales pass, or whether tests are reported correctly, and each
adjudicates with the conventional cutoffs the manuscript benchmarks; none
audits clinical-vs-community comparisons and none has a calibrated reference
test. Do **not** say that no reanalysis has shown a ΔCFI/ΔRMSEA verdict
reversing — Lasker (2024) did, on a non-clinical scale — and do not imply that
calibrated or alternative methods only ever overturn invariance (Cieciuch et
al., 2014, reversed toward invariance). The narrower statements survive: no
review of invariance *decision criteria* restricted to clinical-assessment
journals was found (Schroeders & Gnambs, 2020, audited df reporting in three
of them), and no *Assessment* editorial engaging Flake & Fried was found.
Suggested positioning:

> Prior audits show that invariance is rarely tested and that scales often fail
> when it is (Maassen et al.; Hussey & Hughes; Putnick & Bornstein), audits of
> assessment journals have checked how invariance tests are reported
> (Schroeders & Gnambs, 2020), and one same-data reanalysis shows a
> ΔCFI/ΔRMSEA-based invariance verdict reversing under exact tests and RMSEA_D
> (Lasker, 2024). But the audits adjudicate invariance with the same
> heuristics, whose sensitivity in clinical-vs-community comparisons is
> unknown (Neufeld et al.). We audit the criteria themselves against a
> calibrated benchmark, across comparison types, in a psychiatric inventory.

---

## 10. Integrated framing recommendation

Lead with the substantive–methods hybrid under the title question. The
exhaustive-search results are the structural backbone; the criteria critique
and the consequence analysis are the two halves of one paradox; the HiTOP-SR
crosswalk is the current-instrument payoff.

Suggested spine for the methods thread:

> Conventional ΔCFI/ΔRMSEA criteria detected half of the violations a
> calibrated test found, misattributed the level of several, produced a false
> alarm where a 3-item baseline is saturated, and were least sensitive exactly
> in the clinical-vs-community comparison where applied practice relies on them
> most — the applied counterpart of what recent simulation work (Kenny et al.,
> 2015; Savalei et al., 2023; McNeish, 2026) predicts.

Claims to state as apparent firsts — each survived a dedicated contradiction
search on 2026-10-01 (`PRIOR_ART_contradiction_report.md`), and each should
still carry "to our knowledge": the between-strata configural failure of the
PHQ-8; exhaustive proofs that no invariant subset exists (citing the ACO /
`stuart` global-selection literature as the nearest precedent); the greedy
lockout on real data; pair-dependent criterion sensitivity against a
permutation benchmark; level mislocalization in applied data (with Joo & Kim,
Cao & Liang and Rios as analogical precedents).

Claims that must **not** be stated as firsts, because the contradiction search
found prior papers (credit them instead):

- a separate-sample or parallel clinical/general-population window design
  (Lai et al., 2009; Condon et al., 2020; Kuharic et al., 2026);
- an end-to-end "calibrated or alternative detection plus score-level
  consequences" study of a mental-health measure (Black et al., 2024; Nilsen et
  al., 2024; Zheng et al., 2024);
- a short-window administration of the HiTOP-SR (Mostajabi et al., 2026);
- a same-data reanalysis reversing a ΔCFI/ΔRMSEA verdict (Lasker, 2024);
- the first empirical application of `permuteMeasEq` to ordinal symptom data
  (Kaplan-Kahn et al., 2024; Kildahl et al., 2026, configural only) — describe
  the scope instead (every Wu–Estabrook level including thresholds, 20 scales
  × three pairs, 1,000 permutations per step) without a "largest" or "first"
  claim, which was not searched for;
- global or combinatorial item selection for invariance (Schultze & Eid, 2018;
  Olaru et al., 2019).

**Citation spine by manuscript section**

| Section | Cite |
|---|---|
| Intro: window changes | Schneider et al. 2013; Andrade & Rodríguez 2018; Rawers et al. 2024; Chilver et al. 2023; Lai et al. 2009; Condon et al. 2020; Kuharic et al. 2026; Ringwald et al. 2022 |
| Intro: clinical vs community | Doi et al. 2018 (*Frontiers*, GAD-7; *PLOS ONE*, PHQ-9); Lee et al. 2023; Briers et al. 2026; Florean et al. 2022 |
| Intro: HiTOP context | Watson et al. 2022; Simms et al. 2022; HiTOP-BR 2026; Mostajabi et al. 2026; Trummer et al. 2026 |
| Intro: audit positioning | Maassen et al. 2023/2025; Putnick & Bornstein 2016; Hussey & Hughes 2020; Goretzko et al. 2024; Neufeld et al. 2023; Schroeders & Gnambs 2020; Lasker 2024 |
| Methods: identification and tests | Wu & Estabrook 2016; Jorgensen et al. 2018; Kite et al. 2018; Luong & Flake 2022; Kaplan-Kahn et al. 2024 (prior applied permutation testing) |
| Methods: conventional criteria | Hu & Bentler 1999; Cheung & Rensvold 2002; Chen 2007 |
| Methods: effect sizes | Nye et al. 2019; Gonzalez & Pelham 2021 |
| Results/Discussion: uncalibrated criteria | Kenny et al. 2015; Meade et al. 2008; Kang et al. 2016; Savalei et al. 2023; Beribisky & Hancock 2024; D'Urso et al. 2022; Groskurth et al. 2023; McNeish 2026; Czerwiński & Atroszko 2023; Abulela et al. 2024 |
| Discussion: level mislocalization | Chen 2007; Joo & Kim 2019; Cao & Liang 2024; Rios 2021 |
| Discussion: greedy lockout | Asparouhov & Muthén 2014; MacCallum 1986, 1992; Yoon & Millsap 2007; Yoon & Kim 2014; Jung & Yoon 2016; Woods 2009; Kopf et al. 2015; Kolbe & Jorgensen 2019; Schultze & Eid 2018; Olaru et al. 2019; Olaru & Danner 2021; Schroeders et al. 2016 |
| Discussion: consequences | Gonzalez & Pelham 2021; Ock et al. 2020; Soland 2021; Schneider et al. 2013; Black et al. 2024; Nilsen et al. 2024; Zheng et al. 2024 |
| Discussion: foils (handle diplomatically) | Li et al. 2025; Lee et al. 2023; HiTOP-BR 2026; Lamela et al. 2020; Doi et al. 2018 (*PLOS ONE*); Trummer et al. 2026 |

---

## 11. Claims that were refuted — do not use

- That Chen (2007) found unequal group sizes *shrink* ΔAFIs (she found the
  opposite), so unequal N cannot explain the lower population-strata
  sensitivity.
- That the ΔRMSEA small-model artifact is an *analytic* df-scaling effect
  rather than a sampling effect.
- That Lamela et al. (2020) show "0 of 10 PHQ-9 studies found a violation."
- A specific Doi et al. (2018) PHQ-9 clinical-vs-non-clinical ΔCFI-only example
  (the GAD-7 result in §4 is verified; this PHQ-9 gloss is not). *Note added
  2026-10-01:* a separate article by the same group, Doi et al. (2018, *PLOS
  ONE*, https://doi.org/10.1371/journal.pone.0199235), does report PHQ-9
  scalar invariance between non-clinical and MDD groups with "a difference of
  less than .01 in the Δ CFI index" as its sole adoption criterion (verified at
  full text). Cite that article, by its own DOI, for any PHQ-9 statement (§4);
  this entry stands for whichever source it was originally checked against
  (probably the *Frontiers* GAD-7 paper). Author to confirm.
- That Neufeld et al. (2023) "endorse" Chen cutoffs in a way that undermines
  an audit framing.
- Four stronger readings of Kopf, Zeileis & Strobl (2015): specific success
  rates (13–17%) for iteratively purified anchors; that rank-based global
  strategies outperform sequential ones with specific false-alarm rates; that
  the "all-other" anchor strategy is the IRT analogue of an MI-guided baseline;
  and that forward anchor selection is conditioned on an initial one-item
  choice. Cite Kopf et al. only for the contamination mechanism.
- That Johnson et al. (2019) "reaffirm" the GAD-7 ≥ 10 cutoff (they found ≥ 8
  optimal).

Refuted by the 2026-10-01 contradiction search (`PRIOR_ART_contradiction_report.md`;
quotes and verification level there):

- That the prior reporting-window studies lack a parallel clinical/general-
  population design (Condon et al., 2020, and Kuharic et al., 2026, had cancer
  and general-population strata), or that no study has given identical items
  under different windows to separate samples and tested DIF (Lai et al., 2009;
  Condon et al., 2020; Rawers et al., 2024).
- That no paper combines calibrated or non-fixed-cutoff detection with a
  formal score-level consequence analysis in a mental-health symptom measure
  (Black et al., 2024; Nilsen et al., 2024; Zheng et al., 2024). Only the
  narrower combination — permutation-calibrated detection, window and
  clinical-vs-community comparisons, net/gross sum-score bias and validity
  robustness — survives (§6).
- That no short-window adaptation of the HiTOP-SR exists (Mostajabi et al.,
  2026, used a past-month window).
- That no published reanalysis shows ΔCFI/ΔRMSEA-based invariance conclusions
  reversing under exact or calibrated methods (Lasker, 2024; and, in the
  opposite direction, Cieciuch et al., 2014).
- That this study is the first empirical application of `permuteMeasEq` /
  permutation-tested invariance to ordinal symptom data (Kaplan-Kahn et al.,
  2024; Kildahl et al., 2026, configural only).
- That no paper performs global or combinatorial item selection for
  invariance (Schultze & Eid, 2018; Olaru et al., 2019; Jankowsky et al.,
  2020; Olaru & Danner, 2021). Only the exhaustive-enumeration, "none exists"
  and greedy-lockout claims survive (§7).
- That Maassen et al. recommend preregistering invariance tests (their
  Discussion does not; their own study was preregistered).

---

## 12. Before submission

1. Apply McNeish (2026) dynamic cutoffs and/or Savalei et al. (2023) RMSEA_D
   to the 20 × 3 conventional-criteria screen, using the scaled difference
   statistic from `lavTestLRT` (add to `NB_conventional_criteria.ipynb`). This
   is more pressing now: Maassen et al. point readers to dynamic cutoffs, and
   Lasker (2024) used RMSEA_D to reverse a ΔRMSEA verdict.
2. *Done 2026-10-01, re-run at submission.* Citing-literature checks were run
   (contradiction report): OpenAlex for Jorgensen 2018, Kite 2018, Watson 2022,
   Simms 2022, Nye & Drasgow 2011, Nye 2019, Gonzalez & Pelham 2021, Kopf 2015,
   Woods 2009 and Lamela 2020; Semantic Scholar for McNeish 2026 (11 citing),
   Savalei 2023 (79, via its preprint record), Kang 2016, Joo & Kim 2019 and
   the partial-invariance search papers. OpenAlex's free daily budget ran out
   mid-run, so re-run the large walks (Chen 2007; Asparouhov & Muthén 2014;
   Savalei 2023 by its APA DOI) in OpenAlex at submission. The HiTOP-SR
   check found the past-month administration (Mostajabi et al., 2026); re-check
   for any two-week or invariance-tested version.
3. *Done 2026-10-01.* The within-study criterion-comparison search found
   nothing (§5.4); the reanalysis search found Lasker (2024) (§9).
4. *Done 2026-10-01.* Maassen et al.'s recommendations are summarized in §9.
5. Read the full text of Kuharic et al. (2026) to confirm the design
   (within-person recall formats? strata pooled for DIF?) before citing it as
   a parallel-strata precedent; it was verified at abstract level only.
6. Decide how to handle the §11 Doi et al. (2018) PHQ-9 entry (see the note
   there) and cite the *PLOS ONE* PHQ-9 paper by its own DOI.
7. Watch for a preprint of Cole's (2026) trifactor study of momentary vs
   daily- and weekly-retrospective emotion ratings (talk abstract only; its
   invariance method is unknown), and for further replies in the
   Lasker–Protzko exchange.

---

## 13. References

- Abulela, M. A. A., Nickodem, K., & Rodriguez, M. C. (2024). *Journal of
  Psychoeducational Assessment*, 43(2), 178–198.
  https://doi.org/10.1177/07342829241302238
- Andrade, E., & Rodríguez, D. (2018). *PLOS ONE*, 13(10), e0205892.
  https://doi.org/10.1371/journal.pone.0205892
- Asparouhov, T., & Muthén, B. (2014). Multiple-group factor analysis
  alignment. *Structural Equation Modeling*, 21(4), 495–508.
  https://doi.org/10.1080/10705511.2014.919210
- Belzak, W. C. M., & Bauer, D. J. (2020). Improving the assessment of
  measurement invariance: Using regularization to select anchor items and
  identify differential item functioning. *Psychological Methods*, 25(6),
  673–690. https://doi.org/10.1037/met0000253
- Beribisky, N., & Hancock, G. R. (2024). *Educational and Psychological
  Measurement*, 84(4), 716–735. https://doi.org/10.1177/00131644231202949
- Black, L., Humphrey, N., Panayiotou, M., & Marquez, J. (2024; online 2023).
  Mental health and well-being measures for mean comparison and screening in
  adolescents: An assessment of unidimensionality and sex and age measurement
  invariance. *Assessment*, 31(2), 219–236.
  https://doi.org/10.1177/10731911231158623
- Blake, J. J., Munyombwe, T., Fischer, F., Quinn, T. J., Van der
  Feltz-Cornelis, C. M., et al. (2025). The factor structure of the Patient
  Health Questionnaire-9 in stroke: A comparison with a non-stroke population.
  *Journal of Psychosomatic Research*, 188, 111983.
  https://doi.org/10.1016/j.jpsychores.2024.111983
- Briers, N., Sanders, M. R., Northam, J. C., Dadds, M. R., & Hawes, D. J.
  (2026). *Psychological Assessment*. https://doi.org/10.1037/pas0001498
- Buchanan, E. M. (2025; online 2024). Visualizemi: Visualization, effect
  size, and replication of measurement invariance for registered reports.
  *Assessment*, 32(2), 190–205. https://doi.org/10.1177/10731911241280763
- Cao, C., & Liang, X. (2024; online 2023). The impact of ignoring
  cross-loadings on the sensitivity of fit measures in measurement invariance
  testing. *Structural Equation Modeling*, 31(1), 64–80.
  https://doi.org/10.1080/10705511.2023.2223360
- Chen, F. F. (2007). Sensitivity of goodness of fit indexes to lack of
  measurement invariance. *Structural Equation Modeling*, 14(3), 464–504.
  https://doi.org/10.1080/10705510701301834
- Chen, P.-Y., & Chao, T.-Y. (2026). A comparison of methods for testing
  measurement invariance with unbalanced data. *Structural Equation
  Modeling*, 33(3), 404–411. https://doi.org/10.1080/10705511.2025.2591420
- Cheung, G. W., & Rensvold, R. B. (2002). Evaluating goodness-of-fit indexes
  for testing measurement invariance. *Structural Equation Modeling*, 9(2),
  233–255. https://doi.org/10.1207/s15328007sem0902_5
- Chilver, M. R., Burns, R. A., Botha, F., & Butterworth, P. (2023). *PLOS
  ONE*, 18(12), e0295535. https://doi.org/10.1371/journal.pone.0295535
- Cieciuch, J., Davidov, E., Schmidt, P., Algesheimer, R., & Schwartz, S. H.
  (2014). Comparing results of an exact vs. an approximate (Bayesian)
  measurement invariance test: A cross-country illustration with a scale to
  measure 19 human values. *Frontiers in Psychology*, 5, 982.
  https://doi.org/10.3389/fpsyg.2014.00982
- Condon, D. M., Chapman, R., Shaunfield, S., Kallen, M. A., Beaumont, J. L.,
  et al. (2020; online 2019). Does recall period matter? Comparing PROMIS®
  physical function with no recall, 24-hr recall, and 7-day recall. *Quality
  of Life Research*, 29(3), 745–753.
  https://doi.org/10.1007/s11136-019-02344-0
- Contractor, A. A., Caldas, S. V., Dolan, M., Natesan, P., & Weiss, N. H.
  (2019). Invariance of the construct of posttraumatic stress disorder: A
  systematic review. *Journal of Traumatic Stress*, 32(2), 287–298.
  https://doi.org/10.1002/jts.22389
- Czerwiński, S. K., & Atroszko, P. A. (2023; online 2021). A solution for
  factorial validity testing of three-item scales. *Current Psychology*.
  https://doi.org/10.1007/s12144-021-01554-5
- De La Rosa, J. S., Chism, G. T., Herder, K. E., Mun, C. J., & Aaron, R. V.
  (2026). Do somatic symptoms bias depression screening? Reliability and
  equivalence of PHQ-8 in those with and without chronic pain. *Journal of
  Affective Disorders*, 405, 121496.
  https://doi.org/10.1016/j.jad.2026.121496
- De Los Reyes, A., Oswald, F. L., Racz, S. J., Pina, A., McLeod, B. D., Wang,
  M., & Charamut, N. R. (2025). Editorial: Fairness, validity, and
  transparency in what researchers assume when testing for measurement
  invariance. *Journal of Clinical Child & Adolescent Psychology*, 54(3),
  299–317. https://doi.org/10.1080/15374416.2025.2484813
- Doi, S., Ito, M., Takebayashi, Y., Muramatsu, K., & Horikoshi, M. (2018).
  Factorial validity and invariance of the Patient Health Questionnaire
  (PHQ)-9 among clinical and non-clinical populations. *PLOS ONE*, 13(7),
  e0199235. https://doi.org/10.1371/journal.pone.0199235
- Doi, S., Ito, M., Takebayashi, Y., Muramatsu, K., & Horikoshi, M. (2018).
  [GAD-7 paper] *Frontiers in Psychology*, 9, 1741. https://doi.org/10.3389/fpsyg.2018.01741
- D'Urso, E. D., De Roover, K., Vermunt, J. K., & Tijmstra, J. (2022).
  *Behavior Research Methods*, 54, 2114–2145.
  https://doi.org/10.3758/s13428-021-01690-7
- Flake, J. K., & Fried, E. I. (2020). Measurement schmeasurement. *Advances in
  Methods and Practices in Psychological Science*, 3(4), 456–465.
  https://doi.org/10.1177/2515245920952393
- Florean, I. S., Dobrean, A., Balazsi, R., Roșan, A., Păsărelu, C. R.,
  Predescu, E., & Rad, F. (2022/2023). *Assessment*, 30(3).
  https://doi.org/10.1177/10731911211068178
- Flores-Kanter, P. E., & Alvarado, J. M. (2024). The state of open science
  practices in psychometric studies of suicide: A systematic review.
  *Assessment*, 31(8), 1567–1579. https://doi.org/10.1177/10731911241236315
- Gonzalez, O., & Pelham, W. E. (2021). When does differential item functioning
  matter for screening? *Assessment*, 28(2), 446–456.
  https://doi.org/10.1177/1073191120913618
- Goretzko, D., Siemund, K., & Sterner, P. (2024). *Educational and
  Psychological Measurement*, 84(1), 123–144.
  https://doi.org/10.1177/00131644231163813
- Groskurth, K., Bluemke, M., & Lechner, C. M. (2023/2024). Why we need to
  abandon fixed cutoffs for goodness-of-fit indices. *Behavior Research
  Methods*, 56(4), 3891–3914. https://doi.org/10.3758/s13428-023-02193-3
- HiTOP-BR validation (2026). *Journal of Personality Assessment*.
  https://doi.org/10.1080/00223891.2026.2655185
- Hu, L., & Bentler, P. M. (1999). *Structural Equation Modeling*, 6(1), 1–55.
  https://doi.org/10.1080/10705519909540118
- Hussey, I., & Hughes, S. (2020). Hidden invalidity among 15 commonly used
  measures in social and personality psychology. *AMPPS*, 3(2), 166–184.
  https://doi.org/10.1177/2515245919882903
- Jankowsky, K., Olaru, G., & Schroeders, U. (2020). Compiling measurement
  invariant short scales in cross-cultural personality assessment using ant
  colony optimization. *European Journal of Personality*, 34(3), 470–485.
  https://doi.org/10.1002/per.2260
- Joo, S.-H., & Kim, E. S. (2019). *Behavior Research Methods*, 51, 2688–2699.
  https://doi.org/10.3758/s13428-018-1124-6
- Jorgensen, T. D., Kite, B. A., Chen, P.-Y., & Short, S. D. (2018).
  Permutation randomization methods for testing measurement equivalence.
  *Psychological Methods*, 23(4), 708–728. https://doi.org/10.1037/met0000152
- Jung, E., & Yoon, M. (2016). *Structural Equation Modeling*, 23(4), 567–584.
  https://doi.org/10.1080/10705511.2015.1138092
- Kang, Y., McNeish, D. M., & Hancock, G. R. (2016). *Educational and
  Psychological Measurement*, 76(4), 533–561.
  https://doi.org/10.1177/0013164415603764
- Kaplan-Kahn, E. A., Benecke, R. M., Guthrie, W., Yerys, B. E., Holmes,
  L. G., & Miller, J. S. (2024). Measurement invariance of the PROMIS
  emotional distress and subjective well-being domains among autistic and
  general population adolescents. *Quality of Life Research*, 33(11),
  3003–3012. https://doi.org/10.1007/s11136-024-03742-9
- Kenny, D. A., Kaniskan, B., & McCoach, D. B. (2015). The performance of
  RMSEA in models with small degrees of freedom. *Sociological Methods &
  Research*, 44(3), 486–507. https://doi.org/10.1177/0049124114543236
- Kildahl, A. N., Hellerud, J. M. A., Halvorsen, M. B., & Helverschou, S. B.
  (2026; online 2025). The Aberrant Behavior Checklist in a clinical sample of
  autistic individuals with intellectual disabilities and co-occurring mental
  health problems: Psychometric properties, factor structure, and
  longitudinal measurement invariance. *Journal of Autism and Developmental
  Disorders*, 56(5), 1980–1998. https://doi.org/10.1007/s10803-024-06697-5
- Kite, B. A., Jorgensen, T. D., & Chen, P.-Y. (2018). *Structural Equation
  Modeling*, 25(2), 251–260. https://doi.org/10.1080/10705511.2017.1421467
- Kolbe, L., & Jorgensen, T. D. (2019). *Behavior Research Methods*, 51(1),
  138–151. https://doi.org/10.3758/s13428-018-1151-3
- Kopf, J., Zeileis, A., & Strobl, C. (2015). *Educational and Psychological
  Measurement*, 75(1), 22–56. https://doi.org/10.1177/0013164414529792
- Kuharic, M., Cella, D., Shaunfield, S., Kallen, M. A., Hurt, C. N., Shaw,
  J. W., Chapman, R., & Peipert, J. D. (2026). Reliability, validity, and
  measurement invariance of 7-day recall and no-recall versions of the
  PROMIS® Short Form v2.0 – Physical Function 8c. *Advances in
  Patient-Reported Outcomes*, 2(3), 100186.
  https://doi.org/10.1016/j.apro.2025.100186
- Lai, J.-S., Cook, K., Stone, A., Beaumont, J., & Cella, D. (2009).
  Classical test theory and item response theory/Rasch model to assess
  differences between patient-reported fatigue using 7-day and 4-week recall
  periods. *Journal of Clinical Epidemiology*, 62(9), 991–997.
  https://doi.org/10.1016/j.jclinepi.2008.10.007
- Lamela, D., Soreira, C., Matos, P., & Morais, A. (2020). *Journal of
  Affective Disorders*, 276, 220–233.
  https://doi.org/10.1016/j.jad.2020.06.066
- Lasker, J. (2024). Measurement invariance testing works. *Applied
  Psychological Measurement*, 48(6), 257–275.
  https://doi.org/10.1177/01466216241261708
- Lee, H. C., & Chmielewski, M. (2026). Measurement invariance of
  hierarchical taxonomy of psychopathology across sociodemographic
  covariates: A moderated nonlinear factor analysis approach. *Journal of
  Psychopathology and Clinical Science*, 135(3), 446–460.
  https://doi.org/10.1037/abn0001114
- Lee, S., Kang, S., Kang, J.-H., & Lee, S. (2023). *Frontiers in Psychology*,
  14, 1217038. https://doi.org/10.3389/fpsyg.2023.1217038
- Li, Y., He, S., Waldman, I. D., & Rodriguez-Seijas, C. (2025). *Assessment*.
  https://doi.org/10.1177/10731911251391567
- Luong, R., & Flake, J. K. (2022). *Psychological Methods*.
  https://doi.org/10.1037/met0000441
- Maassen, E., D'Urso, E. D., van Assen, M. A. L. M., Nuijten, M. B., De
  Roover, K., & Wicherts, J. M. (2023 online; 2025). The dire disregard of
  measurement invariance testing in psychological science. *Psychological
  Methods*, 30(5), 966–979. https://doi.org/10.1037/met0000624
- MacCallum, R. C. (1986). Specification searches in covariance structure
  modeling. *Psychological Bulletin*, 100(1), 107–120.
  https://doi.org/10.1037/0033-2909.100.1.107
- MacCallum, R. C., Roznowski, M., & Necowitz, L. B. (1992). *Psychological
  Bulletin*, 111(3), 490–504. https://doi.org/10.1037/0033-2909.111.3.490
- Markon, K. E., & Olino, T. (2025). From confirmation to theory:
  Introduction to the special section on "Assessment, Measurement, and
  Registered Replication." *Assessment*, 32(2), 167–169.
  https://doi.org/10.1177/10731911251320053
- McNeish, D. (2026). Dynamic measurement invariance cutoffs for two-group fit
  index differences. *Psychological Methods*, 31(1), 136–157.
  https://doi.org/10.1037/met0000767
- McNeish, D., & Wolf, M. G. (2023). Dynamic fit index cutoffs for
  confirmatory factor analysis models. *Psychological Methods*, 28(1), 61–88.
  https://doi.org/10.1037/met0000425
- Meade, A. W., Johnson, E. C., & Braddy, P. W. (2008). *Journal of Applied
  Psychology*, 93(3), 568–592. https://doi.org/10.1037/0021-9010.93.3.568
- Mostajabi, J., Vize, C. E., Nielsen, S. R., Ringwald, W. R., & Wright,
  A. G. C. (2026). Structure of current psychopathology and its associations
  with daily life experiences using the Hierarchical Taxonomy of
  Psychopathology Self-Report (HiTOP-SR) in a mixed clinical/community sample.
  *Psychological Assessment*, 38(6–7), 451–465.
  https://doi.org/10.1037/pas0001455
- Neufeld, S. A. S., St Clair, M., Brodbeck, J., Wilkinson, P. O., Goodyer,
  I. M., & Jones, P. B. (2023/2024). *Assessment*, 31(4).
  https://doi.org/10.1177/10731911231182687
- Nilsen, S. A., Stormark, K. M., Bang, L., Brunborg, G. S., Larsen, M., &
  Breivik, K. (2024). Time trends in adolescent depressive symptoms from 2010
  to 2019 in Norway: Real increase or artifacts of measurements?
  *Psychological Medicine*, 54(14), 3949–3961.
  https://doi.org/10.1017/s0033291724002447
- Nye, C. D., Bradburn, J., Olenick, J., Bialko, C., & Drasgow, F. (2019;
  online 2018). How big are my effects? *Organizational Research Methods*,
  22(3), 678–709. https://doi.org/10.1177/1094428118761122
- Ock, J., McAbee, S. T., Mulfinger, E., & Oswald, F. L. (2020; online 2019).
  The practical effects of measurement invariance. *Assessment*, 27(4),
  657–674. https://doi.org/10.1177/1073191119885018
- Olaru, G., & Danner, D. (2021; online 2020). Developing cross-cultural short
  scales using ant colony optimization. *Assessment*, 28(1), 199–210.
  https://doi.org/10.1177/1073191120918026
- Olaru, G., Wilhelm, O., Nordin, S., Witthöft, M., & Köteles, F. (2019).
  Modern health worries: Deriving two measurement invariant short scales for
  cross-cultural research with Ant Colony Optimization. *PLOS ONE*, 14(2),
  e0211819. https://doi.org/10.1371/journal.pone.0211819
- Oliveira, S. E. S., Krueger, R. F., Corrêa, F. M., Corrêa, D. R. C., &
  Faiad, C. (2026). Hierarchical taxonomy of psychopathology – Brazilian Brief
  Scale (HiTOP-BBS): Initial evidence of reliability and validity.
  *Personality and Individual Differences*, 262, 113960.
  https://doi.org/10.1016/j.paid.2026.113960
- Protzko, J. (2025; online 2024). Invariance: What does measurement
  invariance allow us to claim? *Educational and Psychological Measurement*,
  85(3), 458–482. https://doi.org/10.1177/00131644241282982
- Putnick, D. L., & Bornstein, M. H. (2016). *Developmental Review*, 41, 71–90.
  https://doi.org/10.1016/j.dr.2016.06.004
- Rawers, N., Mangiarulo, M., Shevlin, M., & McElroy, E. (2024). Is time of the
  essence? *Translational Issues in Psychological Science*, 10(3), 251–261.
  https://doi.org/10.1037/tps0000420
- Ringwald, W. R., Forbes, M. K., & Wright, A. G. C. (2022). Meta-analytic
  tests of measurement invariance of internalizing and externalizing
  psychopathology across common methodological characteristics. *Journal of
  Psychopathology and Clinical Science*, 131(8), 847–856.
  https://doi.org/10.1037/abn0000785
- Rios, J. A. (2021). Is differential noneffortful responding associated with
  Type I error in measurement invariance testing? *Educational and
  Psychological Measurement*, 81(5), 957–979.
  https://doi.org/10.1177/0013164421990429
- Rohlfs, I. C. P. M., Noce, F., Gabbett, T. J., Wilke, C., Vido, M., Terry,
  V. R., & Terry, P. C. (2023). Psychometric characteristics of the Brazil
  Mood Scale among youth and elite athletes using two response time frames.
  *Sports*, 11(12), 244. https://doi.org/10.3390/sports11120244
- Samuel, D. B. (2019). Incoming editorial. *Assessment*.
  https://doi.org/10.1177/1073191118822760
- Sass, D. A., Schmitt, T. A., & Marsh, H. W. (2014). *Structural Equation
  Modeling*, 21(2), 167–180. https://doi.org/10.1080/10705511.2014.882658
- Savalei, V., Brace, J. C., & Fouladi, R. T. (2023/2024). We need to change
  how we compute RMSEA for nested model comparisons. *Psychological Methods*,
  29(3), 480–493. https://doi.org/10.1037/met0000537
- Schneider, S., Choi, S. W., Junghaenel, D. U., Schwartz, J. E., & Stone,
  A. A. (2013). *Quality of Life Research*, 22, 1859–1869.
  https://doi.org/10.1007/s11136-012-0323-3
- Schroeders, U., & Gnambs, T. (2020; online 2018). Degrees of freedom in
  multigroup confirmatory factor analyses. *European Journal of Psychological
  Assessment*, 36(1), 105–113. https://doi.org/10.1027/1015-5759/a000500
- Schroeders, U., Wilhelm, O., & Olaru, G. (2016). Meta-heuristics in short
  scale construction: Ant colony optimization and genetic algorithm. *PLOS
  ONE*, 11(11), e0167110. https://doi.org/10.1371/journal.pone.0167110
- Schultze, M., & Eid, M. (2018). Identifying measurement invariant item sets
  in cross-cultural settings using an automated item selection procedure.
  *Methodology*, 14(4), 177–188. https://doi.org/10.1027/1614-2241/a000155
- Schulze, D., Reuter, B., & Pohl, S. (2022). Measurement invariance: Dealing
  with the uncertainty in anchor item choice by model averaging. *Structural
  Equation Modeling*, 29(4), 521–530.
  https://doi.org/10.1080/10705511.2021.2012785
- Simms, L. J., et al. (2022). Development of measures for the Hierarchical
  Taxonomy of Psychopathology (HiTOP). *Assessment*, 29(1), 3–16.
  https://doi.org/10.1177/10731911211015309
- Soland, J. (2021). Is measurement noninvariance a threat to inferences drawn
  from randomized control trials? *Applied Psychological Measurement*, 45(5),
  346–360. https://doi.org/10.1177/01466216211013102
- Trummer, B. T. T., Wendt, L. P., Schroeders, U., & Zimmermann, J. (2026).
  Measurement invariance and sociodemographic differences at the lowest level
  of the psychopathology hierarchy: An analysis of the German HiTOP-SR
  [Preprint]. PsyArXiv. https://doi.org/10.31234/osf.io/t4ry2_v1
- Watson, D., Forbes, M. K., Levin-Aspenson, H. F., et al. (2022). The
  development of preliminary HiTOP internalizing spectrum scales.
  *Assessment*, 29(1), 17–33. https://doi.org/10.1177/10731911211003976
- Whittington, D. D., Borgogna, N. C., Jagdam, S., & Varshney, M. (2026).
  Measurement invariance of the PHQ-8 in a large sample of specialty care
  patients with HIV. *Journal of Affective Disorders*, 405, 121594.
  https://doi.org/10.1016/j.jad.2026.121594
- Woods, C. M. (2009). *Applied Psychological Measurement*, 33(1), 42–57.
  https://doi.org/10.1177/0146621607314044
- Wu, H., & Estabrook, R. (2016). Identification of confirmatory factor
  analysis models of different levels of invariance for ordered categorical
  outcomes. *Psychometrika*, 81, 1014–1045.
  https://doi.org/10.1007/s11336-016-9506-0
- Yoon, M., & Kim, E. S. (2014). *Behavior Research Methods*, 46(4),
  1199–1206. https://doi.org/10.3758/s13428-013-0430-2
- Yoon, M., & Millsap, R. E. (2007). *Structural Equation Modeling*, 14(3),
  435–463. https://doi.org/10.1080/10705510701301677
- Zheng, S., Mansolf, M., McGrath, M., Churchill, M. L., Bekelman, T. A., et
  al. (2024; online 2023). Measurement bias in caregiver-report of early
  childhood behavior problems across demographic factors in an ECHO-wide
  diverse sample. *JCPP Advances*, 4(1), e12198.
  https://doi.org/10.1002/jcv2.12198

Not DOI-resolved (cite by title/URL until verified): the HiTOP-SR
first-phase summary (Simms et al., "The HiTOP approach to assessment: Summary
of the first phase of the HiTOP self-report measure development project").
