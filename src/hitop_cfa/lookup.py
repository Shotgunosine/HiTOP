"""Lookup tables aligning hitop/PHQ/GAD/BAARS item ids with item text."""
import pandas as pd


def load_item_lookup(item_lookup_path, cogmood_questions_path, measure='HiTOP'):
    """
    possible values for measure='BAARS-IV','GAD-7','PHQ-8','HiTOP'
    """
    # this is a table that aligns scale items with their corresponding questions
    htqs = pd.read_excel(item_lookup_path, skiprows=2,
                         names=['id', 'scale', 'item', '_0', '_1', '_2', '_3']).drop(['_0', '_1', '_2', '_3'], axis=1)
    # cmqs is a dataframe with items and responses
    # htcm is the same dataframe, but only displaying the requested measure's items
    cmqs = pd.read_csv(cogmood_questions_path)
    cmqs = cmqs.rename({'Unnamed: 0': 'id'}, axis=1)
    htcm = cmqs.query("measure == @measure")
    if measure == 'BAARS-IV':
        return htcm
    elif measure != 'HiTOP':
        m_string = measure.lower().split('-')[0]
        lut = {f'{m_string}_{ix + 1}': tt for ix, tt in enumerate(htcm.item.values)}
        return lut
    # this is a lookup table for subscales, items (sentence questions), and hitop ids
    item_lookup = htcm.loc[:, ['id', 'subscale', 'item']].merge(htqs.loc[:, ['id', 'item']], how='inner', on='item', suffixes=['_cm', '_ht'])
    item_lookup['htid'] = 'hitop' + item_lookup.id_ht.astype(str)
    return item_lookup


def build_luts(item_lookup_path, cogmood_questions_path):
    """Build every lookup the notebooks use in one call.

    Returns
    -------
    dict with keys:
        item_lookup : DataFrame (HiTOP subscale/item/htid table)
        item_lut    : dict hitop id -> item text
        phq_lut     : dict phq_N -> item text
        gad_lut     : dict gad_N -> item text
        baars_lut   : dict subscale -> {subscale_N -> item text}
    """
    item_lookup = load_item_lookup(item_lookup_path, cogmood_questions_path, 'HiTOP')
    item_lut = {row.htid: row.item for row in item_lookup.loc[:, ['item', 'htid']].itertuples()}
    phq_lut = load_item_lookup(item_lookup_path, cogmood_questions_path, 'PHQ-8')
    gad_lut = load_item_lookup(item_lookup_path, cogmood_questions_path, 'GAD-7')
    baars_lookup = load_item_lookup(item_lookup_path, cogmood_questions_path, 'BAARS-IV')
    baars_lut = {}
    for subscale in ['inattention', 'sct', 'hyperactivity', 'impulsivity']:
        if subscale == 'sct':
            ss_items = baars_lookup.loc[baars_lookup.subscale == 'Sluggish Cognitive Tempo', 'item'].values
        else:
            ss_items = baars_lookup.loc[baars_lookup.subscale == subscale.title(), 'item'].values
        baars_lut[subscale] = {f'{subscale}_{ix+1}': tt for ix, tt in enumerate(ss_items)}
    return dict(
        item_lookup=item_lookup,
        item_lut=item_lut,
        phq_lut=phq_lut,
        gad_lut=gad_lut,
        baars_lut=baars_lut,
    )


def check_hitop_ids(items_to_check, my_item_lookup):
    # checks what item ids mean what
    for i in items_to_check:
        a = repr(my_item_lookup.loc[my_item_lookup['htid'] == 'hitop'+i]['htid']).split(' ', 1)[1]
        aa = str(a).split('\n')[0]
        b = repr(my_item_lookup.loc[my_item_lookup['htid'] == 'hitop'+i]['item']).split(' ', 1)[1]
        bb = str(b).split('\n')[0]
        print(aa+bb)
    print('\n')
