# Notes about datasets downloaded using download_parallel_corpora.py

Below are the notes about how we are handling certain language codes that caused us problems:

* `aar` -> Afar language, not supported by NLLB.
* `nde` -> NDebele, not supported by NLLB.
* `ven` -> Venda, not supported by NLLB.
* `gag` -> Gagauz, not supported by NLLB.
* `orm` -> Oromo macro-language. NLLB only supports a single language from that macro group `gaz` – West Central Oromo. None of the downloaded dataset files had `gaz` as a suffix/infix so I added `orm` to `extended_langs.txt` (otherwise it would get filtered out).
* `kur` -> some files had the `kur` suffix but according to @Razhan (Discord) it's apparently Northern Kurdish `kmr_Latn` which is supported so we added `kur` to `extended_langs.txt`.
* `pus` -> Pashto macro-language. NLLB only supports "Southern Pashto" or `pbt`. Included in `extended_langs.txt`.
* `fas` -> Persian macro-lang. NLLB supports both Western Persian ("Iranian Persian") and Dari so we include this suffix in `extended_langs.txt`.
* `ara` -> Arabic marco-lang. NLLB supports many of the specific Arabic languages. Included in `extended_langs.txt`.
* `tir_ET` -> tir_Ethi is supported but added tir_ET to extended_langs.txt because sometimes that suffix appears in our datasets.
* `tir_ER` -> I don't see it mentioned in the NLLB paper, we should filter it out or is this the same lang as `tir_Ethi`? For now we don't include it.
* `msa` -> Malay macro-language. Multiple langs from this group are supported in NLLB. Included in `extended_langs.txt`.
* `din` -> Dinka macro-language. Southwestern Dinka is supported by NLLB. Included in `extended_langs.txt`.
* `aze` -> Azerbaijani macro-language. NLLB supports both the Northern & Southern variants. Included in `extended_langs.txt`.
* `krc` -> not mentioned in the paper, only as a part of Flores-200 so filtering it out.
* `chv` -> Chuvash language, not mentioned in the paper, filtering it out.
* `kum sah alt tyv kaa kjh cjs` -> not mentioned in the paper, can't find the ISO code, Google Translate says Kyrgyz. Filtering out.
* `uum` -> not mentioned in the paper, can't find the ISO code, Google Translate says Luxembourgish. Filtering out.
* `slr` -> not mentioned in the paper, can't find the 639_3 ISO code, Google Translate says it's Turkish. Filtering out.
* `uzb` -> Uzbek language. NLLB supports only Northern Uzbek, adding to `extended_langs.txt`.

TODO: We need people who are native in the following languages to assist:
* Northern Uzbek
* Oromo (West Central Oromo language question)
* Pashto (Southern Pashto question)
* Ethiopian
* Southwestern dinka

Note: `extended_langs.txt` contains the BCP 47 codes of the original 202 NLLB languages + some macro-lang codes that helps us not filter certain files out when they have a macro lang code as an infix or suffix.