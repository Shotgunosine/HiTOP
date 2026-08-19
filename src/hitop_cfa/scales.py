"""Scale formulas: the single source of truth for headless (HPC) runs.

These duplicate the dicts defined in the notebooks (which remain the
source used interactively); keep them in sync if the item sets ever
change.
"""

ORIG_ITEMS = {
    'anhedonic_depression': 'anhedonic_depression =~hitop39 + hitop77 + hitop84 + hitop92 + hitop93 + hitop123 + hitop157 + hitop182 + hitop230 + hitop246',
    'anxious_worry': 'anxious_worry =~hitop20 + hitop34 + hitop89 + hitop203 + hitop240 + hitop248 + hitop265',
    'appetite_gain': 'appetite_gain =~hitop120 + hitop141 + hitop243 + hitop275',
    'appetite_loss': 'appetite_loss =~hitop280 + hitop283 + hitop109',
    'cognitive_problems': 'cognitive_problems =~hitop67 + hitop159 + hitop189 + hitop142',
    'hyposomnia': 'hyposomnia =~hitop99 + hitop181 + hitop5 + hitop66 + hitop231',
    'indecisiveness': 'indecisiveness =~hitop21 + hitop90 + hitop95',
    'insomnia': 'insomnia =~hitop160 + hitop254 + hitop261 + hitop268',
    'panic': 'panic =~hitop15 + hitop104 + hitop126 + hitop211 + hitop215 + hitop257',
    'separation_insecurity': 'separation_insecurity =~hitop40 + hitop50 + hitop69 + hitop81 + hitop113 + hitop136 + hitop151 + hitop197',
    'shame_guilt': 'shame_guilt =~hitop72 + hitop140 + hitop143 + hitop220',
    'situational_phobia': 'situational_phobia =~hitop16 + hitop165 + hitop225 + hitop247 + hitop278',
    'social_anxiety': 'social_anxiety =~hitop1 + hitop17 + hitop114 + hitop117 + hitop124 + hitop129 + hitop204 + hitop222 + hitop236 + hitop258',
    'well_being': 'well_being =~hitop9 + hitop23 + hitop54 + hitop106 + hitop149 + hitop200 + hitop244 + hitop245 + hitop250 + hitop281',
}

OTHER_SCALES = {
    'phq_sum': 'phq_sum=~phq_1 + phq_2 + phq_3 + phq_4 + phq_5 + phq_6 + phq_7 + phq_8',
    'gad_sum': 'gad_sum =~gad_1 + gad_2 + gad_3 + gad_4 + gad_5 + gad_6 + gad_7',
    'baars_inattention_sum': 'baars_inattention_sum =~inattention_1 + inattention_2 + inattention_3 + inattention_4 + inattention_5 + inattention_6 + inattention_7 + inattention_8 + inattention_9',
    'baars_hyperactivity_sum': 'baars_hyperactivity_sum =~hyperactivity_1 + hyperactivity_2 + hyperactivity_3 + hyperactivity_4 + hyperactivity_5',
    'baars_impulsivity_sum': 'baars_impulsivity_sum =~impulsivity_1 + impulsivity_2 + impulsivity_3 + impulsivity_4',
    'baars_sct_sum': 'baars_sct_sum =~sct_1 + sct_2 + sct_3 + sct_4 + sct_5 + sct_6 + sct_7 + sct_8 + sct_9',
}
