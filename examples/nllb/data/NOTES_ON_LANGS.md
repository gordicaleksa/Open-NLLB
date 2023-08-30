We have lang codes present in our primary datasets like:
* aar -> Afar language, but it's not supported so we can safely ignore it.
* nde -> NDebele, not supported in NLLB even though present in datasets.
* ven -> Venda, not supported.
* gag -> Gagauz, not supported by NLLB.

* orm -> Oromo macro-language, but NLLB only supports a single language from that macro group -> gaz – West Central Oromo
because none of the files were included that had "gaz" as a suffix/infix we extended langs.txt with "orm"

TODO: if someone speaks Oromo please confirm that these texts are actually West Central Oromo language.

* kur -> some files had the "kur" suffix but according to @Razhan it's apparently Northern Kurdish "kmr_Latn" which is supported so we added "kur" to extended_langs.txt

* pus -> Pashto macro-language,  NLLB only supports "Southern Pashto" or "pbt". We'll include it to extended langs.txt.

TODO: if someone speaks Pashto verify we have Southern Pashto

* fas -> Persian macro-lang, NLLB supports both Western Persian ("Iranian Persian") and Dari so we include this suffix in extended_langs.txt

* ara -> Arabic marco-lang, NLLB supports many of the specific Arabic languages (if not all?) -> adding to extended_langs.txt

* tir_ET -> tir_Ethi is supported but added tir_ET to extended_langs.txt because sometimes that suffix appears in our datasets.

* tir_ER -> I don't see it mentioned in the NLLB paper, we should filter it out or same langs? For now we don't include it.

TODO: someone whose native lang is Ethiopian help?

* msa -> Malay macro-language, multiple langs from this group are supported in NLLB so adding to extended_langs.txt

* din -> Dinka macro-language, Southwestern Dinka is supported by NLLB so including din to extended_langs.txt

TODO: someone help make sure this is southwestern dinka


TODO: someone help understand this

* aze -> Azerbaijani macro-language NLLB supports both the north & south variants. Added to extended_langs.txt

* krc -> not mentioned in the paper, only as a part of Flores-200 so filtering it out

* chv -> Chuvash language, not mentioned in the paper, filtering it out

* kum & sah & alt & tyv & kaa & kjh & cjs -> not mentioned in the paper, can't find the ISO code, Google Translate says Kyrgyz again. Filtering out.

* uum -> not mentioned in the paper, can't find the ISO code, Google Translate says Luxembourgish. Filtering out.

* slr -> not mentioned in the paper, can't find the ISO code, Google Translate says it's Turkish. Filtering out.

* uzb -> Uzbek language, NLLB supports only Northern Uzbek, adding to extended_langs.txt.

TODO: someone double check this file we have is in Northern Uzbek lang.

