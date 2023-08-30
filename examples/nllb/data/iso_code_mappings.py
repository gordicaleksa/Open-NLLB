import os

# There are some ambiguous langs in the dictionary below:
# ace -> ['ace_Arab', 'ace_Latn']
# bjn -> ['bjn_Arab', 'bjn_Latn']
# kas -> ['kas_Arab', 'kas_Deva']
# knc -> ['knc_Arab', 'knc_Latn']
# taq -> ['taq_Latn', 'taq_Tfng']
# zho -> ['zho_Hans', 'zho_Hant']

AMBIGUOUS_ISO_639_3_CODES = ['ace', 'bjn', 'kas', 'knc', 'taq', 'zho']

ISO_639_3_TO_BCP_47 = {
    "ace": [
        "ace_Arab",
        "ace_Latn"
    ],
    "acm": [
        "acm_Arab"
    ],
    "acq": [
        "acq_Arab"
    ],
    "aeb": [
        "aeb_Arab"
    ],
    "afr": [
        "afr_Latn"
    ],
    "ajp": [
        "ajp_Arab"
    ],
    "aka": [
        "aka_Latn"
    ],
    "amh": [
        "amh_Ethi"
    ],
    "apc": [
        "apc_Arab"
    ],
    # Manually added after analyzing tico dataset and seeing their README (we also ran the text through HuggingFace hosted fasttext model and it gave us MSA as well (modern standard arabic))
    "ara": [
        "arb_Arab"
    ],
    "arb": [
        "arb_Arab"
    ],
    "ars": [
        "ars_Arab"
    ],
    "ary": [
        "ary_Arab"
    ],
    "arz": [
        "arz_Arab"
    ],
    "asm": [
        "asm_Beng"
    ],
    "ast": [
        "ast_Latn"
    ],
    "awa": [
        "awa_Deva"
    ],
    "ayr": [
        "ayr_Latn"
    ],
    "azb": [
        "azb_Arab"
    ],
    # Manually added after analyzing til dataset and seeing it's Latin script (although it looks like Cyrl as well?)
    "aze": [
        "azj_Latn"
    ],
    "azj": [
        "azj_Latn"
    ],
    "bak": [
        "bak_Cyrl"
    ],
    "bam": [
        "bam_Latn"
    ],
    "ban": [
        "ban_Latn"
    ],
    "bel": [
        "bel_Cyrl"
    ],
    "bem": [
        "bem_Latn"
    ],
    "ben": [
        "ben_Beng"
    ],
    "bho": [
        "bho_Deva"
    ],
    "bjn": [
        "bjn_Arab",
        "bjn_Latn"
    ],
    "bod": [
        "bod_Tibt"
    ],
    "bos": [
        "bos_Latn"
    ],
    "bug": [
        "bug_Latn"
    ],
    "bul": [
        "bul_Cyrl"
    ],
    "cat": [
        "cat_Latn"
    ],
    "ceb": [
        "ceb_Latn"
    ],
    "ces": [
        "ces_Latn"
    ],
    "cjk": [
        "cjk_Latn"
    ],
    "ckb": [
        "ckb_Arab"
    ],
    "crh": [
        "crh_Latn"
    ],
    "cym": [
        "cym_Latn"
    ],
    "dan": [
        "dan_Latn"
    ],
    "deu": [
        "deu_Latn"
    ],
    # Manually added after analyzing tico dataset using fasttext model (https://huggingface.co/facebook/fasttext-language-identification)
    "din": [
        "dik_Latn"
    ],
    "dik": [
        "dik_Latn"
    ],
    "dyu": [
        "dyu_Latn"
    ],
    "dzo": [
        "dzo_Tibt"
    ],
    "ell": [
        "ell_Grek"
    ],
    "eng": [
        "eng_Latn"
    ],
    "epo": [
        "epo_Latn"
    ],
    "est": [
        "est_Latn"
    ],
    "eus": [
        "eus_Latn"
    ],
    "ewe": [
        "ewe_Latn"
    ],
    "fao": [
        "fao_Latn"
    ],
    # Manually added after analyzing tico dataset and seeing they have "fas" and "prs", thus I concluded that "fas" is actually "pes"
    "fas": [
        "pes_Arab"
    ],
    "pes": [
        "pes_Arab"
    ],
    "fij": [
        "fij_Latn"
    ],
    "fin": [
        "fin_Latn"
    ],
    "fon": [
        "fon_Latn"
    ],
    "fra": [
        "fra_Latn"
    ],
    "fur": [
        "fur_Latn"
    ],
    "fuv": [
        "fuv_Latn"
    ],
    "gla": [
        "gla_Latn"
    ],
    "gle": [
        "gle_Latn"
    ],
    "glg": [
        "glg_Latn"
    ],
    "grn": [
        "grn_Latn"
    ],
    "guj": [
        "guj_Gujr"
    ],
    "hat": [
        "hat_Latn"
    ],
    "hau": [
        "hau_Latn"
    ],
    "heb": [
        "heb_Hebr"
    ],
    "hin": [
        "hin_Deva"
    ],
    "hne": [
        "hne_Deva"
    ],
    "hrv": [
        "hrv_Latn"
    ],
    "hun": [
        "hun_Latn"
    ],
    "hye": [
        "hye_Armn"
    ],
    "ibo": [
        "ibo_Latn"
    ],
    "ilo": [
        "ilo_Latn"
    ],
    "ind": [
        "ind_Latn"
    ],
    "isl": [
        "isl_Latn"
    ],
    "ita": [
        "ita_Latn"
    ],
    "jav": [
        "jav_Latn"
    ],
    "jpn": [
        "jpn_Jpan"
    ],
    "kab": [
        "kab_Latn"
    ],
    "kac": [
        "kac_Latn"
    ],
    "kam": [
        "kam_Latn"
    ],
    "kan": [
        "kan_Knda"
    ],
    "kas": [
        "kas_Arab",
        "kas_Deva"
    ],
    "kat": [
        "kat_Geor"
    ],
    "knc": [
        "knc_Arab",
        "knc_Latn"
    ],
    "kaz": [
        "kaz_Cyrl"
    ],
    "kbp": [
        "kbp_Latn"
    ],
    "kea": [
        "kea_Latn"
    ],
    "khm": [
        "khm_Khmr"
    ],
    "kik": [
        "kik_Latn"
    ],
    "kin": [
        "kin_Latn"
    ],
    "kir": [
        "kir_Cyrl"
    ],
    "kmb": [
        "kmb_Latn"
    ],
    "kon": [
        "kon_Latn"
    ],
    "kor": [
        "kor_Hang"
    ],
    "kmr": [
        "kmr_Latn"
    ],
    "lao": [
        "lao_Laoo"
    ],
    "lvs": [
        "lvs_Latn"
    ],
    "lij": [
        "lij_Latn"
    ],
    "lim": [
        "lim_Latn"
    ],
    "lin": [
        "lin_Latn"
    ],
    "lit": [
        "lit_Latn"
    ],
    "lmo": [
        "lmo_Latn"
    ],
    "ltg": [
        "ltg_Latn"
    ],
    "ltz": [
        "ltz_Latn"
    ],
    "lua": [
        "lua_Latn"
    ],
    # Manually added after analyzing tico dataset using fasttext model (https://huggingface.co/facebook/fasttext-language-identification) also reading this helped: https://tico-19.github.io/
    "gag": [
        "lug_Latn"
    ],
    "lug": [
        "lug_Latn"
    ],
    "luo": [
        "luo_Latn"
    ],
    "lus": [
        "lus_Latn"
    ],
    "mag": [
        "mag_Deva"
    ],
    "mai": [
        "mai_Deva"
    ],
    "mal": [
        "mal_Mlym"
    ],
    "mar": [
        "mar_Deva"
    ],
    "min": [
        "min_Latn"
    ],
    "mkd": [
        "mkd_Cyrl"
    ],
    "plt": [
        "plt_Latn"
    ],
    "mlt": [
        "mlt_Latn"
    ],
    "mni": [
        "mni_Beng"
    ],
    "khk": [
        "khk_Cyrl"
    ],
    "mos": [
        "mos_Latn"
    ],
    "mri": [
        "mri_Latn"
    ],
    # Manually added after analyzing tico dataset using fasttext model (https://huggingface.co/facebook/fasttext-language-identification)
    "msa": [
        "zsm_Latn"
    ],
    "zsm": [
        "zsm_Latn"
    ],
    "mya": [
        "mya_Mymr"
    ],
    "nld": [
        "nld_Latn"
    ],
    "nno": [
        "nno_Latn"
    ],
    "nob": [
        "nob_Latn"
    ],
    "npi": [
        "npi_Deva"
    ],
    "nso": [
        "nso_Latn"
    ],
    "nus": [
        "nus_Latn"
    ],
    "nya": [
        "nya_Latn"
    ],
    "oci": [
        "oci_Latn"
    ],
    # Manually added as we assume we only have gaz_Latn, orm is a macro-lang.
    "orm": [
        "gaz_Latn"
    ],
    "gaz": [
        "gaz_Latn"
    ],
    # Manually added as we assume we only have ory_Orya, ori is a macro-lang (has 2 langs).
    "ori": [
        "ory_Orya"
    ],
    "ory": [
        "ory_Orya"
    ],
    "pag": [
        "pag_Latn"
    ],
    "pan": [
        "pan_Guru"
    ],
    "pap": [
        "pap_Latn"
    ],
    "pol": [
        "pol_Latn"
    ],
    "por": [
        "por_Latn"
    ],
    "prs": [
        "prs_Arab"
    ],
    "pus": [
        "pbs_Arab"
    ],
    "pbt": [
        "pbt_Arab"
    ],
    "quy": [
        "quy_Latn"
    ],
    "ron": [
        "ron_Latn"
    ],
    "run": [
        "run_Latn"
    ],
    "rus": [
        "rus_Cyrl"
    ],
    "sag": [
        "sag_Latn"
    ],
    "san": [
        "san_Deva"
    ],
    "sat": [
        "sat_Olck"
    ],
    "scn": [
        "scn_Latn"
    ],
    "shn": [
        "shn_Mymr"
    ],
    "sin": [
        "sin_Sinh"
    ],
    "slk": [
        "slk_Latn"
    ],
    "slv": [
        "slv_Latn"
    ],
    "smo": [
        "smo_Latn"
    ],
    "sna": [
        "sna_Latn"
    ],
    "snd": [
        "snd_Arab"
    ],
    "som": [
        "som_Latn"
    ],
    "sot": [
        "sot_Latn"
    ],
    "spa": [
        "spa_Latn"
    ],
    "als": [
        "als_Latn"
    ],
    "srd": [
        "srd_Latn"
    ],
    "srp": [
        "srp_Cyrl"
    ],
    "ssw": [
        "ssw_Latn"
    ],
    "sun": [
        "sun_Latn"
    ],
    "swe": [
        "swe_Latn"
    ],
    "swh": [
        "swh_Latn"
    ],
    "szl": [
        "szl_Latn"
    ],
    "tam": [
        "tam_Taml"
    ],
    "tat": [
        "tat_Cyrl"
    ],
    "tel": [
        "tel_Telu"
    ],
    "tgk": [
        "tgk_Cyrl"
    ],
    "tgl": [
        "tgl_Latn"
    ],
    "tha": [
        "tha_Thai"
    ],
    "tir": [
        "tir_Ethi"
    ],
    "taq": [
        "taq_Latn",
        "taq_Tfng"
    ],
    "tpi": [
        "tpi_Latn"
    ],
    "tsn": [
        "tsn_Latn"
    ],
    "tso": [
        "tso_Latn"
    ],
    "tuk": [
        "tuk_Latn"
    ],
    "tum": [
        "tum_Latn"
    ],
    "tur": [
        "tur_Latn"
    ],
    "twi": [
        "twi_Latn"
    ],
    "tzm": [
        "tzm_Tfng"
    ],
    "uig": [
        "uig_Arab"
    ],
    "ukr": [
        "ukr_Cyrl"
    ],
    "umb": [
        "umb_Latn"
    ],
    "urd": [
        "urd_Arab"
    ],
    # Manually added (til dataset) as we assume we only have Northern Uzbek (uzn) the Southern variant uses Arabic script.
    "uzb": [
        "uzn_Latn"
    ],
    "uzn": [
        "uzn_Latn"
    ],
    "vec": [
        "vec_Latn"
    ],
    "vie": [
        "vie_Latn"
    ],
    "war": [
        "war_Latn"
    ],
    "wol": [
        "wol_Latn"
    ],
    "xho": [
        "xho_Latn"
    ],
    "ydd": [
        "ydd_Hebr"
    ],
    "yor": [
        "yor_Latn"
    ],
    "yue": [
        "yue_Hant"
    ],
    "zho": [
        "zho_Hans",
        "zho_Hant"
    ],
    "zul": [
        "zul_Latn"
    ]
}

# TODO(gordicaleksa): ideally construct a complete table for all 202 supported langs.
ISO_CODE_MAPPER_1_TO_3 = {
    'or' : 'ori',
    'gu' : 'guj',
    'bn' : 'ben',
    'en' : 'eng',
    'ta' : 'tam',
    'mr' : 'mar',
    'pa' : 'pan',
    'hi' : 'hin',
    'ml' : 'mal',
    'kn' : 'kan',
    'te' : 'tel',
    'fr' : 'fra',
}

# Created by manual inspection by gordicaleksa.
FILTERED_LANG_CODES = ['slr', 'kum', 'sah', 'alt', 'tyv', 'kaa', 'kjh', 'cjs', 'chv', 'krc', 'tir_ER', 'aar', 'nde', 'ven', 'uum', 'gag']

# def build_iso_3_to_bcp_mapping():
#     from collections import defaultdict

#     langs_str = "ace_Arab,ace_Latn,acm_Arab,acq_Arab,aeb_Arab,afr_Latn,ajp_Arab,aka_Latn,amh_Ethi,apc_Arab,arb_Arab,ars_Arab,ary_Arab,arz_Arab,asm_Beng,ast_Latn,awa_Deva,ayr_Latn,azb_Arab,azj_Latn,bak_Cyrl,bam_Latn,ban_Latn,bel_Cyrl,bem_Latn,ben_Beng,bho_Deva,bjn_Arab,bjn_Latn,bod_Tibt,bos_Latn,bug_Latn,bul_Cyrl,cat_Latn,ceb_Latn,ces_Latn,cjk_Latn,ckb_Arab,crh_Latn,cym_Latn,dan_Latn,deu_Latn,dik_Latn,dyu_Latn,dzo_Tibt,ell_Grek,eng_Latn,epo_Latn,est_Latn,eus_Latn,ewe_Latn,fao_Latn,pes_Arab,fij_Latn,fin_Latn,fon_Latn,fra_Latn,fur_Latn,fuv_Latn,gla_Latn,gle_Latn,glg_Latn,grn_Latn,guj_Gujr,hat_Latn,hau_Latn,heb_Hebr,hin_Deva,hne_Deva,hrv_Latn,hun_Latn,hye_Armn,ibo_Latn,ilo_Latn,ind_Latn,isl_Latn,ita_Latn,jav_Latn,jpn_Jpan,kab_Latn,kac_Latn,kam_Latn,kan_Knda,kas_Arab,kas_Deva,kat_Geor,knc_Arab,knc_Latn,kaz_Cyrl,kbp_Latn,kea_Latn,khm_Khmr,kik_Latn,kin_Latn,kir_Cyrl,kmb_Latn,kon_Latn,kor_Hang,kmr_Latn,lao_Laoo,lvs_Latn,lij_Latn,lim_Latn,lin_Latn,lit_Latn,lmo_Latn,ltg_Latn,ltz_Latn,lua_Latn,lug_Latn,luo_Latn,lus_Latn,mag_Deva,mai_Deva,mal_Mlym,mar_Deva,min_Latn,mkd_Cyrl,plt_Latn,mlt_Latn,mni_Beng,khk_Cyrl,mos_Latn,mri_Latn,zsm_Latn,mya_Mymr,nld_Latn,nno_Latn,nob_Latn,npi_Deva,nso_Latn,nus_Latn,nya_Latn,oci_Latn,gaz_Latn,ory_Orya,pag_Latn,pan_Guru,pap_Latn,pol_Latn,por_Latn,prs_Arab,pbt_Arab,quy_Latn,ron_Latn,run_Latn,rus_Cyrl,sag_Latn,san_Deva,sat_Olck,scn_Latn,shn_Mymr,sin_Sinh,slk_Latn,slv_Latn,smo_Latn,sna_Latn,snd_Arab,som_Latn,sot_Latn,spa_Latn,als_Latn,srd_Latn,srp_Cyrl,ssw_Latn,sun_Latn,swe_Latn,swh_Latn,szl_Latn,tam_Taml,tat_Cyrl,tel_Telu,tgk_Cyrl,tgl_Latn,tha_Thai,tir_Ethi,taq_Latn,taq_Tfng,tpi_Latn,tsn_Latn,tso_Latn,tuk_Latn,tum_Latn,tur_Latn,twi_Latn,tzm_Tfng,uig_Arab,ukr_Cyrl,umb_Latn,urd_Arab,uzn_Latn,vec_Latn,vie_Latn,war_Latn,wol_Latn,xho_Latn,ydd_Hebr,yor_Latn,yue_Hant,zho_Hans,zho_Hant,zul_Latn"
#     langs = langs_str.split(',')

#     ISO_639_3_TO_BCP_47 = defaultdict(list)

#     for lang in langs:
#         lang, script = lang.split('_')
#         ISO_639_3_TO_BCP_47[lang].append(f'{lang}_{script}')

#     for key, value in ISO_639_3_TO_BCP_47.items():
#         if len(value) > 1:
#             print(key, value)
#     # Save dictionary as json
#     import json
#     with open('ISO_639_3_TO_BCP_47.json', 'w') as f:
#         json.dump(ISO_639_3_TO_BCP_47, f, indent=4)


extended_langs_path = os.path.join(os.path.dirname(__file__), 'extended_langs.txt')
with open(extended_langs_path, 'r') as f:
    SUPPORTED_ISO_3_LANG_CODES_AND_SCRIPT = f.readlines()[0].strip().split(',')
    SUPPORTED_ISO_3_LANG_CODES = [lang.split('_')[0] for lang in SUPPORTED_ISO_3_LANG_CODES_AND_SCRIPT]

def retrieve_supported_files_and_directions(files):
    new_files_and_lang_directions = []

    for file in files:
        suffix = file.split('.')[-1]
        if suffix in FILTERED_LANG_CODES:
            continue
        if file in SUPPORTED_ISO_3_LANG_CODES_AND_SCRIPT:
            new_files_and_lang_directions.append((file, file.split('_')[0]))
        elif suffix in SUPPORTED_ISO_3_LANG_CODES_AND_SCRIPT:
            new_files_and_lang_directions.append((file, suffix.split('_')[0]))
        elif suffix in SUPPORTED_ISO_3_LANG_CODES:
            new_files_and_lang_directions.append((file, suffix))
        elif suffix in ISO_CODE_MAPPER_1_TO_3.keys():
            new_files_and_lang_directions.append((file, ISO_CODE_MAPPER_1_TO_3[suffix]))
        else:
            print(f'Skipping {file}.')

    return new_files_and_lang_directions

#
# Below data was scraped from the web in order to construct the mapping but at the end we just created the above
# mapping manually and ignored everything below.
#

# new_dict = {}
# for lang in supported_lang_codes:
#     if not lang in ISO_2_TO_1_MAPPING and not lang in ISO_2_TO_1_MAPPING_2:
#         print(f'Lang {lang} not in ISO_2_TO_1_MAPPING.')
#         continue

#     if lang in ISO_2_TO_1_MAPPING:
#         new_dict[lang] = ISO_2_TO_1_MAPPING[lang]
#         if len(ISO_2_TO_1_MAPPING[lang]) != 2:
#             print(f'[1] Got a wrong length replacement code for lang {lang} -> {ISO_2_TO_1_MAPPING[lang]}.')
#     else:
#         new_dict[lang] = ISO_2_TO_1_MAPPING_2[lang]
#         if len(ISO_2_TO_1_MAPPING_2[lang]) != 2:
#             print(f'[2] Got a wrong length replacement code for lang {lang} -> {ISO_2_TO_1_MAPPING_2[lang]}.')

# print(len(new_dict))

# Found here: https://github.com/rspeer/langcodes/blob/master/langcodes/data_dicts.py
# ISO_2_TO_1_MAPPING_2 = {
#     'aa-saaho': 'ssy',
#     'aam': 'aas',
#     'aar': 'aa',
#     'abk': 'ab',
#     'adp': 'dz',
#     'afr': 'af',
#     'agp': 'apf',
#     'ais': 'ami',
#     'aka': 'ak',
#     'alb': 'sq',
#     'amh': 'am',
#     'ara': 'ar',
#     'arg': 'an',
#     'arm': 'hy',
#     'art-lojban': 'jbo',
#     'asd': 'snz',
#     'asm': 'as',
#     'aue': 'ktz',
#     'ava': 'av',
#     'ave': 'ae',
#     'aym': 'ay',
#     'ayx': 'nun',
#     'aze': 'az',
#     'bak': 'ba',
#     'bam': 'bm',
#     'baq': 'eu',
#     'baz': 'nvo',
#     'bel': 'be',
#     'ben': 'bn',
#     'bgm': 'bcg',
#     'bhk': 'fbl',
#     'bic': 'bir',
#     'bih': 'bh',
#     'bis': 'bi',
#     'bjd': 'drl',
#     'bjq': 'bzc',
#     'bkb': 'ebk',
#     'blg': 'iba',
#     'bod': 'bo',
#     'bos': 'bs',
#     'bre': 'br',
#     'btb': 'beb',
#     'bul': 'bg',
#     'bur': 'my',
#     'cat': 'ca',
#     'ccq': 'rki',
#     'cel-gaulish': 'xtg',
#     'ces': 'cs',
#     'cha': 'ch',
#     'che': 'ce',
#     'chi': 'zh',
#     'chu': 'cu',
#     'chv': 'cv',
#     'cjr': 'mom',
#     'cka': 'cmr',
#     'cmk': 'xch',
#     'cnr': 'sr-ME',
#     'cor': 'kw',
#     'cos': 'co',
#     'coy': 'pij',
#     'cqu': 'quh',
#     'cre': 'cr',
#     'cym': 'cy',
#     'cze': 'cs',
#     'daf': 'dnj',
#     'dan': 'da',
#     'dap': 'njz',
#     'deu': 'de',
#     'dit': 'dif',
#     'div': 'dv',
#     'djl': 'dze',
#     'dkl': 'aqd',
#     'drh': 'mn',
#     'drr': 'kzk',
#     'drw': 'fa-AF',
#     'dud': 'uth',
#     'duj': 'dwu',
#     'dut': 'nl',
#     'dwl': 'dbt',
#     'dzo': 'dz',
#     'ell': 'el',
#     'elp': 'amq',
#     'en-gb-oed': 'en-GB-oxendict',
#     'eng': 'en',
#     'epo': 'eo',
#     'est': 'et',
#     'eus': 'eu',
#     'ewe': 'ee',
#     'fao': 'fo',
#     'fas': 'fa',
#     'fij': 'fj',
#     'fin': 'fi',
#     'fra': 'fr',
#     'fre': 'fr',
#     'fry': 'fy',
#     'ful': 'ff',
#     'gav': 'dev',
#     'gbc': 'wny',
#     'geo': 'ka',
#     'ger': 'de',
#     'gfx': 'vaj',
#     'ggn': 'gvr',
#     'ggo': 'esg',
#     'ggr': 'gtu',
#     'gio': 'aou',
#     'gla': 'gd',
#     'gle': 'ga',
#     'glg': 'gl',
#     'gli': 'kzk',
#     'glv': 'gv',
#     'gre': 'el',
#     'grn': 'gn',
#     'gti': 'nyc',
#     'guj': 'gu',
#     'guv': 'duz',
#     'hat': 'ht',
#     'hau': 'ha',
#     'hbs': 'sr-Latn',
#     'heb': 'he',
#     'her': 'hz',
#     'hin': 'hi',
#     'hmo': 'ho',
#     'hrr': 'jal',
#     'hrv': 'hr',
#     'hun': 'hu',
#     'hy-arevmda': 'hyw',
#     'hye': 'hy',
#     'i-ami': 'ami',
#     'i-bnn': 'bnn',
#     'i-default': 'en-x-i-default',
#     'i-enochian': 'und-x-i-enochian',
#     'i-hak': 'hak',
#     'i-klingon': 'tlh',
#     'i-lux': 'lb',
#     'i-mingo': 'see-x-i-mingo',
#     'i-navajo': 'nv',
#     'i-pwn': 'pwn',
#     'i-tao': 'tao',
#     'i-tay': 'tay',
#     'i-tsu': 'tsu',
#     'ibi': 'opa',
#     'ibo': 'ig',
#     'ice': 'is',
#     'ido': 'io',
#     'iii': 'ii',
#     'iku': 'iu',
#     'ile': 'ie',
#     'ill': 'ilm',
#     'ilw': 'gal',
#     'in': 'id',
#     'ina': 'ia',
#     'ind': 'id',
#     'ipk': 'ik',
#     'isl': 'is',
#     'ita': 'it',
#     'iw': 'he',
#     'izi': 'eza',
#     'jar': 'jgk',
#     'jav': 'jv',
#     'jeg': 'oyb',
#     'ji': 'yi',
#     'jpn': 'ja',
#     'jw': 'jv',
#     'kal': 'kl',
#     'kan': 'kn',
#     'kas': 'ks',
#     'kat': 'ka',
#     'kau': 'kr',
#     'kaz': 'kk',
#     'kdv': 'zkd',
#     'kgc': 'tdf',
#     'kgd': 'ncq',
#     'kgh': 'kml',
#     'khm': 'km',
#     'kik': 'ki',
#     'kin': 'rw',
#     'kir': 'ky',
#     'koj': 'kwv',
#     'kom': 'kv',
#     'kon': 'kg',
#     'kor': 'ko',
#     'kpp': 'jkm',
#     'krm': 'bmf',
#     'ktr': 'dtp',
#     'kua': 'kj',
#     'kur': 'ku',
#     'kvs': 'gdj',
#     'kwq': 'yam',
#     'kxe': 'tvd',
#     'kxl': 'kru',
#     'kzh': 'dgl',
#     'kzj': 'dtp',
#     'kzt': 'dtp',
#     'lao': 'lo',
#     'lat': 'la',
#     'lav': 'lv',
#     'leg': 'enl',
#     'lii': 'raq',
#     'lim': 'li',
#     'lin': 'ln',
#     'lit': 'lt',
#     'llo': 'ngt',
#     'lmm': 'rmx',
#     'ltz': 'lb',
#     'lub': 'lu',
#     'lug': 'lg',
#     'mac': 'mk',
#     'mah': 'mh',
#     'mal': 'ml',
#     'mao': 'mi',
#     'mar': 'mr',
#     'may': 'ms',
#     'meg': 'cir',
#     'mgx': 'jbk',
#     'mkd': 'mk',
#     'mlg': 'mg',
#     'mlt': 'mt',
#     'mnt': 'wnn',
#     'mo': 'ro',
#     'mof': 'xnt',
#     'mol': 'mo',
#     'mon': 'mn',
#     'mri': 'mi',
#     'msa': 'ms',
#     'mst': 'mry',
#     'mwd': 'dmw',
#     'mwj': 'vaj',
#     'mya': 'my',
#     'myd': 'aog',
#     'myt': 'mry',
#     'nad': 'xny',
#     'nau': 'na',
#     'nav': 'nv',
#     'nbf': 'nru',
#     'nbl': 'nr',
#     'nbx': 'ekc',
#     'ncp': 'kdz',
#     'nde': 'nd',
#     'ndo': 'ng',
#     'nep': 'ne',
#     'nld': 'nl',
#     'nln': 'azd',
#     'nlr': 'nrk',
#     'nno': 'nn',
#     'nns': 'nbr',
#     'nnx': 'ngv',
#     'no-bok': 'nb',
#     'no-bokmal': 'nb',
#     'no-nyn': 'nn',
#     'no-nynorsk': 'nn',
#     'nob': 'nb',
#     'noo': 'dtd',
#     'nor': 'no',
#     'nts': 'pij',
#     'nxu': 'bpp',
#     'nya': 'ny',
#     'oci': 'oc',
#     'oji': 'oj',
#     'ori': 'or',
#     'orm': 'om',
#     'oss': 'os',
#     'oun': 'vaj',
#     'pan': 'pa',
#     'pat': 'kxr',
#     'pcr': 'adx',
#     'per': 'fa',
#     'pli': 'pi',
#     'pmc': 'huw',
#     'pmu': 'phr',
#     'pol': 'pl',
#     'por': 'pt',
#     'ppa': 'bfy',
#     'ppr': 'lcq',
#     'prs': 'fa-AF',
#     'pry': 'prt',
#     'pus': 'ps',
#     'puz': 'pub',
#     'que': 'qu',
#     'rmr': 'emx',
#     'roh': 'rm',
#     'ron': 'ro',
#     'root': 'und',
#     'rum': 'ro',
#     'run': 'rn',
#     'rus': 'ru',
#     'sag': 'sg',
#     'san': 'sa',
#     'sap': 'aqt',
#     'sca': 'hle',
#     'scc': 'sr',
#     'scr': 'hr',
#     'sgl': 'isk',
#     'sgn-be-fr': 'sfb',
#     'sgn-be-nl': 'vgt',
#     'sgn-br': 'bzs',
#     'sgn-ch-de': 'sgg',
#     'sgn-co': 'csn',
#     'sgn-de': 'gsg',
#     'sgn-dk': 'dsl',
#     'sgn-es': 'ssp',
#     'sgn-fr': 'fsl',
#     'sgn-gb': 'bfi',
#     'sgn-gr': 'gss',
#     'sgn-ie': 'isg',
#     'sgn-it': 'ise',
#     'sgn-jp': 'jsl',
#     'sgn-mx': 'mfs',
#     'sgn-ni': 'ncs',
#     'sgn-nl': 'dse',
#     'sgn-no': 'nsi',
#     'sgn-pt': 'psr',
#     'sgn-se': 'swl',
#     'sgn-us': 'ase',
#     'sgn-za': 'sfs',
#     'sh': 'sr-Latn',
#     'sin': 'si',
#     'skk': 'oyb',
#     'slk': 'sk',
#     'slo': 'sk',
#     'slv': 'sl',
#     'sme': 'se',
#     'smo': 'sm',
#     'sna': 'sn',
#     'snd': 'sd',
#     'som': 'so',
#     'sot': 'st',
#     'spa': 'es',
#     'sqi': 'sq',
#     'srd': 'sc',
#     'srp': 'sr',
#     'ssw': 'ss',
#     'sul': 'sgd',
#     'sum': 'ulw',
#     'sun': 'su',
#     'swa': 'sw',
#     'swc': 'sw-CD',
#     'swe': 'sv',
#     'tah': 'ty',
#     'tam': 'ta',
#     'tat': 'tt',
#     'tdu': 'dtp',
#     'tel': 'te',
#     'tgg': 'bjp',
#     'tgk': 'tg',
#     'tgl': 'fil',
#     'tha': 'th',
#     'thc': 'tpo',
#     'thw': 'ola',
#     'thx': 'oyb',
#     'tib': 'bo',
#     'tid': 'itd',
#     'tie': 'ras',
#     'tir': 'ti',
#     'tkk': 'twm',
#     'tl': 'fil',
#     'tlw': 'weo',
#     'tmp': 'tyj',
#     'tne': 'kak',
#     'tnf': 'fa-AF',
#     'ton': 'to',
#     'tsf': 'taj',
#     'tsn': 'tn',
#     'tso': 'ts',
#     'tuk': 'tk',
#     'tur': 'tr',
#     'twi': 'tw',
#     'uig': 'ug',
#     'ukr': 'uk',
#     'und-aaland': 'und-AX',
#     'und-arevela': 'und',
#     'und-arevmda': 'und',
#     'und-bokmal': 'und',
#     'und-hakka': 'und',
#     'und-hepburn-heploc': 'und-alalc97',
#     'und-lojban': 'und',
#     'und-nynorsk': 'und',
#     'und-saaho': 'und',
#     'und-xiang': 'und',
#     'unp': 'wro',
#     'uok': 'ema',
#     'urd': 'ur',
#     'uzb': 'uz',
#     'ven': 've',
#     'vie': 'vi',
#     'vol': 'vo',
#     'wel': 'cy',
#     'wgw': 'wgb',
#     'wit': 'nol',
#     'wiw': 'nwo',
#     'wln': 'wa',
#     'wol': 'wo',
#     'xba': 'cax',
#     'xho': 'xh',
#     'xia': 'acn',
#     'xkh': 'waw',
#     'xrq': 'dmw',
#     'xsj': 'suj',
#     'ybd': 'rki',
#     'yen': 'ynq',
#     'yid': 'yi',
#     'yiy': 'yrm',
#     'yma': 'lrr',
#     'ymt': 'mtm',
#     'yor': 'yo',
#     'yos': 'zom',
#     'yuu': 'yug',
#     'zh-cmn': 'zh',
#     'zh-cmn-hans': 'zh-Hans',
#     'zh-cmn-hant': 'zh-Hant',
#     'zh-gan': 'gan',
#     'zh-guoyu': 'zh',
#     'zh-hakka': 'hak',
#     'zh-min': 'nan-x-zh-min',
#     'zh-min-nan': 'nan',
#     'zh-wuu': 'wuu',
#     'zh-xiang': 'hsn',
#     'zh-yue': 'yue',
#     'zha': 'za',
#     'zho': 'zh',
#     'zir': 'scv',
#     'zul': 'zu',
# }

# ISO_2_TO_1_MAPPING_1 = {'aar': 'aa', 'abk': 'ab', 'afr': 'af', 'aka': 'ak', 'alb': 'sq', 'amh': 'am', 'ara': 'ar', 'arg': 'an', 'arm': 'hy', 'asm': 'as', 'ava': 'av', 'ave': 'ae', 'aym': 'ay', 'aze': 'az', 'bak': 'ba', 'bam': 'bm', 'baq': 'eu', 'bel': 'be', 'ben': 'bn', 'bih': 'bh', 'bis': 'bi', 'tib': 'bo', 'bos': 'bs', 'bre': 'br', 'bul': 'bg', 'bur': 'my', 'cat': 'ca', 'cze': 'cs', 'cha': 'ch', 'che': 'ce', 'chi': 'zh', 'chu': 'cu', 'chv': 'cv', 'cor': 'kw', 'cos': 'co', 'cre': 'cr', 'wel': 'cy', 'dan': 'da', 'ger': 'de', 'div': 'dv', 'dut': 'nl', 'dzo': 'dz', 'gre': 'el', 'eng': 'en', 'epo': 'eo', 'est': 'et', 'ewe': 'ee', 'fao': 'fo', 'per': 'fa', 'fij': 'fj', 'fin': 'fi', 'fre': 'fr', 'fry': 'fy', 'ful': 'ff', 'geo': 'ka', 'gla': 'gd', 'gle': 'ga', 'glg': 'gl', 'glv': 'gv', 'grn': 'gn', 'guj': 'gu', 'hat': 'ht', 'hau': 'ha', 'heb': 'he', 'her': 'hz', 'hin': 'hi', 'hmo': 'ho', 'hrv': 'hr', 'hun': 'hu', 'ibo': 'ig', 'ice': 'is', 'ido': 'io', 'iii': 'ii', 'iku': 'iu', 'ile': 'ie', 'ina': 'ia', 'ind': 'id', 'ipk': 'ik', 'ita': 'it', 'jav': 'jv', 'jpn': 'ja', 'kal': 'kl', 'kan': 'kn', 'kas': 'ks', 'kau': 'kr', 'kaz': 'kk', 'khm': 'km', 'kik': 'ki', 'kin': 'rw', 'kir': 'ky', 'kom': 'kv', 'kon': 'kg', 'kor': 'ko', 'kua': 'kj', 'kur': 'ku', 'lao': 'lo', 'lat': 'la', 'lav': 'lv', 'lim': 'li', 'lin': 'ln', 'lit': 'lt', 'ltz': 'lb', 'lub': 'lu', 'lug': 'lg', 'mac': 'mk', 'mah': 'mh', 'mal': 'ml', 'mao': 'mi', 'mar': 'mr', 'may': 'ms', 'mlg': 'mg', 'mlt': 'mt', 'mon': 'mn', 'nau': 'na', 'nav': 'nv', 'nbl': 'nr', 'nde': 'nd', 'ndo': 'ng', 'nep': 'ne', 'nno': 'nn', 'nob': 'nb', 'nor': 'no', 'nya': 'ny', 'oci': 'oc', 'oji': 'oj', 'ori': 'or', 'orm': 'om', 'oss': 'os', 'pan': 'pa', 'pli': 'pi', 'pol': 'pl', 'por': 'pt', 'pus': 'ps', 'que': 'qu', 'roh': 'rm', 'rum': 'ro', 'run': 'rn', 'rus': 'ru', 'sag': 'sg', 'san': 'sa', 'sin': 'si', 'slo': 'sk', 'slv': 'sl', 'sme': 'se', 'smo': 'sm', 'sna': 'sn', 'snd': 'sd', 'som': 'so', 'sot': 'st', 'spa': 'es', 'srd': 'sc', 'srp': 'sr', 'ssw': 'ss', 'sun': 'su', 'swa': 'sw', 'swe': 'sv', 'tah': 'ty', 'tam': 'ta', 'tat': 'tt', 'tel': 'te', 'tgk': 'tg', 'tgl': 'tl', 'tha': 'th', 'tir': 'ti', 'ton': 'to', 'tsn': 'tn', 'tso': 'ts', 'tuk': 'tk', 'tur': 'tr', 'twi': 'tw', 'uig': 'ug', 'ukr': 'uk', 'urd': 'ur', 'uzb': 'uz', 'ven': 've', 'vie': 'vi', 'vol': 'vo', 'wln': 'wa', 'wol': 'wo', 'xho': 'xh', 'yid': 'yi', 'yor': 'yo', 'zha': 'za', 'zul': 'zu'}

# Found it here: https://gist.github.com/kaisyu/6103312
# tmp = """{
#     {"aa", "aar"},
#     {"ab", "abk"},
#     {"af", "afr"},
#     {"ak", "aka"},
#     {"sq", "alb"},
#     {"am", "amh"},
#     {"ar", "ara"},
#     {"an", "arg"},
#     {"hy", "arm"},
#     {"as", "asm"},
#     {"av", "ava"},
#     {"ae", "ave"},
#     {"ay", "aym"},
#     {"az", "aze"},
#     {"ba", "bak"},
#     {"bm", "bam"},
#     {"eu", "baq"},
#     {"be", "bel"},
#     {"bn", "ben"},
#     {"bh", "bih"},
#     {"bi", "bis"},
#     {"bo", "tib"},
#     {"bs", "bos"},
#     {"br", "bre"},
#     {"bg", "bul"},
#     {"my", "bur"},
#     {"ca", "cat"},
#     {"cs", "cze"},
#     {"ch", "cha"},
#     {"ce", "che"},
#     {"zh", "chi"},
#     {"cu", "chu"},
#     {"cv", "chv"},
#     {"kw", "cor"},
#     {"co", "cos"},
#     {"cr", "cre"},
#     {"cy", "wel"},
#     {"cs", "cze"},
#     {"da", "dan"},
#     {"de", "ger"},
#     {"dv", "div"},
#     {"nl", "dut"},
#     {"dz", "dzo"},
#     {"el", "gre"},
#     {"en", "eng"},
#     {"eo", "epo"},
#     {"et", "est"},
#     {"eu", "baq"},
#     {"ee", "ewe"},
#     {"fo", "fao"},
#     {"fa", "per"},
#     {"fj", "fij"},
#     {"fi", "fin"},
#     {"fr", "fre"},
#     {"fr", "fre"},
#     {"fy", "fry"},
#     {"ff", "ful"},
#     {"ka", "geo"},
#     {"de", "ger"},
#     {"gd", "gla"},
#     {"ga", "gle"},
#     {"gl", "glg"},
#     {"gv", "glv"},
#     {"el", "gre"},
#     {"gn", "grn"},
#     {"gu", "guj"},
#     {"ht", "hat"},
#     {"ha", "hau"},
#     {"he", "heb"},
#     {"hz", "her"},
#     {"hi", "hin"},
#     {"ho", "hmo"},
#     {"hr", "hrv"},
#     {"hu", "hun"},
#     {"hy", "arm"},
#     {"ig", "ibo"},
#     {"is", "ice"},
#     {"io", "ido"},
#     {"ii", "iii"},
#     {"iu", "iku"},
#     {"ie", "ile"},
#     {"ia", "ina"},
#     {"id", "ind"},
#     {"ik", "ipk"},
#     {"is", "ice"},
#     {"it", "ita"},
#     {"jv", "jav"},
#     {"ja", "jpn"},
#     {"kl", "kal"},
#     {"kn", "kan"},
#     {"ks", "kas"},
#     {"ka", "geo"},
#     {"kr", "kau"},
#     {"kk", "kaz"},
#     {"km", "khm"},
#     {"ki", "kik"},
#     {"rw", "kin"},
#     {"ky", "kir"},
#     {"kv", "kom"},
#     {"kg", "kon"},
#     {"ko", "kor"},
#     {"kj", "kua"},
#     {"ku", "kur"},
#     {"lo", "lao"},
#     {"la", "lat"},
#     {"lv", "lav"},
#     {"li", "lim"},
#     {"ln", "lin"},
#     {"lt", "lit"},
#     {"lb", "ltz"},
#     {"lu", "lub"},
#     {"lg", "lug"},
#     {"mk", "mac"},
#     {"mh", "mah"},
#     {"ml", "mal"},
#     {"mi", "mao"},
#     {"mr", "mar"},
#     {"ms", "may"},
#     {"mk", "mac"},
#     {"mg", "mlg"},
#     {"mt", "mlt"},
#     {"mn", "mon"},
#     {"mi", "mao"},
#     {"ms", "may"},
#     {"my", "bur"},
#     {"na", "nau"},
#     {"nv", "nav"},
#     {"nr", "nbl"},
#     {"nd", "nde"},
#     {"ng", "ndo"},
#     {"ne", "nep"},
#     {"nl", "dut"},
#     {"nn", "nno"},
#     {"nb", "nob"},
#     {"no", "nor"},
#     {"ny", "nya"},
#     {"oc", "oci"},
#     {"oj", "oji"},
#     {"or", "ori"},
#     {"om", "orm"},
#     {"os", "oss"},
#     {"pa", "pan"},
#     {"fa", "per"},
#     {"pi", "pli"},
#     {"pl", "pol"},
#     {"pt", "por"},
#     {"ps", "pus"},
#     {"qu", "que"},
#     {"rm", "roh"},
#     {"ro", "rum"},
#     {"ro", "rum"},
#     {"rn", "run"},
#     {"ru", "rus"},
#     {"sg", "sag"},
#     {"sa", "san"},
#     {"si", "sin"},
#     {"sk", "slo"},
#     {"sk", "slo"},
#     {"sl", "slv"},
#     {"se", "sme"},
#     {"sm", "smo"},
#     {"sn", "sna"},
#     {"sd", "snd"},
#     {"so", "som"},
#     {"st", "sot"},
#     {"es", "spa"},
#     {"sq", "alb"},
#     {"sc", "srd"},
#     {"sr", "srp"},
#     {"ss", "ssw"},
#     {"su", "sun"},
#     {"sw", "swa"},
#     {"sv", "swe"},
#     {"ty", "tah"},
#     {"ta", "tam"},
#     {"tt", "tat"},
#     {"te", "tel"},
#     {"tg", "tgk"},
#     {"tl", "tgl"},
#     {"th", "tha"},
#     {"bo", "tib"},
#     {"ti", "tir"},
#     {"to", "ton"},
#     {"tn", "tsn"},
#     {"ts", "tso"},
#     {"tk", "tuk"},
#     {"tr", "tur"},
#     {"tw", "twi"},
#     {"ug", "uig"},
#     {"uk", "ukr"},
#     {"ur", "urd"},
#     {"uz", "uzb"},
#     {"ve", "ven"},
#     {"vi", "vie"},
#     {"vo", "vol"},
#     {"cy", "wel"},
#     {"wa", "wln"},
#     {"wo", "wol"},
#     {"xh", "xho"},
#     {"yi", "yid"},
#     {"yo", "yor"},
#     {"za", "zha"},
#     {"zh", "chi"},
#     {"zu", "zul"},
# }"""

# lines = tmp.split('\n')[1:-1]
# lines = [line.strip()[1:-2] for line in lines]
# lines = [line.replace('"', '').replace(' ', '').split(',') for line in lines]
# new_dict = {}
# for el in lines:
#     new_dict[el[1]] = el[0]
# print(len(new_dict))

# Found here: https://huggingface.co/datasets/allenai/nllb/blob/main/nllb_lang_pairs.py
# CCMATRIX_MAPPING = {
#     "afr_Latn": "af",
#     "als_Latn": "sq",
#     "amh_Ethi": "am",
#     "arb_Arab": "ar",
#     "ast_Latn": "ast",
#     "azj_Latn": "az",
#     "bel_Cyrl": "be",
#     "ben_Beng": "bn",
#     "bul_Cyrl": "bg",
#     "cat_Latn": "ca",
#     "ceb_Latn": "ceb",
#     "ces_Latn": "cs",
#     "cym_Latn": "cy",
#     "dan_Latn": "da",
#     "deu_Latn": "de",
#     "ell_Grek": "el",
#     "eng_Latn": "en",
#     "epo_Latn": "eo",
#     "est_Latn": "et",
#     "fin_Latn": "fi",
#     "fra_Latn": "fr",
#     "gaz_Latn": "om",
#     "gla_Latn": "gd",
#     "gle_Latn": "ga",
#     "glg_Latn": "gl",
#     "hau_Latn": "ha",
#     "heb_Hebr": "he",
#     "hin_Deva": "hi",
#     "hrv_Latn": "hr",
#     "hun_Latn": "hu",
#     "hye_Armn": "hy",
#     "ibo_Latn": "ig",
#     "ilo_Latn": "ilo",
#     "ind_Latn": "id",
#     "isl_Latn": "is",
#     "ita_Latn": "it",
#     "jav_Latn": "jv",
#     "jpn_Jpan": "ja",
#     "kat_Geor": "ka",
#     "kaz_Cyrl": "kk",
#     "khm_Khmr": "km",
#     "kor_Hang": "ko",
#     "lit_Latn": "lt",
#     "ltz_Latn": "lb",
#     "lug_Latn": "lg",
#     "lvs_Latn": "lv",
#     "mal_Mlym": "ml",
#     "mar_Deva": "mr",
#     "mkd_Cyrl": "mk",
#     "mya_Mymr": "my",
#     "nld_Latn": "nl",
#     "nob_Latn": "no",
#     "npi_Deva": "ne",
#     "oci_Latn": "oc",
#     "ory_Orya": "or",
#     "pes_Arab": "fa",
#     "plt_Latn": "mg",
#     "pol_Latn": "pl",
#     "por_Latn": "pt",
#     "ron_Latn": "ro",
#     "rus_Cyrl": "ru",
#     "sin_Sinh": "si",
#     "slk_Latn": "sk",
#     "slv_Latn": "sl",
#     "snd_Arab": "sd",
#     "som_Latn": "so",
#     "spa_Latn": "es",
#     "srp_Cyrl": "sr",
#     "sun_Latn": "su",
#     "swe_Latn": "sv",
#     "swh_Latn": "sw",
#     "tam_Taml": "ta",
#     "tat_Cyrl": "tt",
#     "tgl_Latn": "tl",
#     "tur_Latn": "tr",
#     "ukr_Cyrl": "uk",
#     "urd_Arab": "ur",
#     "uzn_Latn": "uz",
#     "vie_Latn": "vi",
#     "wol_Latn": "wo",
#     "xho_Latn": "xh",
#     "ydd_Hebr": "yi",
#     "yor_Latn": "yo",
#     "zho_Hans": "zh",
#     "zsm_Latn": "ms",
#     "zul_Latn": "zu",
# }

# ISO_2_TO_1_MAPPING_MAIN = {}

# for key, value in ISO_2_TO_1_MAPPING_1.items():
#     if len(key) == 3 and len(value) == 2:
#         ISO_2_TO_1_MAPPING_MAIN[key] = value

# for key, value in ISO_2_TO_1_MAPPING_2.items():
#     if len(key) == 3 and len(value) == 2:
#         if key in ISO_2_TO_1_MAPPING_MAIN:
#             assert ISO_2_TO_1_MAPPING_MAIN[key] == value
#         ISO_2_TO_1_MAPPING_MAIN[key] = value

# for key, value in CCMATRIX_MAPPING.items():
#     key = key.split('_')[0]
#     if len(key) == 3 and len(value) == 2:
#         if key in ISO_2_TO_1_MAPPING_MAIN:
#             assert ISO_2_TO_1_MAPPING_MAIN[key] == value
#         ISO_2_TO_1_MAPPING_MAIN[key] = value

# print(len(ISO_2_TO_1_MAPPING_MAIN))