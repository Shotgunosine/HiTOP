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
"no prior paper does X" are *absence from the verified set*, not proof of
absence — re-check them at submission; (2) several abstracts were verified via
indexing services because publisher pages were blocked, so condition-level
details inside paywalled papers were not always confirmed. Every DOI below was
resolved through Crossref on 2026-10-01.

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
  days) within subjects and found no substantive effect; a 2025 PROMIS Physical
  Function FDA-qualification study found no meaningful DIF between no-recall
  and seven-day versions. Both are nulls under conventional methods.

**What the manuscript can claim.** The window question is *rarely tested*, not
untested. The novelty is the design and the rigor: a parallel-strata design
with the original validation sample as a third group, calibrated permutation
tests, an exhaustive subset search, and a consequence analysis — none of which
the prior window studies have. The intro should cite Schneider → Andrade &
Rodríguez → Rawers in that order.

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

**What the manuscript can claim.** No verified paper reports a *configural*
failure for PHQ-8/9 or GAD-7 between general-population and clinical strata;
the manuscript's PHQ-8 result stands as an apparent first (with the
absence-of-evidence caveat). Scalar-level failures at this boundary are
documented (Doi et al.) and should be cited as precedent.

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
mislocalization result can be claimed as an applied first, cautiously.

### 5.4 What applied comparisons exist

Only one applied head-to-head of conventional criteria against RMSEA_D was
found (Abulela, Nickodem & Rodriguez, 2024, five social-emotional measures,
n ≈ 626,000): the two agreed. There is no applied paper comparing criterion
sensitivity across comparison types against a calibrated benchmark, and no
paper arguing that subtle clinical-vs-community non-invariance is
systematically under-detected by ΔCFI.

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
are *larger* with unequal N — attribute it to violation magnitude.

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

**What the manuscript can claim.** No verified paper combines
sensitivity-calibrated detection with formal score-level consequence analysis
in a psychiatric symptom inventory. The arc is occupied piecewise, never end to
end. Both halves of the manuscript's paradox — the criteria are unreliable
*and* most of what they miss does not bias sum scores — now have literature
behind them.

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

**What the manuscript can claim.** No verified paper performs exhaustive
subset enumeration for invariance, proves that no invariant subset exists, or
demonstrates a greedy lockout on real data. Recommended wording: *a concrete
instance of the path-dependence long asserted for MI-guided searches, in a
regime (ordinal indicators, item removal, majority non-invariance, two groups)
that the simulations endorsing sequential search did not cover, and one where
alignment is not available.* Do not frame it as contradicting Yoon & Kim; it
realizes their own stated boundary condition.

---

## 8. Element F — the HiTOP measures and supersession risk

Watson et al. (2022) describe the scales as preliminary Phase-1 products with
an independent validation sample of 496 adults (the manuscript's third group).
Simms et al. (2022) state that "research applications and clinical translation
of the model require measures that are specifically keyed to the model" and
describe later phases. The scale developers consider the Phase-1 scales
superseded by Phase 2 and the HiTOP-SR; the HiTOP-SR uses a past-12-months
window, and the HiTOP-BR (2026) ran cross-population invariance under
conventional criteria with no window adaptation. The two-week-window niche is
therefore unoccupied, but a validation of superseded scales is not a compelling
deliverable in itself. The manuscript should treat the Phase-1 scales as a
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
  no *Assessment* editorial engaging it was verified.

**What the manuscript can claim.** The audit framing is available and not
preempted, **provided it is worded as an audit of decision criteria rather
than of practice prevalence**. Every exemplar audits how often invariance is
tested or whether scales pass, and every one adjudicates with the conventional
cutoffs the manuscript benchmarks; none audits clinical-vs-community
comparisons and none has a calibrated reference test. Suggested positioning:

> Prior audits show that invariance is rarely tested and that scales often fail
> when it is (Maassen et al.; Hussey & Hughes; Putnick & Bornstein), but those
> audits themselves adjudicate invariance with ΔCFI/ΔRMSEA heuristics whose
> sensitivity in clinical-vs-community comparisons is unknown (Neufeld et al.).
> We audit the criteria themselves against a calibrated benchmark.

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

Claims to state as apparent firsts (each with the absence-of-evidence caveat):
the between-strata configural failure of the PHQ-8; exhaustive proofs that no
invariant subset exists; the greedy lockout on real data; pair-dependent
criterion sensitivity against a permutation benchmark; level mislocalization
in applied data.

**Citation spine by manuscript section**

| Section | Cite |
|---|---|
| Intro: window changes | Schneider et al. 2013; Andrade & Rodríguez 2018; Rawers et al. 2024; Chilver et al. 2023 |
| Intro: clinical vs community | Doi et al. 2018; Lee et al. 2023; Briers et al. 2026; Florean et al. 2022 |
| Intro: HiTOP context | Watson et al. 2022; Simms et al. 2022; HiTOP-BR 2026 |
| Intro: audit positioning | Maassen et al. 2023/2025; Putnick & Bornstein 2016; Hussey & Hughes 2020; Goretzko et al. 2024; Neufeld et al. 2023 |
| Methods: identification and tests | Wu & Estabrook 2016; Jorgensen et al. 2018; Kite et al. 2018; Luong & Flake 2022 |
| Methods: conventional criteria | Hu & Bentler 1999; Cheung & Rensvold 2002; Chen 2007 |
| Methods: effect sizes | Nye et al. 2019; Gonzalez & Pelham 2021 |
| Results/Discussion: uncalibrated criteria | Kenny et al. 2015; Meade et al. 2008; Kang et al. 2016; Savalei et al. 2023; Beribisky & Hancock 2024; D'Urso et al. 2022; Groskurth et al. 2023; McNeish 2026; Czerwiński & Atroszko 2023; Abulela et al. 2024 |
| Discussion: level mislocalization | Chen 2007; Joo & Kim 2019 |
| Discussion: greedy lockout | Asparouhov & Muthén 2014; MacCallum 1986, 1992; Yoon & Millsap 2007; Yoon & Kim 2014; Jung & Yoon 2016; Woods 2009; Kopf et al. 2015; Kolbe & Jorgensen 2019 |
| Discussion: consequences | Gonzalez & Pelham 2021; Ock et al. 2020; Soland 2021; Schneider et al. 2013 |
| Discussion: foils (handle diplomatically) | Li et al. 2025; Lee et al. 2023; HiTOP-BR 2026; Lamela et al. 2020 |

---

## 11. Claims that were refuted — do not use

- That Chen (2007) found unequal group sizes *shrink* ΔAFIs (she found the
  opposite), so unequal N cannot explain the lower population-strata
  sensitivity.
- That the ΔRMSEA small-model artifact is an *analytic* df-scaling effect
  rather than a sampling effect.
- That Lamela et al. (2020) show "0 of 10 PHQ-9 studies found a violation."
- A specific Doi et al. (2018) PHQ-9 clinical-vs-non-clinical ΔCFI-only example
  (the GAD-7 result in §4 is verified; this PHQ-9 gloss is not).
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

---

## 12. Before submission

1. Apply McNeish (2026) dynamic cutoffs and/or Savalei et al. (2023) RMSEA_D
   to the 20 × 3 conventional-criteria screen, using the scaled difference
   statistic from `lavTestLRT` (add to `NB_conventional_criteria.ipynb`).
2. Re-run a citing-literature check on McNeish (2026), Savalei et al. (2023)
   and Maassen et al. (2023) — this literature is moving month to month — and
   re-check the HiTOP-SR/HiTOP-PRO outputs for any short-window adaptation.
3. Run one targeted search for a within-study comparison of criterion
   performance across grouping variables, and for any reanalysis showing
   published invariance claims reversing under permutation, alignment, DMI or
   RMSEA_D; the current "first" claims rest on absence from unfinished
   searches.
4. Pull Maassen et al.'s explicit recommendations from their Discussion (not
   captured by any verified claim).

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
- Beribisky, N., & Hancock, G. R. (2024). *Educational and Psychological
  Measurement*, 84(4), 716–735. https://doi.org/10.1177/00131644231202949
- Briers, N., Sanders, M. R., Northam, J. C., Dadds, M. R., & Hawes, D. J.
  (2026). *Psychological Assessment*. https://doi.org/10.1037/pas0001498
- Chen, F. F. (2007). Sensitivity of goodness of fit indexes to lack of
  measurement invariance. *Structural Equation Modeling*, 14(3), 464–504.
  https://doi.org/10.1080/10705510701301834
- Cheung, G. W., & Rensvold, R. B. (2002). Evaluating goodness-of-fit indexes
  for testing measurement invariance. *Structural Equation Modeling*, 9(2),
  233–255. https://doi.org/10.1207/s15328007sem0902_5
- Chilver, M. R., Burns, R. A., Botha, F., & Butterworth, P. (2023). *PLOS
  ONE*, 18(12), e0295535. https://doi.org/10.1371/journal.pone.0295535
- Czerwiński, S. K., & Atroszko, P. A. (2023; online 2021). A solution for
  factorial validity testing of three-item scales. *Current Psychology*.
  https://doi.org/10.1007/s12144-021-01554-5
- Doi, S., Ito, M., Takebayashi, Y., Muramatsu, K., & Horikoshi, M. (2018).
  *Frontiers in Psychology*, 9, 1741. https://doi.org/10.3389/fpsyg.2018.01741
- D'Urso, E. D., De Roover, K., Vermunt, J. K., & Tijmstra, J. (2022).
  *Behavior Research Methods*, 54, 2114–2145.
  https://doi.org/10.3758/s13428-021-01690-7
- Flake, J. K., & Fried, E. I. (2020). Measurement schmeasurement. *Advances in
  Methods and Practices in Psychological Science*, 3(4), 456–465.
  https://doi.org/10.1177/2515245920952393
- Florean, I. S., Dobrean, A., Balazsi, R., Roșan, A., Păsărelu, C. R.,
  Predescu, E., & Rad, F. (2022/2023). *Assessment*, 30(3).
  https://doi.org/10.1177/10731911211068178
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
- Kenny, D. A., Kaniskan, B., & McCoach, D. B. (2015). The performance of
  RMSEA in models with small degrees of freedom. *Sociological Methods &
  Research*, 44(3), 486–507. https://doi.org/10.1177/0049124114543236
- Kite, B. A., Jorgensen, T. D., & Chen, P.-Y. (2018). *Structural Equation
  Modeling*, 25(2), 251–260. https://doi.org/10.1080/10705511.2017.1421467
- Kolbe, L., & Jorgensen, T. D. (2019). *Behavior Research Methods*, 51(1),
  138–151. https://doi.org/10.3758/s13428-018-1151-3
- Kopf, J., Zeileis, A., & Strobl, C. (2015). *Educational and Psychological
  Measurement*, 75(1), 22–56. https://doi.org/10.1177/0013164414529792
- Lamela, D., Soreira, C., Matos, P., & Morais, A. (2020). *Journal of
  Affective Disorders*, 276, 220–233.
  https://doi.org/10.1016/j.jad.2020.06.066
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
- McNeish, D. (2026). Dynamic measurement invariance cutoffs for two-group fit
  index differences. *Psychological Methods*, 31(1), 136–157.
  https://doi.org/10.1037/met0000767
- Meade, A. W., Johnson, E. C., & Braddy, P. W. (2008). *Journal of Applied
  Psychology*, 93(3), 568–592. https://doi.org/10.1037/0021-9010.93.3.568
- Neufeld, S. A. S., St Clair, M., Brodbeck, J., Wilkinson, P. O., Goodyer,
  I. M., & Jones, P. B. (2023/2024). *Assessment*, 31(4).
  https://doi.org/10.1177/10731911231182687
- Nye, C. D., Bradburn, J., Olenick, J., Bialko, C., & Drasgow, F. (2019;
  online 2018). How big are my effects? *Organizational Research Methods*,
  22(3), 678–709. https://doi.org/10.1177/1094428118761122
- Ock, J., McAbee, S. T., Mulfinger, E., & Oswald, F. L. (2020; online 2019).
  The practical effects of measurement invariance. *Assessment*, 27(4),
  657–674. https://doi.org/10.1177/1073191119885018
- Putnick, D. L., & Bornstein, M. H. (2016). *Developmental Review*, 41, 71–90.
  https://doi.org/10.1016/j.dr.2016.06.004
- Rawers, N., Mangiarulo, M., Shevlin, M., & McElroy, E. (2024). Is time of the
  essence? *Translational Issues in Psychological Science*, 10(3), 251–261.
  https://doi.org/10.1037/tps0000420
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
- Simms, L. J., et al. (2022). Development of measures for the Hierarchical
  Taxonomy of Psychopathology (HiTOP). *Assessment*, 29(1), 3–16.
  https://doi.org/10.1177/10731911211015309
- Soland, J. (2021). Is measurement noninvariance a threat to inferences drawn
  from randomized control trials? *Applied Psychological Measurement*, 45(5),
  346–360. https://doi.org/10.1177/01466216211013102
- Watson, D., Forbes, M. K., Levin-Aspenson, H. F., et al. (2022). The
  development of preliminary HiTOP internalizing spectrum scales.
  *Assessment*, 29(1), 17–33. https://doi.org/10.1177/10731911211003976
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

Not DOI-resolved (cite by title/URL until verified): the 2025 PROMIS Physical
Function 8c recall-period FDA-qualification study (*Advances in
Patient-Reported Outcomes*, ScienceDirect PII S3050696425001855); the HiTOP-SR
first-phase summary (Simms et al., "The HiTOP approach to assessment: Summary
of the first phase of the HiTOP self-report measure development project").
