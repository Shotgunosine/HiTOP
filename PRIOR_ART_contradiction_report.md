# Contradiction searches for the novelty claims in `PRIOR_ART.md`

**Date:** 2026-10-01. **Brief:** `HANDOFF_prior_art_contradiction_searches.md`
(C1–C10). **Outcome:** `PRIOR_ART.md` sections 3–13 were revised to match
the verdicts below (same commit).

## Verdicts at a glance

| Claim | Short name | Verdict |
|---|---|---|
| C1 | Reporting-window invariance with calibrated tests, parallel strata, consequences | **WEAKENED** |
| C2 | Configural failure of PHQ-8/9 or GAD-7 between clinical and community strata | **STANDS** |
| C3 | End-to-end calibrated detection + score-level consequences | **CONTRADICTED** |
| C4 | HiTOP-SR/PRO short-window versions or cross-population invariance | **CONTRADICTED** for (a) short window; (b) and (c) **STAND** |
| C5 | Exhaustive subsets, "no invariant subset exists" proofs, greedy lockout | **WEAKENED** |
| C6 | Within-study ΔAFI sensitivity across comparison types; under-detection argument | **STANDS** |
| C7 | Empirical level mislocalization | **STANDS** |
| C8 | Reanalyses reversing ΔCFI verdicts; clinical-journal practice reviews; *Assessment* editorials | **CONTRADICTED** for (1) reanalysis; (2) and (3) **STAND** |
| C9 | Prior applied use of `permuteMeasEq` on ordinal symptom data | **CONTRADICTED**: prior applications exist |
| C10 | Maassen et al.'s explicit recommendations | **RETRIEVED** |

## How the searches were run, and their limits

- **Direct searches (C2–C7, C9, C10)** used the following sources:
  - OpenAlex cited-by walks and keyword searches.
  - Semantic Scholar cited-by lists, with abstracts.
  - PubMed E-utilities.
  - Europe PMC full-text search and full-text XML, with NCBI PMC `efetch` as
    a fallback.
  - The OSF API, to download PsyArXiv/OSF preprints.
  - Crossref, for DOI resolution, reference lists, and a sweep of
    *Assessment* items from 2019 to 2026.
- **Two `/deep-research` runs (C1, C8)**, as the handoff prescribed: run
  `wf_67a0d21e-0da` (99 agents) and run `wf_8af9e1d1-60f` (101 agents).
  Their candidates were treated as leads. Every counterexample used below was
  re-read at source in this session, unless it is explicitly marked as
  workflow-verified.
- **Budget limits that shape the "nothing found" statements.**
  - The session's 200-call WebSearch budget was used up by the two workflow
    runs. My own searches therefore went through the scholarly APIs above,
    not general web search.
  - OpenAlex's free daily budget for list queries ran out partway through C5.
    That budget is shared across the NIH network IP and resets at midnight
    UTC. The remaining cited-by walks used Semantic Scholar, which indexes
    fewer citations (Asparouhov & Muthén 2014: 78 citing works in S2 vs 804
    in OpenAlex).
  - Google Scholar was not used.
- **What "verified" means.** "Full text" means I read the quoted passage in a
  PMC copy, an OA copy, or a preprint (the copy is named). "Abstract" means
  only the abstract was read. "Nothing found" means nothing turned up in the
  searches listed for that claim. It is not proof of absence.
- **TLS.** NIH's network re-signs HTTPS traffic. Requests were verified
  against the NIH root certificate, exported from the macOS System keychain;
  verification was not disabled.

---

### C1  Reporting-window invariance with calibrated tests, parallel strata, and consequence analysis

**Verdict: WEAKENED.** The window question has more separate-sample and
parallel-strata precedent than §3 credited. Two prior window studies ran
cancer and general-population strata side by side. Nothing found uses a
calibrated test or a dMACS/expected-score consequence analysis across
windows. Nothing found runs a separate-sample window-invariance test on a
psychiatric inventory, apart from Rawers et al. 2024, which is already cited.

**Searches run:**
- `/deep-research` run `wf_67a0d21e-0da`, scoped adversarially. It covered
  five angles: PROMIS/ePRO recall-period DIF; affect/mood time instructions;
  depression/anxiety inventory time frames; data harmonization; and
  survey-methodology reference-period experiments. It fetched 17 sources and
  extracted 84 claims; 23 claims were confirmed 3-0 or 2-1 and 2 were killed.
- Re-verification of its counterexamples in Europe PMC / NCBI PMC full text.
- Crossref, PubMed and OpenAlex lookups of the not-yet-resolved PROMIS PF8c
  study.
- Cross-checks with the C2/C4 searches, which surfaced Ringwald et al. 2022
  and Mostajabi et al. 2026.

**Best candidates found:**

- **Condon, D. M., Chapman, R., Shaunfield, S., Kallen, M. A., Beaumont, J. L.,
  … Cella, D. (2020). Does recall period matter? Comparing PROMIS® physical
  function with no recall, 24-hr recall, and 7-day recall. *Quality of Life
  Research*, 29(3), 745–753. https://doi.org/10.1007/s11136-019-02344-0**
  - **Design.** 31 PROMIS PF v2.0 items, N = 2,400 (1,001 cancer, 1,399
    general population). Recall condition was randomized between persons. DIF
    was tested with lordif.
  - **Quote:** "We administered 31 items from the PROMIS Physical Function
    v2.0 item bank to 2400 respondents ( n = 1001 with cancer; n = 1399 from
    the general population). Respondents were randomly assigned to one of
    three recall conditions (no recall, 24-hours, or 7-days)…"
  - **Quote:** "We used a McFadden pseudo-R 2 change criterion of ≥ 0.02 to
    flag items for DIF and utilized the lordif R package"
  - **Quote:** "no items were flagged for the DIF factor recall time period"
  - **Quote:** "No Stage 2 DIF score impact studies were required."
  - **Quote:** "Analyses of variance (ANOVA) … were conducted separately in
    the cancer and general population samples."
  - **Verified at:** full text (PMC7199782).
  - **Why it partly preempts.** This is a separate-sample, randomized window
    comparison with parallel clinical and general-population strata. It
    planned a score-impact stage but never ran it. Its DIF test was
    conventional, run on the pooled sample, and applied to physical function
    rather than a psychiatric construct.

- **Kuharic, M., Cella, D., Shaunfield, S., Kallen, M. A., Hurt, C. N., Shaw,
  J. W., Chapman, R., & Peipert, J. D. (2026). Reliability, validity, and
  measurement invariance of 7-day recall and no-recall versions of the PROMIS®
  Short Form v2.0 – Physical Function 8c. *Advances in Patient-Reported
  Outcomes*, 2(3), 100186. https://doi.org/10.1016/j.apro.2025.100186**
  (PII S3050696425001855)
  - **Design.** N = 1,810 general population plus 300 with cancer. DIF by
    recall period and administration order.
  - **Quote:** "this secondary analysis included 1810 US adults from the
    general population and 300 adults with cancer … No significant DIF was
    detected due to recall period or administration order, with all McFadden
    Pseudo ΔR 2 values < 0.02"
  - **Verified at:** abstract (OpenAlex).
  - **Why it does not preempt.** It is the paper §3 already cites as "the
    2025 PROMIS PF8c FDA-qualification study", now DOI-resolved. It is
    another clinical-plus-general-population window study, using conventional
    DIF.

- **Lai, J.-S., Cook, K., Stone, A., Beaumont, J., & Cella, D. (2009).
  *Journal of Clinical Epidemiology*, 62(9), 991–997.
  https://doi.org/10.1016/j.jclinepi.2008.10.007**
  - **Design.** FACIT-F fatigue, 7-day vs 4-week windows, separate groups of
    cancer outpatients (100 vs 116). Assignment was not randomized.
  - **Quote:** "One was loaded with the Functional Assessment of Chronic
    Illness Therapy-Fatigue, FACIT-F, … using a 7-days time frame. The other
    was loaded with exactly the same questions, but with a 4-weeks time
    frame."
  - **Quote:** "DIF criterion: significant chi-square statistic, p < 0.01 …
    DIF criterion: t > 2.58, p < .01"
  - **Verified at:** full text (PMC2771583).
  - **Why it partly preempts.** It is an earlier separate-sample window DIF
    study, with conventional tests and a single clinical population.

- **Rohlfs, I. C. P. M., Noce, F., Gabbett, T. J., Wilke, C., Vido, M.,
  Terry, V. R., & Terry, P. C. (2023). *Sports*, 11(12), 244.
  https://doi.org/10.3390/sports11120244**
  - **Design.** BRAMS mood scale (depression, tension, fatigue and other
    subscales). "Right now" (n = 481) vs "past week" (n = 417), separate
    athlete samples.
  - **Quote:** "Respondents were in two groups according to the response time
    frame used to assess mood (i.e., "right now", or "past week")."
  - **Quote:** "The six-factor measurement model showed an acceptable fit …
    for both … response time frames independently, and in a multi-sample
    CFA."
  - **Verified at:** full text (PMC10747205). The reading that the
    multi-sample model was configural-only (df = 2 × single-group df) comes
    from the workflow verifier's reading of Table 3. Those table values are
    not in the XML text, so I could not re-check them.
  - **Why it does not preempt.** It is configural-only, with fixed cutoffs and
    no clinical stratum. It is the closest psychiatric-adjacent analogue of
    Andrade & Rodríguez 2018.

- **Ringwald, W. R., Forbes, M. K., & Wright, A. G. C. (2022). Meta-analytic
  tests of measurement invariance of internalizing and externalizing
  psychopathology across common methodological characteristics. *Journal of
  Psychopathology and Clinical Science*, 131(8), 847–856.
  https://doi.org/10.1037/abn0000785**
  - **Design.** Meta-analytic multigroup CFA of DSM-diagnosis correlation
    matrices: 47 samples, N = 118,966.
  - **Quote:** "Results supported partial or full invariance across (a)
    samples selected versus not selected for psychopathology, (b) diagnoses
    defined by binary DSM thresholds versus dimensional symptoms counts, and
    (c) diagnoses based on lifetime versus current symptoms."
  - **Verified at:** abstract (PubMed).
  - **Why it does not preempt.** It works at the level of diagnosis structure,
    not items. It is HiTOP-adjacent and worth citing as the
    lifetime-vs-current precedent.

- **Mostajabi et al. 2026** (see C4). Gave the HiTOP-SR with a past-month
  window and only speculated about the effect of the window. No test.

- **Neighbors with no invariance test across windows (workflow-verified, 3-0):**
  - Stone et al. 2016, *J Clin Epidemiol* 74:194–206,
    https://doi.org/10.1016/j.jclinepi.2015.08.029. Parallel community and
    four clinical strata, daily vs 7-day PROMIS; invariance was assumed.
  - Waller et al. 2016, OHIP, within-subject, no scalar step.
  - Peipert et al. 2022, PF8c, agreement statistics only.
  - Walentynowicz et al. 2018 and Lance & Griggs 2025, affect time frames,
    no invariance test.
  - Courtin et al. 2015, CES-D vs Euro-D; the instrument is confounded with
    the window.
  - Arizmendi et al. 2024, *Value in Health* 27(4):518–526,
    https://doi.org/10.1016/j.jval.2024.01.016. A systematic review of 30
    recall-period studies whose methods are agreement statistics.
  - Cole (2026), a talk abstract only: a trifactor model of momentary,
    daily-retrospective and weekly-retrospective mDES items. Within-person,
    with no test named. Watch for a preprint.

**Recommended change to `PRIOR_ART.md`.** §3, "What exists": add Condon
2020, Lai 2009, Rohlfs 2023 and Ringwald 2022, and replace the undated PF8c
mention with Kuharic et al. 2026. §3, "What the manuscript can claim":
replace with

> The window question is rarely tested, not untested, and the separate-sample
> design is not new: Lai et al. (2009) and Condon et al. (2020) gave identical
> items under different windows to separate groups, and Condon et al. (2020)
> and Kuharic et al. (2026) did so with clinical (cancer) and general-population
> strata. Every prior window study found used conventional criteria
> (lordif pseudo-R², ordinal logistic χ², Rasch t, fixed fit cutoffs,
> configural-only CFA) or no invariance test, and none reported dMACS,
> expected-score or sum-score bias tied to the detected non-invariance. What is
> new is the combination applied to a psychiatric symptom inventory: calibrated
> permutation tests at every Wu–Estabrook level, a three-group design with the
> instrument's original validation sample, an exhaustive subset search, and a
> score-level consequence analysis. Do not say the prior window studies lack a
> parallel-strata design.

**New entries for §11:**
- "The prior window studies have no parallel clinical/general-population
  strata." Refuted by Condon et al. 2020 and Kuharic et al. 2026.
- "No study has given identical items under different windows to separate
  samples and tested DIF." Refuted by Lai et al. 2009, Condon et al. 2020, and
  Rawers et al. 2024 (already cited).

---

### C2  A configural failure of PHQ-8/PHQ-9 or GAD-7 between general-population and clinical strata

**Verdict: STANDS.** Every comparison of PHQ-9, PHQ-8 or GAD-7 between a
clinical (psychiatric or medical) group and a community group passed
configural invariance.

**Searches run:**
- PubMed:
  - (PHQ-9 | PHQ-8 | "Patient Health Questionnaire") × (measurement
    invariance | factorial invariance | DIF | multigroup) × clinical terms:
    155 records scanned.
  - GAD-7 × the same invariance terms: 121 records.
  - (PHQ/GAD) × (factor structure | two-factor | bifactor | somatic) ×
    (community/general population AND psychiatric/clinical): 26 records.
- Europe PMC full text: (PHQ-9 | PHQ-8 | GAD-7) × configural-failure phrases.
  330 hits; the first 100 were scanned.
- Lamela et al. 2020 reference list via OpenAlex (89 references; every PHQ-9
  invariance study it reviewed was identified).
- Abstracts read for 15 candidates; full text read for Doi et al. 2018 (PLoS
  One).

**Best candidates found:**

- **Doi, S., Ito, M., Takebayashi, Y., Muramatsu, K., & Horikoshi, M.
  (2018). Factorial validity and invariance of the Patient Health
  Questionnaire (PHQ)-9 among clinical and non-clinical populations. *PLOS
  ONE*, 13(7), e0199235. https://doi.org/10.1371/journal.pone.0199235**
  - **Design.** Japanese adults: MDD (n = 406), MDD with anxiety disorder
    (n = 636), non-clinical (n = 1,163).
  - **Quote:** "The following criterion was used to adopting the model: a
    difference of less than .01 in the Δ CFI index supports the less
    parameterized model"
  - **Quote:** "for the non-clinical and only MDD groups … According to the
    criterion for adopting the model, Model 3 showed the best fit (scalar
    invariance)"
  - **Verified at:** full text (PMC6053131).
  - **Why it does not preempt.** Configural held: scalar invariance under a
    ΔCFI-only rule. It is a direct foil for the manuscript's PHQ-8 result.
    This is a different article from the GAD-7 paper (Frontiers) that §4
    cites; see Flag 1.

- **Blake, J. J., Munyombwe, T., Fischer, F., … Broomfield, N. M. (2025).
  *Journal of Psychosomatic Research*, 188, 111983.
  https://doi.org/10.1016/j.jpsychores.2024.111983**
  - **Design.** PHQ-9, stroke (787) vs propensity-matched non-stroke (1,574).
  - **Quote:** "Configural invariance between stroke and non-stroke was
    supported (CFI = 0.983, RMSEA = 0.080), as were invariant thresholds
    (p = .092) and loadings (p = .103). Strong invariance was violated …"
  - **Verified at:** abstract (PubMed).
  - **Why it does not preempt.** Configural held, and the sample is a medical
    one, not psychiatric.

- **Other neighbors in which configural held (abstracts, PubMed):**
  - Whittington, Borgogna, Jagdam & Varshney 2026, *JAD* 405:121594,
    https://doi.org/10.1016/j.jad.2026.121594. PHQ-8 in an HIV clinic
    (n = 3,696) vs a matched national sample: "support for scalar invariance
    across HIV status, but the measure fails residual invariance".
  - De La Rosa et al. 2026, *JAD* 405:121496,
    https://doi.org/10.1016/j.jad.2026.121496. PHQ-8 with vs without chronic
    pain (NHIS): invariant at configural, metric and scalar.
  - Chung et al. 2015, *QoL Res* 24(8):1829–1834,
    https://doi.org/10.1007/s11136-015-0927-5. PHQ-9 metric invariance
    between neurologic and community samples.
  - Nouwen et al. 2021, *JAD*. Diabetes vs no diabetes.
  - Ringwald et al. 2022 (see C1). Invariance held between samples selected
    and not selected for psychopathology, at the level of diagnoses.

**Recommended change to `PRIOR_ART.md`.** §4, "What exists": add Doi et al.
2018 (PLoS One) as a foil, with Blake 2025 and Whittington 2026 as medical
neighbors. §4, "What the manuscript can claim": replace with

> A contradiction search (2026-10-01; PubMed, Europe PMC full text, and the
> studies reviewed by Lamela et al., 2020) found no PHQ-8/9 or GAD-7 paper
> reporting a configural failure between general-population and clinical
> strata; every clinical- or medical-vs-community comparison found passed
> configural (e.g., PHQ-9 non-clinical vs MDD reached scalar under a ΔCFI < .01
> rule, Doi et al., 2018, *PLOS ONE*). The manuscript's PHQ-8 result can be
> stated as, to our knowledge, the first reported configural-level failure at
> this boundary. Scalar-level failures at the boundary are documented (GAD-7:
> Doi et al., 2018, *Frontiers*) and should be cited as precedent.

**New entries for §11:** none. Flag 1 below explains a clarifying note added
to an existing §11 entry.

---

### C3  End-to-end "calibrated detection + score-level consequences" in a psychiatric symptom inventory

**Verdict: CONTRADICTED.** Three applied papers on mental-health symptom
measures combine a non-fixed-cutoff detection method (alignment, or
dynamic-fit cutoffs) with a score-level consequence analysis. One of them
appeared in *Assessment*, the target journal.

**Searches run:**
- OpenAlex cited-by lists:
  - Nye & Drasgow 2011 (https://doi.org/10.1037/a0022955; 217 citing works).
  - Nye et al. 2019 (113).
  - Gonzalez & Pelham 2021 (29).
  - Together 279 unique works, filtered by clinical-measure terms and flagged
    for method keywords.
- The C9 cited-by list for Jorgensen et al. 2018, re-scanned for consequence
  layers.
- Europe PMC full text: (dMACS | "Millsap and Kwok" | "selection accuracy" |
  "expected test score" | DTF) × (permutation | alignment | "dynamic fit" |
  RMSEA_D | Bayesian approximate) × MI × clinical terms (17 hits).
- Full text read for the three papers below.

**Best candidates found:**

- **Black, L., Humphrey, N., Panayiotou, M., & Marquez, J. (2024; online
  2023). Mental health and well-being measures for mean comparison and
  screening in adolescents: An assessment of unidimensionality and sex and age
  measurement invariance. *Assessment*, 31(2), 219–236.
  https://doi.org/10.1177/10731911231158623**
  - **Design.** #BeeWell, N = 37,149, age 12–15. Eight measures, including
    the Me and My Feelings internalizing-symptoms scale. Dynamic fit indices
    for dimensionality; alignment (fixed) for detection; Millsap–Kwok/Lai
    selection-bias analysis.
  - **Quote:** "Since we compared groups with only two categories, we used
    alignment with fixed optimization"
  - **Quote:** "Using the method set out by Millsap and Kwok (2004), and
    elaborated by Lai et al. (2017), we estimated the effect of measurement
    non-invariance on selection across groups."
  - **Quote (abstract):** "Effects on selection were minimal, except
    sensitivity was substantially lower in boys for the internalizing
    symptoms measure."
  - **Verified at:** full text (PMC10822075).
  - **Why it preempts.** Under the handoff's own definition ("alignment with
    effect sizes … and … impact on cutoffs"), this is end-to-end, and it
    appeared in the target journal. Its groups are sex and age, not clinical
    strata, and it uses no significance test with calibrated error rates.

- **Nilsen, S. A., Stormark, K. M., Bang, L., Brunborg, G. S., Larsen, M., &
  Breivik, K. (2024). Time trends in adolescent depressive symptoms from 2010
  to 2019 in Norway: Real increase or artifacts of measurements?
  *Psychological Medicine*, 54(14), 3949–3961.
  https://doi.org/10.1017/s0033291724002447**
  - **Design.** Kandel & Davies 6-item Depressive Mood Inventory,
    N = 560,712. Wu–Estabrook ordinal ladder, dynamic fit cutoffs,
    ΔCFI ≥ −.002, dMACS, and consequences for trend estimates.
  - **Quote:** "we chose the stricter ΔCFI ⩾ −0.002 as the main cut-off, as
    proposed by Meade, Johnson, and Braddy (2008)"
  - **Quote:** "not accounting for the noninvariant parameters yielded highly
    similar trends as when accounted for … and latent means only differed by
    about 0.01 to 0.03 standard deviation units"
  - **Quote:** "state-of-the-art methods, including dynamic rather than static
    fit indices cut-offs (McNeish, 2023), basing the MI-analyses on recent
    advances in ordinal invariance testing (Wu & Estabrook, 2016), and by
    explicitly assessing the consequences that noninvariance may have for
    group comparisons and trend estimates."
  - **Verified at:** full text (PMC11578914).
  - **Why it preempts.** It tells the "detectable but inconsequential" arc end
    to end on a depressive-symptom inventory, with the manuscript's own
    identification scheme. Its detection still uses a fixed (if stricter) ΔCFI
    cutoff.

- **Zheng, S., Mansolf, M., McGrath, M., … Bishop, S. (2024; online 2023).
  Measurement bias in caregiver-report of early childhood behavior problems
  across demographic factors in an ECHO-wide diverse sample. *JCPP Advances*,
  4(1), e12198. https://doi.org/10.1002/jcv2.12198**
  - **Design.** CBCL/1.5-5, N = 9,087 from 26 cohorts. Alignment across
    child characteristics (including neurodevelopmental disorders) and
    caregiver characteristics. DIF effect sizes; robust item sets compared
    with the full scales.
  - **Quote:** "Factor analyses and the alignment method were applied to
    examine measurement invariance (MI) and differential item functioning
    (DIF) across child (age, sex, bilingual status, and neurodevelopmental
    disorders), and caregiver (…) characteristics."
  - **Quote:** "The robust item sets, excluding the high DIF items, showed
    good reliability and high correlation with the original Internalizing and
    Total Problems scales"
  - **Verified at:** full text (PMC10933609).
  - **Why it preempts.** Alignment detection plus a score-level comparison of
    reduced vs full scales, which is close to the manuscript's "cores vs full
    scales" logic.

- **Neighbors that pair conventional detection with consequences
  (abstracts):**
  - Blake et al. 2025: PHQ-9 in stroke, d = 0.434 overestimation.
  - Sunderland & Slade 2024, *IJMPR* 33(4), https://doi.org/10.1002/mpr.70008.
    DIF in CIDI screening questions changed sensitivity/specificity by
    0.001–0.091.
  - Kaplan-Kahn et al. 2024 (see C9). Permutation detection, but no
    consequence layer.

**Recommended change to `PRIOR_ART.md`.** §6: add the three papers to "What
exists". Replace "What the manuscript can claim" with

> The end-to-end arc is occupied: Black et al. (2024, *Assessment*) paired
> alignment-based detection with Millsap–Kwok selection-bias estimates for an
> adolescent internalizing measure; Nilsen et al. (2024) ran a Wu–Estabrook
> ordinal ladder with dynamic fit cutoffs and dMACS and showed non-invariance
> shifted depressive-symptom trend estimates by only 0.01–0.03 SD; Zheng et al.
> (2024) used alignment and DIF-impact analysis on the CBCL/1.5-5 and compared
> robust item sets with the full scales. The manuscript joins this line rather
> than opening it. What remains distinctive is the detector — permutation tests
> with calibrated Type I error at every Wu–Estabrook level — applied across a
> reporting-window change and clinical-vs-community strata, together with a
> consequence layer that reports signed net and gross sum-score bias with
> confidence intervals and tests whether preregistered validity conclusions
> survive core vs full-scale scoring.

**New entries for §11:**
- "No paper combines sensitivity-calibrated detection with formal score-level
  consequence analysis in a psychiatric symptom inventory." Refuted by Black et
  al. 2024, Nilsen et al. 2024, and Zheng et al. 2024.

---

### C4  HiTOP-SR / HiTOP-PRO short-window versions or cross-population invariance

**Verdict: CONTRADICTED for sub-claim (a)** ("no short-window adaptation
exists"). **Sub-claims (b) and (c) STAND.**

**Searches run:**
- OpenAlex cited-by Watson et al. 2022 (56) and Simms et al. 2022 (112).
- OpenAlex searches:
  - "HiTOP-SR" (950), "HiTOP self-report" (2,600), "HiTOP-PRO" (587), and
    "Hierarchical Taxonomy of Psychopathology measurement invariance"
    (1,447). Together 4,191 unique works, filtered for HiTOP plus
    SR/invariance/window/brief terms, 2021 onward.
  - HiTOP short form / brief / screener / "HiTOP internalizing scales",
    2022 onward.
- OSF API downloads of the preprint full texts of Mostajabi et al. (rjm4s v3)
  and Trummer et al. (t4ry2 v1), plus the OSF record for HiTOP-BR in cancer
  survivors (5mfpx).
- `hitop-system.org/hitop-sr` returned 404, and WebSearch was exhausted.

**Best candidates found:**

- **Mostajabi, J., Vize, C. E., Nielsen, S. R., Ringwald, W. R., & Wright,
  A. G. C. (2026). Structure of current psychopathology and its associations
  with daily life experiences using the Hierarchical Taxonomy of
  Psychopathology Self-Report (HiTOP-SR) in a mixed clinical/community sample.
  *Psychological Assessment*, 38(6–7), 451–465.
  https://doi.org/10.1037/pas0001455**
  - **Design.** HiTOP-SR with a past-month window. Mixed clinical/community
    sample (80% with treatment history). EFA n = 637, EMA n = 531. The v1
    preprint was titled "…using the HiTOP-PRO…".
  - **Quote:** "Participants were asked to rate how much each item applied to
    them in the past month. Each Likert-like item was rated using a 1 ("Not at
    all") to 4 ("A lot") scale."
  - **Quote:** "The version of the HiTOP-SR used in the present study asked
    about experiences in the past month. This differs from the official
    measure published by Simms and colleagues (2023), which focuses on
    experiences over the past year."
  - **Quote:** "One possibility for the emergence of this factor in our study
    is that the measure was designed to assess past-year symptoms, thus
    included many low base rate experiences, but we asked about experiences in
    the past month. This narrower timescale may have resulted in certain
    experiences appearing especially "rare." Consistent with this possibility,
    factor analysis of the German version of the measure using the past-year
    time frame did not find a rarity factor (Zimmerman et al., 2024)."
  - **Verified at:** full text (PsyArXiv rjm4s v3, 2026-02-26; the published
    version was not read).
  - **Why it preempts (a).** A short-window administration of the HiTOP-SR,
    including its internalizing scales, exists. It contains no invariance test
    of the window change, uses a past-month rather than a two-week window, and
    has no comparison sample under the original window. It explicitly raises
    the window-effect question that the manuscript tests.

- **Trummer, B. T. T., Wendt, L. P., Schroeders, U., & Zimmermann, J. (2026).
  Measurement invariance and sociodemographic differences at the lowest level
  of the psychopathology hierarchy: An analysis of the German HiTOP-SR
  [Preprint]. PsyArXiv. https://doi.org/10.31234/osf.io/t4ry2_v1**
  - **Design.** N = 1,049 general population. 87 facets × sex/age/SES. Ordinal
    multigroup CFA with Chen cutoffs.
  - **Quote:** "Non-invariance was inferred if, relative to the configural
    model, the scalar model showed ΔCFI ≤ −.005 and ΔRMSEA ≥ .010 (Chen,
    2007)."
  - **Quote:** "the decision rules relied on fit-index cutoffs developed for
    continuous data and maximum-likelihood estimation …, applied here to short
    ordinal scales estimated with W[LSMV]"
  - **Quote:** "General-population samples are therefore ill-suited to such
    content, and larger or enriched clinical samples would allow more complete
    testing."
  - **Verified at:** full text (OSF docx).
  - **Why it does not preempt.** It tests HiTOP-SR invariance only across
    demographics, within the general population. It is a foil for the
    criteria thread, and it names the clinical-sample gap.

- **Lee, H. C., & Chmielewski, M. (2026). *Journal of Psychopathology and
  Clinical Science*, 135(3), 446–460. https://doi.org/10.1037/abn0001114**
  - **Design.** Moderated nonlinear factor analysis (MNLFA) of HiTOP
    dimensions on diagnostic data (N = 16,238), across sociodemographic
    covariates.
  - **Quote:** "Results for MNLFA revealed sources of measurement
    noninvariance that were not previously detected using multigroup
    confirmatory factor analysis."
  - **Verified at:** abstract (OpenAlex).
  - **Why it does not preempt.** It concerns neither the SR nor clinical vs
    community groups. It is relevant to C6 as a method-sensitivity point.

- **(c) Brief HiTOP instruments that are not short forms of the internalizing
  scales:**
  - HiTOP-BR (already cited) and a PsyArXiv validation of HiTOP-BR in cancer
    survivors (5mfpx), which has no invariance analysis.
  - de Oliveira, Krueger et al. 2026, *Personality and Individual
    Differences*, https://doi.org/10.1016/j.paid.2026.113960, a Brazilian
    brief scale (HiTOP-BBS).
  - Zhang et al. (OSF t6vxy), a Mandarin HiTOP-SR adaptation with a
    five-week retest.

**Recommended change to `PRIOR_ART.md`.** §8: replace "the HiTOP-SR uses a
past-12-months window … The two-week-window niche is therefore unoccupied"
with

> The official HiTOP-SR asks about the past year, but Mostajabi et al. (2026,
> *Psychological Assessment*) administered it with a past-month window in a
> mixed clinical/community sample and attributed an unexpected "Rarity" factor
> partly to the narrower window — without testing invariance across windows.
> A short-window HiTOP-SR administration therefore exists; what remains
> unoccupied is a two-week window, a formal (calibrated) test of the window
> change against data collected under the original window, and clinical-vs-
> community invariance of HiTOP-SR item sets (the German HiTOP-SR has been
> tested only across sex, age and SES in a general-population sample with Chen
> cutoffs; Trummer et al., 2026). Mostajabi et al. should be cited as the paper
> that raises the window question for the current instrument.

**New entries for §11:**
- "No short-window adaptation of the HiTOP-SR exists." Refuted by Mostajabi et
  al. 2026 (past-month window).

---

### C5  Exhaustive subset enumeration, "no invariant subset exists" proofs, greedy lockout

**Verdict: WEAKENED.** Global, combinatorial item selection aimed at
invariance is an established technique: ant colony optimization, the
`stuart` package's search algorithms, and one small exhaustive enumeration.
It appears in *Assessment* and elsewhere, and it comes with explicit
arguments that sequential removal gets stuck in local optima. Two things were
not found: a certificate that no invariant subset exists, and a real-data
demonstration that MI-guided stepwise removal discarded an item belonging to
the only invariant subset.

**Searches run:**
- OpenAlex searches: Schultze & Eid title; `stuart`; ACO invariant short
  scales; "exhaustive search measurement invariance item subsets"; "all
  possible anchor sets"; brute force; combinatorial partial invariance.
- Europe PMC full text: (bruteforce | "brute force" | "all possible
  combinations" | "exhaustive search" | "every possible combination") × (MI |
  DIF). 111 hits; brute-force passages read in nine PMC full texts.
- OpenAlex cited-by Kopf et al. 2015 (120) and Woods 2009 (174), filtered for
  exhaustive / all-possible / combinatorial / enumeration / brute force /
  branch-and-bound / global optimum. No anchor-enumeration paper was found.
- Semantic Scholar cited-by, with abstracts, after the OpenAlex budget ran
  out:
  - Asparouhov & Muthén 2014 (78)
  - Yoon & Millsap 2007 (209)
  - Yoon & Kim 2014 (54)
  - Jung & Yoon 2016 (66)
  - Kolbe & Jorgensen 2019 (11)
  - MacCallum et al. 1992 (1,731)
  - Schultze & Eid 2018 (14)

**Best candidates found:**

- **Schultze, M., & Eid, M. (2018). Identifying measurement invariant item
  sets in cross-cultural settings using an automated item selection
  procedure. *Methodology*, 14(4), 177–188.
  https://doi.org/10.1027/1614-2241/a000155**
  - **Quote:** "We present an approach to automated item selection which
    depicts the process as a combinatorial optimization problem and aims at
    finding a scale which fulfils predefined target criteria – such as
    measurement invariance across cultures."
  - **Verified at:** abstract (OpenAlex).
  - **Why it does not fully preempt.** It is a heuristic search (Ant System),
    not an exhaustive one. It looks for an optimal subset but cannot certify
    that none exists.

- **Olaru, G., Wilhelm, O., Nordin, S., Witthöft, M., & Köteles, F. (2019).
  Modern health worries: Deriving two measurement invariant short scales for
  cross-cultural research with Ant Colony Optimization. *PLOS ONE*, 14(2),
  e0211819. https://doi.org/10.1371/journal.pone.0211819**
  - **Quote:** "Instead of removing items se[quentially] …, ACO searches for
    item samples of a fixed size. Thus, it is not affected sequence effects and
    more likely to find the best model instead of optimize the scale towards a
    local optimum."
  - **Quote:** "As the number of possible four item combinations based on the
    previously model was relatively small (81), we estimated all possible
    models and compared them based on the optimization criterion"
  - **Verified at:** full text (PMC6366774).
  - **Why it partly preempts.** It is a real-data, global selection of
    invariant items, with a small exhaustive enumeration and the local-optimum
    argument. Its search space was fixed-size and constrained (one item per
    factor), it used a composite criterion rather than an invariance test, and
    it made no claim that no subset exists.

- **Jankowsky, K., Olaru, G., & Schroeders, U. (2020). *European Journal of
  Personality*, 34(3), 470–485. https://doi.org/10.1002/per.2260**
  - **Quote:** ACO used "to select item sets that satisfy multiple
    psychometric requirements including model fit, reliability, and
    measurement invariance."
  - **Verified at:** abstract (OpenAlex).

- **Olaru, G., & Danner, D. (2021; online 2020). Developing cross-cultural
  short scales using ant colony optimization. *Assessment*, 28(1), 199–210.
  https://doi.org/10.1177/1073191120918026**
  - **Quote:** "the ACO short scale achieved better model fit and measurement
    invariance across countries than the Big Five Inventory-2 extra-short form"
    (the latter was developed with a traditional approach).
  - **Verified at:** abstract (OpenAlex).
  - **Why it does not preempt.** It is in-journal precedent for preferring a
    global over a traditional selection. The comparison was against an
    expert-built short form, not against greedy MI-guided removal.

- **Schroeders, U., Wilhelm, O., & Olaru, G. (2016). Meta-heuristics in short
  scale construction. *PLOS ONE*, 11(11), e0167110.
  https://doi.org/10.1371/journal.pone.0167110**
  - **Quote:** "[Strategies that remove items stepwise] are dependent on the
    sequence of items removed and are prone to local optima during the
    selection process."
  - **Verified at:** full text (PMC5125670).
  - **Why it does not preempt.** It compares stepwise CFA with metaheuristics
    on real data, but not for invariance.

- **Other neighbors:**
  - Schulze, Reuter & Pohl 2022, *SEM* 29(4):521–530,
    https://doi.org/10.1080/10705511.2021.2012785. Model averaging over
    anchor-item choices, with an OCD example. Abstract only.
  - Belzak & Bauer 2020, *Psychological Methods* 25(6):673–690,
    https://doi.org/10.1037/met0000253. Regularized anchor selection, a
    global rather than sequential alternative.
  - Kerber et al. 2020, *Assessment* (PMC8866743), used `stuart`'s
    "brute-force" function to compare "every possible combination of items",
    but only for fit and reliability. A related, not preempting use.

**Recommended change to `PRIOR_ART.md`.** §7: add these papers to "What
exists". Replace "What the manuscript can claim" with

> Global, combinatorial item selection for invariance is established —
> automated ACO/`stuart` searches for invariant item sets (Schultze & Eid,
> 2018; Jankowsky et al., 2020; Olaru & Danner, 2021, in *Assessment*), one of
> which enumerated all 81 candidate four-item sets (Olaru et al., 2019) — and
> so is the argument that stepwise removal is trapped by local optima
> (Schroeders et al., 2016; Olaru et al., 2019). The manuscript should cite this
> line and not claim to introduce global item selection. What was not found:
> an exhaustive enumeration of every subset of three or more items under a
> calibrated significance test; a certificate that no invariant subset exists
> (8 of 14 constructs here); and a real-data case in which MI-guided stepwise
> removal discarded an item belonging to the only invariant subset (social
> anxiety here). Those remain apparent firsts. Recommended wording for the
> lockout: *a concrete instance of the path-dependence long asserted for
> MI-guided searches, in a regime (ordinal indicators, item removal, majority
> non-invariance, two groups) that the simulations endorsing sequential search
> did not cover, where alignment is unavailable and heuristic global searches
> cannot certify absence.*

**New entries for §11:**
- "No paper performs global or combinatorial item selection for invariance."
  Refuted by Schultze & Eid 2018, Olaru et al. 2019, Jankowsky et al. 2020, and
  Olaru & Danner 2021. Only the narrower claims (exhaustive ≥3-item
  enumeration, a "none exists" certificate, a greedy lockout) survive.

---

### C6  Within-study comparison of ΔAFI sensitivity across comparison types; clinical-vs-community under-detection argument

**Verdict: STANDS.** No applied paper was found that runs ΔCFI/ΔRMSEA
alongside a calibrated test across several grouping variables and reports
agreement or power for each grouping variable. No paper was found arguing that
clinical-vs-community comparisons are where ΔCFI is least sensitive.

**Searches run:**
- Semantic Scholar cited-by:
  - McNeish 2026 (11).
  - Savalei et al. 2023, via its PsyArXiv record (79 citing works; S2 returns
    404 for the APA DOI).
  - Kang et al. 2016 (94).
  - Jorgensen et al. 2018 (63).
  - Each list was filtered for invariance × (ΔCFI | cutoff | dynamic |
    RMSEA_D | permutation | sensitivity | power).
- OpenAlex cited-by Jorgensen 2018 and Kite 2018, from C9.
- Europe PMC full text: (RMSEA_D | dynamic measurement invariance |
  permuteMeasEq | permutation test) × ΔCFI × MI × clinical × community
  (12 hits; four checked in full text).
- The C8 workflow's near-misses (Baghaei et al. 2026; Hlynsson et al. 2025).

**Best candidates found:**

- **Lee & Chmielewski 2026** (see C4). MNLFA detected non-invariance "not
  previously detected using multigroup confirmatory factor analysis" across
  sex, race/ethnicity, age and income.
  - **Verified at:** abstract.
  - **Why it does not preempt.** The comparison is between methods and against
    earlier studies. It is not ΔAFI vs a calibrated benchmark per grouping
    variable within one study, and it does not involve clinical vs community
    groups.

- **Trummer et al. 2026** (see C4). Reported Cohen's w from the scaled
  Δχ² alongside the ΔCFI/ΔRMSEA decisions for each of three grouping
  variables.
  - **Quote:** "These effect sizes complemented, but did not alter, the
    ΔCFI/ΔRMSEA decisions."
  - **Verified at:** full text.
  - **Why it does not preempt.** It does not compare the criteria's
    sensitivity, and its groups are demographic only.

- **Kaplan-Kahn et al. 2024** (see C9). Permutation-tested Δχ² and ΔCFI in
  autistic vs general-population teens, for one grouping variable. It does
  not compare against fixed cutoffs.

- **Chen, P.-Y., & Chao, T.-Y. (2026). A comparison of methods for testing
  measurement invariance with unbalanced data. *Structural Equation
  Modeling*, 33(3), 404–411. https://doi.org/10.1080/10705511.2025.2591420**
  - **Design.** Simulation.
  - **Quote:** "The results indicate the type I error rates of the Δ AFI
    cutoffs are often too conservative."
  - **Verified at:** abstract.
  - **Why it does not preempt.** It is a simulation, not an applied
    comparison. See Flag 2.

- **Already cited:** Abulela et al. 2024 (conventional criteria and RMSEA_D
  agreed); Briers et al. 2026 and Florean et al. 2022 (verdicts differ by
  grouping variable, with no comparison of criteria); Neufeld et al. 2023 (the
  under-detection caveat).

**Recommended change to `PRIOR_ART.md`.** §5.4: add one sentence noting that
the 2026-10-01 contradiction search found nothing new, and name Lee &
Chmielewski 2026 and Trummer et al. 2026 as the nearest neighbors. §5.5:
keep the narrowed pair-dependence claim, and add a caution about Chen & Chao
2026 (Flag 2).

**New entries for §11:** none.

---

### C7  Empirical "level mislocalization"

**Verdict: STANDS.** The only precedents remain analogical simulations. Two
have been added to Joo & Kim 2019.

**Searches run:**
- Semantic Scholar cited-by Joo & Kim 2019 (19 citing works; abstracts
  scanned for misattribution / transfer / mask / configural language).
- Europe PMC full text: MI × (misattributed | misattribution | mislocalized |
  "wrong level" | "manifest as metric noninvariance" | "appear as metric").
  143 hits, none on point.
- The Chen 2007 cited-by walk was not run: the OpenAlex budget had run out,
  and the list runs to several thousand works.

**Best candidates found:**

- **Cao, C., & Liang, X. (2024; online 2023). The impact of ignoring
  cross-loadings on the sensitivity of fit measures in measurement invariance
  testing. *Structural Equation Modeling*, 31(1), 64–80.
  https://doi.org/10.1080/10705511.2023.2223360**
  - **Quote:** "the ignored cross-loadings affected the sensitivity of all fit
    measures but LRT to metric noninvariance … In the largest model size, CFI
    failed to detect metric noninvariance when there were no cross-loadings in
    the population model but detected the metric noninvariance of .30 with
    ignored cross-loadings."
  - **Verified at:** abstract.
  - **Why it does not preempt.** A configural-type misspecification changes
    what ΔAFIs detect at the metric step, which is analogical support only. It
    is a simulation.

- **Rios, J. A. (2021). Is differential noneffortful responding associated
  with Type I error in measurement invariance testing? *Educational and
  Psychological Measurement*, 81(5), 957–979.
  https://doi.org/10.1177/0013164421990429**
  - **Quote:** "as differential rates of NER grew, increased Type I errors of
    measurement invariance were observed only at the metric invariance level,
    while no negative effects were apparent for configural or scalar
    invariance."
  - **Verified at:** abstract.
  - **Why it does not preempt.** A violation that does not involve loadings
    surfaces as a metric-level flag. It is an analogy, from a simulation.

**Recommended change to `PRIOR_ART.md`.** §5.3: add Cao & Liang and Rios
alongside Joo & Kim as analogical precedents. Keep "can be claimed as an
applied first, cautiously".

**New entries for §11:** none.

---

### C8  Reanalyses reversing published invariance claims; practice reviews in clinical-assessment journals; *Assessment* editorials

**Verdict: CONTRADICTED for sub-claim (1)** (same-data reanalysis reversing a
ΔCFI/ΔRMSEA verdict). **Sub-claims (2) and (3) STAND.**

**Searches run:**
- `/deep-research` run `wf_8af9e1d1-60f`, scoped adversarially to the three
  sub-claims. It fetched 19 sources; 23 claims were confirmed and 2 refuted.
- Re-verification here:
  - Lasker 2024, full text via the PMC HTML.
  - Cieciuch et al. 2014, Schroeders & Gnambs 2020 and Protzko 2024,
    abstracts via OpenAlex.
  - The De Los Reyes et al. 2025 editorial: PubMed record, plus a Crossref
    check of all 79 of its references for Flake & Fried, Hussey & Hughes,
    Maassen et al. and Goretzko et al.
- A Crossref sweep of *Assessment* (ISSN 1073-1911) items published 2019–2026,
  with queries for editorial, author Samuel, author Simms, "measurement
  practices", "reporting standards", "transparency open science", and
  "measurement invariance reporting". Reference lists were checked for the
  editorial-type and meta-science items.

**Best candidates found:**

- **(1) Lasker, J. (2024). Measurement invariance testing works. *Applied
  Psychological Measurement*, 48(6), 257–275.
  https://doi.org/10.1177/01466216241261708**
  - **Design.** Reanalysis of Protzko's N ≈ 1,500 randomized "meaning in life
    vs gavagai" data. Protzko's invariance conclusion rested on ΔCFI/ΔRMSEA;
    Lasker re-tested with χ² difference tests, AIC and RMSEA_D.
  - **Quote:** "First, Protzko (2022) used insensitive model fit indices that
    failed to indicate measurement noninvariance where it was tested."
  - **Quote:** "That it did not appear as indicated with liberal CFI and RMSEA
    cutoffs indicts those approximate fit indices more than it supports metric
    or scalar invariance."
  - **Quote (footnote 8):** "unlike ∆RMSEA, the use of RMSEAD disconfirms the
    findings of Protzko (2022)"
  - **Verified at:** full text (PMC11331746 HTML).
  - **Why it preempts.** It is a same-data reversal of a fixed-cutoff
    invariance verdict under exact tests and RMSEA_D. The construct is
    non-clinical. The RMSEA_D result appears only in a footnote. Protzko's
    published version (*Educational and Psychological Measurement*, 85(3),
    458–482, https://doi.org/10.1177/00131644241282982) keeps its
    conclusion, so the dispute is live.

- **(1, opposite direction) Cieciuch, J., Davidov, E., Schmidt, P.,
  Algesheimer, R., & Schwartz, S. H. (2014). *Frontiers in Psychology*, 5,
  982. https://doi.org/10.3389/fpsyg.2014.00982**
  - **Quote:** "The current study applied the approximate measurement
    invariance procedure on the same data and established approximate scalar
    measurement invariance even for all 19 values."
  - **Verified at:** abstract.
  - **Why it matters.** A calibrated or approximate method reversed toward
    *more* invariance. The text should not imply that reanalyses reverse in
    only one direction.

- **(1) No many-analysts or multiverse project on invariance decisions was
  found** (workflow-verified). The MARP measurement commentary and Sarstedt et
  al. 2024 were ruled out.

- **(2) Schroeders, U., & Gnambs, T. (2020; online 2018). Degrees of freedom
  in multigroup confirmatory factor analyses. *European Journal of
  Psychological Assessment*, 36(1), 105–113.
  https://doi.org/10.1027/1015-5759/a000500**
  - **Quote:** "we reviewed 128 studies from six leading peer-reviewed
    journals focusing on psychological assessment and recalculated the df for
    302 measurement invariance testing procedures."
  - **Verified at:** abstract. The journal list (*Assessment*, *Psychological
    Assessment*, *JPA*, *EJPA*, *JCCP*, *PAID*; 1996–2016) is
    workflow-verified from the accepted manuscript, not re-read by me.
  - **Why it does not preempt.** It is an audit of how invariance tests are
    reported, partly in the named journals. It audits df correctness only,
    not decision criteria or pass rates, and it does not cover *Clinical
    Psychological Science*.

- **(2) Contractor, A. A., Caldas, S. V., Dolan, M., Natesan, P., & Weiss,
  N. H. (2019). Invariance of the construct of posttraumatic stress disorder:
  A systematic review. *Journal of Traumatic Stress*, 32(2), 287–298.
  https://doi.org/10.1002/jts.22389**
  - **Verified at:** workflow-verified (3-0). It codes decision criteria
    (Δχ² in 86.5% of analyses, ΔCFI in 31.3%).
  - **Why it does not preempt.** It is limited to one construct, not to
    particular journals. It is the closest psychopathology precedent for
    coding which criteria are used.

- **(3) Markon, K. E., & Olino, T. (2025). From confirmation to theory:
  Introduction to the special section on "Assessment, Measurement, and
  Registered Replication." *Assessment*, 32(2), 167–169.
  https://doi.org/10.1177/10731911251320053**
  - **Quote:** "The goal of this special section was to encourage discussion
    about replication in assessment science, as well as the use and
    development of registered replication and open science more broadly."
  - **Verified at:** abstract, plus a Crossref check of its eight references.
    Flake & Fried 2020 is not among them.
  - **Why it does not preempt.** It is an editorial-type piece in *Assessment*
    on replication and open science that does not engage Flake & Fried. It is
    useful for positioning.

- **(3) Other neighbors:**
  - Buchanan, E. M. (2025; online 2024). Visualizemi. *Assessment*, 32(2), 190–205.
    https://doi.org/10.1177/10731911241280763.
  - Flores-Kanter, P. E., & Alvarado, J. M. (2024). *Assessment*, 31(8),
    1567–1579. https://doi.org/10.1177/10731911241236315.
  - Both are regular *Assessment* articles that cite Flake & Fried 2020
    (Crossref reference lists).
  - De Los Reyes, A., Oswald, F. L., Racz, S. J., Pina, A., McLeod, B. D.,
    Wang, M., & Charamut, N. R. (2025). Editorial: Fairness, validity, and
    transparency in what researchers assume when testing for measurement
    invariance. *Journal of Clinical Child & Adolescent Psychology*, 54(3),
    299–317. https://doi.org/10.1080/15374416.2025.2484813. An invariance
    editorial in a clinical journal; none of its 79 references is Flake &
    Fried, Hussey & Hughes, Maassen or Goretzko.

**Recommended change to `PRIOR_ART.md`.** §9: add the items above to "What
exists". Revise "What the manuscript can claim" so that the reanalysis line
credits Lasker (2024). The suggested positioning paragraph becomes

> Prior audits show that invariance is rarely tested and that scales often fail
> when it is (Maassen et al.; Hussey & Hughes; Putnick & Bornstein), audits of
> assessment journals have checked how invariance tests are reported
> (Schroeders & Gnambs, 2020), and one same-data reanalysis shows a
> ΔCFI/ΔRMSEA-based invariance verdict reversing under exact tests and RMSEA_D
> (Lasker, 2024). But the audits adjudicate invariance with the same
> heuristics, whose sensitivity in clinical-vs-community comparisons is
> unknown (Neufeld et al.). We audit the criteria themselves against a
> calibrated benchmark, across comparison types, in a psychiatric inventory.

Sub-claims (2) and (3) can stay. Wording: "no review of invariance *decision
criteria* restricted to clinical-assessment journals was found (Schroeders &
Gnambs, 2020, audited df reporting in three of them)" and "no *Assessment*
editorial engaging Flake & Fried (2020) was found in a Crossref sweep of
2019–2026 items."

**New entries for §11:**
- "No published reanalysis shows ΔCFI/ΔRMSEA-based invariance conclusions
  reversing under calibrated or exact methods." Refuted by Lasker 2024. Note
  that Cieciuch et al. 2014 reversed in the opposite direction.

---

### C9  Has `permuteMeasEq` been applied empirically to ordinal symptom-inventory data?

**Verdict: CONTRADICTED** (taking the potential claim to be "first empirical
application"). Yes: it has been applied to ordinal symptom scales at every
level, between a clinical-adjacent group and a general-population group.

**Searches run:**
- OpenAlex cited-by Jorgensen et al. 2018 (W2770732967; 78 works) and Kite et
  al. 2018 (W2789566388; 32 works).
- Semantic Scholar citations for the same two papers (63 and 28; 8 not in
  OpenAlex, none relevant).
- Europe PMC full text: "permuteMeasEq" (2 hits); and (permutation test |
  permutation-based) × MI × symptom terms (117 hits, mostly network-analysis
  permutation tests).
- Full-text checks of 16 candidates.

**Best candidates found:**

- **Kaplan-Kahn, E. A., Benecke, R. M., Guthrie, W., Yerys, B. E., Holmes,
  L. G., & Miller, J. S. (2024). Measurement invariance of the PROMIS
  emotional distress and subjective well-being domains among autistic and
  general population adolescents. *Quality of Life Research*, 33(11),
  3003–3012. https://doi.org/10.1007/s11136-024-03742-9**
  - **Design.** PROMIS pediatric Anger, Anxiety, Depression and Psychological
    Stress, plus subjective well-being, in autistic vs general-population
    teens (about 406–411 general-population teens per scale). Ordinal DWLS;
    configural, metric and scalar levels, with permutation at every level.
  - **Quote:** "we used permutation tests [49] to evaluate the hypothesis of
    measurement invariance and determine whether the ∆χ2 and the ∆CFI between
    the increasingly restrictive models were significant. As reported in
    Jorgensen et al., 2018, permutation tests provide better Type-I error
    control than commonly used benchmarks. We generated null distributions for
    all measurement invariance tests based on 1,000 permutated datasets"
  - **Verified at:** full text (PMC11541282).
  - **Why it preempts "first application."** No separate thresholds step, no
    consequence analysis, a single grouping variable, and about five scales.

- **Kildahl, A. N., Hellerud, J. M. A., Halvorsen, M. B., & Helverschou,
  S. B. (2026; online 2025). The Aberrant Behavior Checklist in a clinical
  sample of autistic individuals with intellectual disabilities…. *Journal of
  Autism and Developmental Disorders*, 56(5), 1980–1998.
  https://doi.org/10.1007/s10803-024-06697-5**
  - **Quote:** "For the configural models, we chose to use permutation tests
    (3000 permutations) … via the permuteMeasEq function of semTools in R …
    For the remaining models (threshold, metric, scalar, residual), we chose to
    use the cutoffs suggested by Chen (2007)."
  - **Verified at:** full text (PMC13190804).
  - **Why it does not preempt.** It uses permutation for the configural step
    only, applies the Wu–Estabrook thresholds step under Chen cutoffs, and is
    longitudinal within one clinical sample.

- **Other applications on non-symptom constructs:**
  - PROMIS Family Relationships in autistic vs general-population teens
    (Benecke, Williams, Holmes, Miller & Kaplan-Kahn, 2026, *Autism
    Research*, 19(2), https://doi.org/10.1002/aur.70161; PMC12945458),
    permutation at every level.
  - Clements et al. 2020 (DAS-II IQ).
  - Jang et al. 2022 (organizational citizenship behavior).

**Recommended change to `PRIOR_ART.md`.**
- Methods citation row (§10 table): add Kaplan-Kahn et al. 2024 as prior
  applied use.
- §10 "apparent firsts": do not add a "first application of permuteMeasEq"
  claim. Defensible wording:

> Permutation-tested invariance has been applied to ordinal symptom scales
> before (Kaplan-Kahn et al., 2024, at every level for five PROMIS pediatric
> scales; Kildahl et al., 2026, at the configural level only); the present
> study applies it at scale — every Wu–Estabrook level including thresholds,
> 20 scales × three pairs, 1,000 permutations per step — and pairs it with
> exhaustive subset searches and a consequence analysis.

**New entries for §11:**
- "First empirical application of `permuteMeasEq` to ordinal symptom-inventory
  data." Refuted by Kaplan-Kahn et al. 2024 (and, for the configural step,
  Kildahl et al. 2026).

---

### C10  Maassen et al.'s explicit recommendations

**Verdict: RETRIEVED.**

**Source read:** the accepted manuscript on PsyArXiv
(https://osf.io/preprints/psyarxiv/n3f5u; file `240114-manuscript.pdf`, which
carries the APA "not the copy of record" notice). Read at full text. The
GitHub code repository was not needed.

**Recommendations, verbatim:**

- **Decision criteria.** They used the conventional cutoffs and also
  questioned whether those cutoffs suit every dataset:

  > "Researchers should also carefully consider the fit measures and cutoffs
  > they plan to use to evaluate model fit. While there are numerous
  > goodness-of-fit indices and cutoffs available for assessing model fit,
  > researchers—including us—often resort to commonly used and widely accepted
  > fit indices and demarcation criteria (e.g., Chen, 2007; Cheung & Rensvold,
  > 2002). However, their suitability can differ based on the data and model
  > characteristics. Fortunately, open-source R packages and web-based
  > applications now provide dynamic fit index cutoffs … (McNeish & Wolf, 2023;
  > M. G. Wolf & McNeish, 2023)."

  Their own Step 3 rule was joint: a significant χ² difference *and* at
  least two of ΔRMSEA > .01, ΔCFI < −.01, ΔAIC and ΔBIC. They neither
  endorse ΔCFI/ΔRMSEA outright nor mention permutation tests.

- **Practical significance:**

  > "The magnitude of the violation in relation to the expected target effect
  > and the number of non-invariant items should be considered (Borsboom, 2006;
  > Nye et al., 2018), and standardized effect size measures can provide
  > information on the magnitude of measurement non-invariance that is
  > comparable across studies"

- **Partial invariance:**

  > "while these procedures may improve model fit, they are often based on post
  > hoc data-driven decisions that capitalize on chance and may lead to
  > overfitting the model to improve fit." (citing MacCallum et al., 1992)

  If configural fails, they suggest multigroup EFA (De Roover & Vermunt,
  2019).

- **Modified scales.** This is directly relevant to the window adaptation:

  > "altering an existing scale essentially requires a reevaluation of its
  > underlying structure. … Subsequent MI testing can verify that the changes
  > have not inadvertently introduced dimensionality differences or
  > group-specific biases. … we urge researchers to assess a scale's factor
  > structure and reliability separately for each group they analyze,
  > especially when using modified scales."

- **Reporting:**

  > "MI results should be reported according to established guidelines, such as
  > those by Putnick and Bornstein (2016), which include providing information
  > on total and group sample sizes, missing data, fit criteria and fit
  > measures, and the related invariance conclusion for all fitted models."

  They also point to COSMIN and to "six questions on measurement practices
  proposed by Flake and Fried (2020)". They urge journals to require
  measurement sections and checklists.

- **Code and data:**

  > "sharing code with the data is crucial to reproducing results"

  > "We recommend that researchers adopt FAIR principles"

  The paper proposes a Report–Reproduce–Reassess–Reuse framework.

- **Preregistration.** The Discussion contains no explicit recommendation to
  preregister invariance tests. Preregistration appears only in their own
  Methods (osf.io/s96gc).

**Recommended change to `PRIOR_ART.md`.** §9: add a bullet summarizing these
recommendations, especially the modified-scales recommendation and the
criteria caveat. §12 item 4: mark done.

**New entries for §11:** "Maassen et al. recommend preregistering
invariance tests." Not supported, so do not attribute it to them.

---

## Flags for the author

1. **§11 entry on Doi et al. (2018), PHQ-9.**
   - §11 lists "A specific Doi et al. (2018) PHQ-9 clinical-vs-non-clinical
     ΔCFI-only example" as refuted.
   - A *separate* 2018 paper by the same group, the *PLOS ONE* PHQ-9 article
     (https://doi.org/10.1371/journal.pone.0199235), states that ΔCFI < .01
     was its model-adoption criterion. It found scalar invariance between
     non-clinical and MDD groups (full text, quotes under C2).
   - The earlier refutation was probably checked against the *Frontiers*
     GAD-7 paper.
   - I did not delete the §11 entry. I added a clarifying note and cited the
     *PLOS ONE* paper separately in §4. Please confirm that is the right
     reading of what was refuted.

2. **Chen & Chao (2026) and the refuted unequal-N explanation.**
   - This simulation finds ΔAFI cutoffs' Type I error "often too
     conservative" with unbalanced groups (abstract only).
   - It concerns Type I error, not power. It does not license the unequal-N
     explanation for lower population-strata sensitivity that §11 refutes.
   - A reviewer may raise it. If so, read the full text for its power results
     before responding. Chen (2007)'s finding still stands as cited.

3. **An open reanalysis target in the target journal.** The C8 workflow
   surfaced Hlynsson et al. 2025 (*Psychiatric Quarterly*,
   https://doi.org/10.1007/s11126-025-10208-9), workflow-verified. It
   questions, without reanalyzing, a Hu & Bentler-based PHQ-9 temporal
   invariance result in *Assessment* (Stochl et al.). Not needed for this
   manuscript; a possible future note.

4. **Watch list.**
   - Cole (2026), a trifactor recall-window talk (C1).
   - The Lasker–Protzko exchange (C8), which is live.
   - The full text of Kuharic et al. 2026, read at abstract only.
   - A re-run of the Chen 2007 and Asparouhov & Muthén 2014 cited-by walks
     in OpenAlex once its daily budget resets, since the Semantic Scholar
     coverage used here is thinner.
