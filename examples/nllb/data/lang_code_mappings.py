import os
import re

BCP47_REGEX = re.compile(r'[a-z]{3}_[a-zA-Z]{4}')

# Created by manual inspection by @gordicaleksa, check NOTES_ON_LANGS.md file as well for more information.
UNSUPPORTED_LANG_CODES = ['slr', 'kum', 'sah', 'alt', 'tyv', 'kaa', 'kjh', 'cjs', 'chv', 'krc', 'tir_ER', 'aar', 'nde', 'ven', 'uum', 'gag']

# These codes contain 2 possible scripts
AMBIGUOUS_ISO_639_3_CODES = ['ace', 'bjn', 'kas', 'knc', 'taq', 'zho', "srp", "bos"]

# These are some additional mappings I added manually after analyzing the data to ISO_639_3_TO_BCP_47.
# Most of these are macro-langs and we make an assumption about which specific langs they map to.
# tir_ET', 'pus', 'orm', 'gag', 'ara', 'ori', 'aze', 'msa', 'uzb', 'din', 'kur', 'fas'

# Constructed using the `build_iso_3_to_bcp_mapping` function below.
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
        "bos_Latn",
        "bos_Cyrl"
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
    # Manually added after analyzing tico dataset using fasttext model (https://huggingface.co/facebook/fasttext-language-identification), din stands for Dinka macro-language.
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
    # Manually added after analyzing tico dataset and seeing they have "fas" and "prs", thus I concluded that "fas" is actually "pes".
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
    # Manually added after analyzing bianet dataset and seeing Latn script (thus concluding it's Northern Kurdish).
    "kur": [
        "kmr_Latn"
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
    # Manually added as we assume we only have ory_Orya (Odia), ori is a macro-lang (has 2 langs).
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
    # Manually added (tico dataset) as we assume we only have Southern Pashto.
    "pus": [
        "pbt_Arab"
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
        "srp_Latn",
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
    # Not an ISO 639-3 code per se but we need this mapping.
    "tir_ET": [
        "tir_Ethi"
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
ISO_639_1_TO_ISO_639_3 = {
    "ar" : "ara",
    "am" : "amh",
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
    "az" : "aze",
    "ba" : "bak",
    "cv" : "chv",
    "kk" : "kaz",
    "ky" : "kir",
    "ru" : "rus",
    "tk" : "tuk",
    "tr" : "tur",
    "tt" : "tat",
    "ug" : "uig",
    "uz" : "uzb",
    "fa" : "fas",
    "id" : "ind",
    "zh" : "zho",
    "ha" : "hau",
    "km" : "khm",
    "lg" : "lug",
    "ln" : "lin",
    "ms" : "msa",
    "my" : "mya",
    "om" : "orm",
    "ps" : "pus",
    "rw" : "kin",
    "so" : "som",
    "tl" : "tgl",
    "ur" : "urd",
    "zu" : "zul",
    "sr" : "srp",
    "bs" : "bos",
    "hr" : "hrv",
    "de" : "deu",
    "el" : "ell",
    "pl" : "pol",
    "es" : "spa",
    "be" : "bel",
    "bg" : "bul",
    "cs" : "ces",
    "mk" : "mkd",
    "sk" : "slk",
    "sl" : "slv",
    "uk" : "ukr",
    "szl": "szl",  # exception for Silesian
}

def ISO_639_1_TO_BCP_47_func(iso_639_1_code):
    return ISO_639_3_TO_BCP_47[ISO_639_1_TO_ISO_639_3[iso_639_1_code]][0]

LOCALIZED_TO_ISO_639_3 = {
    "es-LA": "spa",
    "pt-BR": "por",
}

# def build_iso_3_to_bcp_mapping():
#     import json
#     from collections import defaultdict

#     # Found this list of 202 langs here: fairseq/examples/nllb/modeling/scripts/flores200/langs.txt
#     langs_str = "ace_Arab,ace_Latn,acm_Arab,acq_Arab,aeb_Arab,afr_Latn,ajp_Arab,aka_Latn,amh_Ethi,apc_Arab,arb_Arab,ars_Arab,ary_Arab,arz_Arab,asm_Beng,ast_Latn,awa_Deva,ayr_Latn,azb_Arab,azj_Latn,bak_Cyrl,bam_Latn,ban_Latn,bel_Cyrl,bem_Latn,ben_Beng,bho_Deva,bjn_Arab,bjn_Latn,bod_Tibt,bos_Latn,bug_Latn,bul_Cyrl,cat_Latn,ceb_Latn,ces_Latn,cjk_Latn,ckb_Arab,crh_Latn,cym_Latn,dan_Latn,deu_Latn,dik_Latn,dyu_Latn,dzo_Tibt,ell_Grek,eng_Latn,epo_Latn,est_Latn,eus_Latn,ewe_Latn,fao_Latn,pes_Arab,fij_Latn,fin_Latn,fon_Latn,fra_Latn,fur_Latn,fuv_Latn,gla_Latn,gle_Latn,glg_Latn,grn_Latn,guj_Gujr,hat_Latn,hau_Latn,heb_Hebr,hin_Deva,hne_Deva,hrv_Latn,hun_Latn,hye_Armn,ibo_Latn,ilo_Latn,ind_Latn,isl_Latn,ita_Latn,jav_Latn,jpn_Jpan,kab_Latn,kac_Latn,kam_Latn,kan_Knda,kas_Arab,kas_Deva,kat_Geor,knc_Arab,knc_Latn,kaz_Cyrl,kbp_Latn,kea_Latn,khm_Khmr,kik_Latn,kin_Latn,kir_Cyrl,kmb_Latn,kon_Latn,kor_Hang,kmr_Latn,lao_Laoo,lvs_Latn,lij_Latn,lim_Latn,lin_Latn,lit_Latn,lmo_Latn,ltg_Latn,ltz_Latn,lua_Latn,lug_Latn,luo_Latn,lus_Latn,mag_Deva,mai_Deva,mal_Mlym,mar_Deva,min_Latn,mkd_Cyrl,plt_Latn,mlt_Latn,mni_Beng,khk_Cyrl,mos_Latn,mri_Latn,zsm_Latn,mya_Mymr,nld_Latn,nno_Latn,nob_Latn,npi_Deva,nso_Latn,nus_Latn,nya_Latn,oci_Latn,gaz_Latn,ory_Orya,pag_Latn,pan_Guru,pap_Latn,pol_Latn,por_Latn,prs_Arab,pbt_Arab,quy_Latn,ron_Latn,run_Latn,rus_Cyrl,sag_Latn,san_Deva,sat_Olck,scn_Latn,shn_Mymr,sin_Sinh,slk_Latn,slv_Latn,smo_Latn,sna_Latn,snd_Arab,som_Latn,sot_Latn,spa_Latn,als_Latn,srd_Latn,srp_Cyrl,ssw_Latn,sun_Latn,swe_Latn,swh_Latn,szl_Latn,tam_Taml,tat_Cyrl,tel_Telu,tgk_Cyrl,tgl_Latn,tha_Thai,tir_Ethi,taq_Latn,taq_Tfng,tpi_Latn,tsn_Latn,tso_Latn,tuk_Latn,tum_Latn,tur_Latn,twi_Latn,tzm_Tfng,uig_Arab,ukr_Cyrl,umb_Latn,urd_Arab,uzn_Latn,vec_Latn,vie_Latn,war_Latn,wol_Latn,xho_Latn,ydd_Hebr,yor_Latn,yue_Hant,zho_Hans,zho_Hant,zul_Latn"
#     langs = langs_str.split(',')

#     ISO_639_3_TO_BCP_47 = defaultdict(list)

#     for lang in langs:
#         lang, script = lang.split('_')
#         ISO_639_3_TO_BCP_47[lang].append(f'{lang}_{script}')

#     # Save dictionary as json
#     with open('ISO_639_3_TO_BCP_47.json', 'w') as f:
#         json.dump(ISO_639_3_TO_BCP_47, f, indent=4)

#     # After this I just copy pasted the content of the json file to the above dictionary.

extended_langs_path = os.path.join(os.path.dirname(__file__), 'extended_langs.txt')
with open(extended_langs_path, 'r') as f:
    EXTENDED_SUPPORTED_ISO_639_3_CODES_AND_SCRIPTS = f.readlines()[0].strip().split(',')
    EXTENDED_SUPPORTED_ISO_639_3_CODES = [lang.split('_')[0] for lang in EXTENDED_SUPPORTED_ISO_639_3_CODES_AND_SCRIPTS]
    SUPPORTED_ISO_639_1_CODES = ISO_639_1_TO_ISO_639_3.keys()
    bcp_47_codes = []
    for v in ISO_639_3_TO_BCP_47.values():
        bcp_47_codes.extend(v)
    SUPPORTED_BCP_47_CODES = list(set(bcp_47_codes))
    # 204 bc 202 originally + Serbian Latin + Bosnian Cyrillic.
    assert len(SUPPORTED_BCP_47_CODES) == 204, f'Expected 204 supported langs, got {len(SUPPORTED_BCP_47_CODES)}.'

def retrieve_supported_files_and_iso_639_3_codes(files, is_gz=False):
    new_files_and_iso_639_3_codes = []

    for file in files:
        lang_code_suffix = file.split('.')[-2] if is_gz else file.split('.')[-1]
        if lang_code_suffix in UNSUPPORTED_LANG_CODES:
            print(f'Unsupported language code {lang_code_suffix}.')
            continue
        if file in EXTENDED_SUPPORTED_ISO_639_3_CODES_AND_SCRIPTS:
            raise Exception(f'Legacy - we should never hit this branch.')
            # iso_639_3_code = file.split('_')[0]
            # new_files_and_lang_directions.append((file, iso_639_3_code))
        elif lang_code_suffix in EXTENDED_SUPPORTED_ISO_639_3_CODES_AND_SCRIPTS:
            new_files_and_iso_639_3_codes.append((file, lang_code_suffix.split('_')[0]))
        elif lang_code_suffix in EXTENDED_SUPPORTED_ISO_639_3_CODES:
            new_files_and_iso_639_3_codes.append((file, lang_code_suffix))
        elif lang_code_suffix in SUPPORTED_ISO_639_1_CODES:
            new_files_and_iso_639_3_codes.append((file, ISO_639_1_TO_ISO_639_3[lang_code_suffix]))
        else:
            print(f'Skipping {file} - not a language file.')

    return new_files_and_iso_639_3_codes

#
# Below data was scraped from the web in order to construct the mapping but at the end we just created the above
# mapping manually and ignored everything below. Feel free to use to extend the above mappings esp. the ISO_639_1.
#

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
