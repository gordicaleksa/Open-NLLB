# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

#
# The required output dataset structure of each of our download functions is:
# {corpus_name}/
#     bcp47_code1-bcp47_code2/
#         {corpus_name}.bcp47_code1
#         {corpus_name}.bcp47_code2
#     bcp47_code3-bcp47_code4/
#         {corpus_name}.bcp47_code3
#         {corpus_name}.bcp47_code4
#     ...
# We have an expectation that each download function obeys this structure.
#

import argparse
import csv
import gzip
import os
import re
import requests
import shutil
import tarfile
import zipfile

import openpyxl
from translate.storage.tmx import tmxfile

from lang_code_mappings import BCP47_REGEX, UNSUPPORTED_LANG_CODES, ISO_639_1_TO_ISO_639_3, ISO_639_3_TO_BCP_47, AMBIGUOUS_ISO_639_3_CODES

"""
Dependencies:
openpyxl (pip)
gsutil (pip)
translate-toolkit (pip)

See README in local directory for important notes on usage / data coverage
"""

UNSUPPORTED_CODE = -1


#
# Helper functions
#
def init_routine(directory, corpus_name):
    dataset_directory = os.path.join(directory, corpus_name)
    os.makedirs(dataset_directory, exist_ok=True)
    print(f"Saving {corpus_name} data to:", dataset_directory)
    return dataset_directory


def download_file(download_url, download_path):
    response = requests.get(download_url)
    if not response.ok:
        print(f"Could not download from {download_url}!")
        return False
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")
    return True


def gzip_extract_and_remove(zipped_path):
    assert zipped_path.endswith(".gz")
    unzipped_path = zipped_path[:-3]

    with gzip.open(zipped_path, "rb") as f:
        file_content = f.read()
    with open(unzipped_path, "wb") as f:
        f.write(file_content)
    os.remove(zipped_path)
    print(f"Extracted and removed: {zipped_path}")
    return unzipped_path


def concat_url_text_contents_to_file(url_list, download_path):
    with open(download_path, "w") as f:
        for download_url in url_list:
            response = requests.get(download_url)
            if not response.ok:
                raise Exception(f"Could not download from {download_url}!")
            f.write(response.text)
            if not response.text.endswith("\n"):
                f.write("\n")
    print(f"Wrote: {download_path}")
    return True


def convert_into_bcp47(lang_code):
    lang_code = ISO_639_1_TO_ISO_639_3[lang_code] if len(lang_code) == 2 else lang_code
    if BCP47_REGEX.match(lang_code):
        return lang_code

    if lang_code == 'tir_ET':
        lang_code = 'tir'
    if lang_code == 'tir_ER':
        lang_code = 'tir_ER'  # This will trigger the unsupported code branch.

    if lang_code in AMBIGUOUS_ISO_639_3_CODES:
        raise Exception(f'Please manually decide which script is being used.')
    if lang_code in UNSUPPORTED_LANG_CODES:
        print(f"{lang_code} language is unsupported! Deleting this piece of data.")
        return UNSUPPORTED_CODE

    lang_code = ISO_639_3_TO_BCP_47[lang_code][0]

    return lang_code


def validate_downloaded_data(directory):
    for corpus_name in os.listdir(directory):
        corpus_path = os.path.join(directory, corpus_name)
        for lang_direction in os.listdir(corpus_path):
            lang_direction_path = os.path.join(corpus_path, lang_direction)
            src, trg = lang_direction.split("-")
            assert BCP47_REGEX.match(src), f"Expected {src} to be a valid BCP 47 code!"
            assert BCP47_REGEX.match(trg), f"Expected {trg} to be a valid BCP 47 code!"
            for file in os.listdir(lang_direction_path):
                prefix = file.split(".")[0]
                suffix = file.split(".")[-1]
                assert prefix == corpus_name, f"Expected {prefix} to be {corpus_name}!"
                assert BCP47_REGEX.match(suffix), f"Expected {suffix} to be a valid BCP 47 code!"

#
# End of helper functions
#

def download_TIL(directory):
    """
    https://arxiv.org/pdf/2109.04593.pdf
    https://github.com/turkic-interlingua/til-mt
    Total download: 22.4 GB
    """
    corpus_name = "til"
    dataset_directory = init_routine(directory, corpus_name)

    til_train_url = "gs://til-corpus/corpus/train/*"
    command = f"gsutil -m cp -r {til_train_url} {dataset_directory}"
    print(f"Running: {command}")
    try:
        os.system(command)
    except Exception as e:
        print(f"gsutil download failed! \n{e}")
        raise e

    pair_directories = os.listdir(dataset_directory)
    for pair_directory in pair_directories:
        try:
            src, tgt = pair_directory.split("-")
        except:
            raise Exception(f"Unexpected {corpus_name} pair directory name! {pair_directory}")

        dest_src = convert_into_bcp47(src)
        if dest_src == UNSUPPORTED_CODE:
            print(f"{src} language is unsupported! Deleting this piece of data.")
            shutil.rmtree(os.path.join(dataset_directory, pair_directory))
            continue

        dest_tgt = convert_into_bcp47(tgt)
        if dest_tgt == UNSUPPORTED_CODE:
            print(f"{tgt} language is unsupported! Deleting this piece of data.")
            shutil.rmtree(os.path.join(dataset_directory, pair_directory))
            continue

        pair_directory_path = os.path.join(dataset_directory, pair_directory)
        try:
            os.rename(
                os.path.join(pair_directory_path, f"{src}-{tgt}.{src}"),
                os.path.join(pair_directory_path, f"{corpus_name}.{dest_src}"),
            )
            os.rename(
                os.path.join(pair_directory_path, f"{src}-{tgt}.{tgt}"),
                os.path.join(pair_directory_path, f"{corpus_name}.{dest_tgt}"),
            )
        except:
            files = os.listdir(pair_directory_path)
            assert files[0] == f"{corpus_name}.{dest_src}" if dest_src in files[0] else files[0] == f"{corpus_name}.{dest_tgt}"
            assert files[1] == f"{corpus_name}.{dest_tgt}" if dest_tgt in files[1] else files[1] == f"{corpus_name}.{dest_src}"

        renamed_pair_directory = os.path.join(
            dataset_directory, f"{dest_src}-{dest_tgt}"
        )
        os.rename(pair_directory_path, renamed_pair_directory)


def download_TICO(directory, verbose=False):
    """
    https://tico-19.github.io/
    Total after extraction: 130M
    """
    corpus_name = "tico"
    dataset_directory = init_routine(directory, corpus_name)

    # This is a special knowledge that can't easily be inferred
    # because it maps from a macro-language 2 letter (ISO 639 1) code
    # to a particular language (ISO 639 3) code within that macro-language.
    # Not used, just for reference.
    # dataset_specific_lang_mapping = {
    #     "ku": "kmr",
    #     "kr": "knc",
    #     "ne": "npi",
    #     "sw": "swh",
    # }

    source_langs = {
        "am": "amh",
        "ar": "ara",
        "en": "eng",
        "es-LA": "spa",
        "fa": "fas",
        "fr": "fra",
        "hi": "hin",
        "id": "ind",
        "ku": "kmr",
        "pt-BR": "por",
        "ru": "rus",
        "zh": "zho_Hans",  # Added Hans to remove ambiguity, their website says it's simplified Chinese.
    }

    target_langs = {
        "am": "amh",
        "ar": "ara",
        "bn": "ben",
        "ckb": "ckb",
        "din": "din",
        "es-LA": "spa",
        "fa": "fas",
        "fr": "fra",
        "fuv": "fuv",
        "ha": "hau",
        "hi": "hin",
        "id": "ind",
        "km": "khm",
        "kr": "knc_Latn",  # Added Latn to remove ambiguity, I opened the data and saw it's Latn and not Arabic script.
        "ku": "kmr",
        "lg": "lug",
        "ln": "lin",
        "mr": "mar",
        "ms": "msa",
        "my": "mya",
        "ne": "npi",
        "nus": "nus",
        "om": "orm",
        "prs": "prs",
        "pt-BR": "por",
        "ps": "pus",
        "ru": "rus",
        "rw": "kin",
        "so": "som",
        "sw": "swh",
        "ta": "tam",
        "ti_ET": "tir_ET",  # we combine both Tigrinya varieties
        "ti_ER": "tir_ER",  # we combine both Tigrinya varieties
        "tl": "tgl",
        "ur": "urd",
        "zh": "zho_Hans",  # Added Hans to remove ambiguity, their website says it's simplified Chinese.
        "zu": "zul",
    }

    flag_all_failed = True
    for source in source_langs:
        for target in target_langs:
            url = f"https://tico-19.github.io/data/TM/all.{source}-{target}.tmx.zip"
            response = requests.get(url)
            if not response.ok:
                if verbose:
                    print("Could not download data for {source}-{target}! Skipping...")
                continue

            flag_all_failed = False
            lang1 = source_langs[source]
            lang2 = target_langs[target]
            if lang2 < lang1:
                lang1, lang2 = lang2, lang1

            lang1 = convert_into_bcp47(lang1)
            if lang1 == UNSUPPORTED_CODE:
                continue

            lang2 = convert_into_bcp47(lang2)
            if lang2 == UNSUPPORTED_CODE:
                continue

            direction_directory = os.path.join(dataset_directory, f"{lang1}-{lang2}")
            os.makedirs(direction_directory, exist_ok=True)

            download_path = os.path.join(
                direction_directory, f"all.{source}-{target}.tmx.zip"
            )
            open(download_path, "wb").write(response.content)
            print(f"Wrote: {download_path}")

            with zipfile.ZipFile(download_path, "r") as z:
                z.extractall(direction_directory)
            tmx_file_path = os.path.join(
                direction_directory, f"all.{source}-{target}.tmx"
            )
            os.remove(download_path)
            print(f"Extracted and removed: {download_path}")

            with open(tmx_file_path, "rb") as f:
                tmx_data = tmxfile(f, source, target)
            source_path = os.path.join(
                direction_directory, f"{corpus_name}.{lang1}"
            )
            with open(source_path, "w") as f:
                for node in tmx_data.unit_iter():
                    f.write(node.source)
                    f.write("\n")
            print(f"Wrote: {source_path}")

            target_path = os.path.join(
                direction_directory, f"{corpus_name}.{lang2}"
            )
            with open(target_path, "w") as f:
                for node in tmx_data.unit_iter():
                    f.write(node.target)
                    f.write("\n")
            print(f"Wrote: {target_path}")
            os.remove(tmx_file_path)
            print(f"Deleted: {tmx_file_path}")

    if flag_all_failed:
        raise Exception("Could not download any data for TICO!")


def download_IndicNLP(directory, non_train_datasets_path):
    """
    http://lotus.kuee.kyoto-u.ac.jp/WAT/indic-multilingual/
    Total after extraction: 3.1GB
    """
    corpus_name = "indic_nlp"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "http://lotus.kuee.kyoto-u.ac.jp/WAT/indic-multilingual/indic_wat_2021.tar.gz"
    )
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for Indic NLP!")
    download_path = os.path.join(dataset_directory, "indic_wat_2021.tar.gz")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    with tarfile.open(download_path) as tar:
        tar.extractall(dataset_directory)
    os.remove(download_path)
    print(f"Deleted: {download_path}")
    print(f"Extracted to: {dataset_directory}")

    # Get the dataset into the required structure:
    nested_path = os.path.join(dataset_directory, 'finalrepo')
    target_directory = os.path.join(non_train_datasets_path, corpus_name)
    os.makedirs(target_directory, exist_ok=True)
    try:
        os.rename(os.path.join(nested_path, 'README'), os.path.join(target_directory, 'README'))
    except:
        pass
    try:
        shutil.move(os.path.join(nested_path, 'dev'), target_directory)
    except:
        pass
    try:
        shutil.move(os.path.join(nested_path, 'test'), target_directory)
    except:
        pass
    train_path = os.path.join(nested_path, 'train')
    target_directory = os.path.join(target_directory, 'train')
    os.makedirs(target_directory, exist_ok=True)

    # Rename files & lang direction directories to BCP 47.
    for el in os.listdir(train_path):
        child_dataset_path = os.path.join(train_path, el)
        if os.path.isdir(child_dataset_path):
            for lang_direction in os.listdir(child_dataset_path):
                lang_direction_path = os.path.join(child_dataset_path, lang_direction)
                assert os.path.isdir(lang_direction_path), f"Expected {lang_direction_path} to be a directory!"
                should_del_flag = False
                for file in os.listdir(lang_direction_path):
                    file_path = os.path.join(lang_direction_path, file)
                    suffix = file.split('.')[-1]
                    suffix_bcp47 = convert_into_bcp47(suffix)
                    if suffix_bcp47 == UNSUPPORTED_CODE:
                        should_del_flag = True
                        break
                    new_file_path = os.path.join(lang_direction_path, f'{el}.{suffix_bcp47}')
                    os.rename(file_path, new_file_path)
                if should_del_flag:
                    shutil.rmtree(lang_direction_path)
                else:
                    src, trg = lang_direction.split('-')
                    src_bcp47 = convert_into_bcp47(src)
                    trg_bcp47 = convert_into_bcp47(trg)
                    os.rename(lang_direction_path, os.path.join(child_dataset_path, f'{src_bcp47}-{trg_bcp47}'))
            shutil.move(child_dataset_path, os.path.join(directory, el))
        else:
            shutil.move(os.path.join(train_path, el), os.path.join(target_directory, el))

    shutil.rmtree(dataset_directory)


def download_Lingala_Song_Lyrics(directory):
    """
    https://github.com/espoirMur/songs_lyrics_webscrap
    """
    corpus_name = "lingala_songs"
    dataset_directory = init_routine(directory, corpus_name)

    lang_code1 = 'fra_Latn'
    lang_code2 = 'lin_Latn'

    download_url = "https://raw.githubusercontent.com/espoirMur/songs_lyrics_webscrap/master/data/all_data.csv"
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for Lingala song lyrics!")
    download_path = os.path.join(dataset_directory, "all_data.csv")

    def core_fn(download_path, source_file_path, target_file_path):
        open(download_path, "wb").write(response.content)
        print(f"Wrote: {download_path}")

        content_lines = open(download_path).readlines()
        fr_examples = []
        lin_examples = []
        for pair_line in content_lines[1:]:  # first line specifies languages
            fr, lin = pair_line.split("|")

            # multiple spaces separate song lines within stanzas
            fr_lines = re.sub("\s\s+", "\t", fr).split("\t")
            lin_lines = re.sub("\s\s+", "\t", lin).split("\t")

            if len(fr_lines) == len(lin_lines):
                fr_examples.extend(fr_lines)
                lin_examples.extend(lin_lines)
            else:
                fr_examples.append(" ".join(fr_lines))
                lin_examples.append(" ".join(lin_lines))
        fr_examples = [examp.strip() for examp in fr_examples]
        lin_examples = [examp.strip() for examp in lin_examples]

        with open(source_file_path, "w") as f:
            f.write("\n".join(fr_examples))

        with open(target_file_path, "w") as f:
            f.write("\n".join(lin_examples))

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_FFR(directory):
    """
    https://arxiv.org/abs/2006.09217
    https://github.com/bonaventuredossou/ffr-v1/tree/master/FFR-Dataset
    """
    corpus_name = "ffr"
    dataset_directory = init_routine(directory, corpus_name)

    lang_code1 = "fon_Latn"
    lang_code2 = "fra_Latn"

    download_url = "https://raw.githubusercontent.com/bonaventuredossou/ffr-v1/master/FFR-Dataset/FFR%20Dataset%20v2/ffr_dataset_v2.txt"
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for FFR!")
    download_path = os.path.join(dataset_directory, "ffr_dataset_v2.txt")

    def core_fn(download_path, source_file_path, target_file_path):
        open(download_path, "wb").write(response.content)
        print(f"Wrote: {download_path}")

        with open(download_path) as f, open(source_file_path, "w") as fon, open(
            target_file_path, "w"
        ) as fra:
            for joint_line in f:
                # one line has a tab in the French side: "A tout seigneur \t tout honneur"
                fon_line, fra_line = joint_line.split("\t", 1)
                fon.write(fon_line.strip() + "\n")
                fra.write(fra_line.strip() + "\n")

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_Mburisano_Covid(directory):
    """
    https://repo.sadilar.org/handle/20.500.12185/536
    """
    print("IMPORTANT!")
    print("By downloading this corpus, you agree to the terms of use found here:")
    print("https://sadilar.org/index.php/en/guidelines-standards/terms-of-use")

    corpus_name = "mburisano"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = "https://repo.sadilar.org/bitstream/20.500.12185/536/1/mburisano_multilingual_corpus.csv"
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for Mburisano!")
    download_path = os.path.join(dataset_directory, "mburisano_multilingual_corpus.csv")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    # line 0 contains language names
    csv_lines = open(download_path).readlines()[1:]
    data = {
        "afr": [],  # Afrikaans
        "eng": [],  # English
        "nde": [],  # isiNdebele
        "sot": [],  # Sesotho
        "ssw": [],  # Siswati
        "tsn": [],  # Setswana
        "tso": [],  # Xitsonga
        "ven": [],  # Tshiven·∏ìa
        "xho": [],  # isiXhosa
        "zul": [],  # isiZulu
    }
    for line in csv.reader(csv_lines):
        if len(line) == 11:
            afr, eng, nde, xho, zul, sot, _, tsn, ssw, ven, tso = line
        else:
            print("Does not have correct number of fields!")
            print(line)
            continue
        data["afr"].append(afr)
        data["eng"].append(eng)
        data["nde"].append(nde)
        data["sot"].append(sot)
        data["ssw"].append(ssw)
        data["tsn"].append(tsn)
        data["tso"].append(tso)
        data["ven"].append(ven)
        data["xho"].append(xho)
        data["zul"].append(zul)

    for source, target in [
        ("afr", "eng"),
        ("eng", "nde"),
        ("eng", "sot"),
        ("eng", "ssw"),
        ("eng", "tsn"),
        ("eng", "tso"),
        ("eng", "ven"),
        ("eng", "xho"),
        ("eng", "zul"),
    ]:
        source_bcp47 = convert_into_bcp47(source)
        if source_bcp47 == UNSUPPORTED_CODE:
            continue
        target_bcp47 = convert_into_bcp47(target)
        if target_bcp47 == UNSUPPORTED_CODE:
            continue

        direction_directory = os.path.join(dataset_directory, f"{source_bcp47}-{target_bcp47}")
        os.makedirs(direction_directory, exist_ok=True)

        source_file = os.path.join(direction_directory, f"{corpus_name}.{source_bcp47}")
        with open(source_file, "w") as f:
            for line in data[source]:
                f.write(line)
                f.write("\n")
        print(f"Wrote: {source_file}")

        target_file = os.path.join(direction_directory, f"{corpus_name}.{target_bcp47}")
        with open(target_file, "w") as f:
            for line in data[target]:
                f.write(line)
                f.write("\n")
        print(f"Wrote: {target_file}")

    os.remove(download_path)
    print(f"Deleted: {download_path}")


def download_XhosaNavy(directory):
    """
    https://opus.nlpl.eu/XhosaNavy.php
    """
    corpus_name = "xhosa_navy"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "https://opus.nlpl.eu/download.php?f=XhosaNavy/v1/moses/en-xh.txt.zip"
    )
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for Xhosa Navy!")
    download_path = os.path.join(dataset_directory, "en-xh.txt.zip")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    extract_directory = os.path.join(dataset_directory, "extract")
    os.makedirs(extract_directory, exist_ok=True)
    with zipfile.ZipFile(download_path, "r") as z:
        z.extractall(extract_directory)
    print("Extracted to:", extract_directory)

    lang_code1 = 'eng_Latn'
    lang_code2 = 'xho_Latn'
    lang_direction_path1 = os.path.join(dataset_directory, f'{lang_code1}-{lang_code2}')
    lang_direction_path2 = os.path.join(dataset_directory, f'{lang_code2}-{lang_code1}')
    os.makedirs(lang_direction_path1, exist_ok=True)
    os.makedirs(lang_direction_path2, exist_ok=True)

    eng_filename = f"{corpus_name}.{lang_code1}"
    eng_file_path = os.path.join(dataset_directory, lang_direction_path1, eng_filename)
    os.rename(
        os.path.join(extract_directory, "XhosaNavy.en-xh.en"),
        eng_file_path,
    )
    print(f"Wrote: {eng_file_path}")

    xho_filename = f"{corpus_name}.{lang_code2}"
    xho_file_path = os.path.join(dataset_directory, lang_direction_path1, xho_filename)
    os.rename(
        os.path.join(extract_directory, "XhosaNavy.en-xh.xh"),
        xho_file_path,
    )
    print(f"Wrote: {xho_file_path}")

    shutil.copyfile(eng_file_path, os.path.join(lang_direction_path2, eng_filename))
    shutil.copyfile(xho_file_path, os.path.join(lang_direction_path2, xho_filename))

    shutil.rmtree(extract_directory)
    print(f"Deleted tree: {extract_directory}")
    os.remove(download_path)
    print(f"Deleted: {download_path}")


def download_Menyo20K(directory):
    """
    https://arxiv.org/abs/2103.08647
    https://github.com/uds-lsv/menyo-20k_MT
    """
    corpus_name = "menyo20k"
    dataset_directory = init_routine(directory, corpus_name)

    lang_code1 = 'eng_Latn'
    lang_code2 = 'yor_Latn'

    download_url = (
        "https://raw.githubusercontent.com/uds-lsv/menyo-20k_MT/master/data/train.tsv"
    )
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for MENYO-20k!")
    download_path = os.path.join(dataset_directory, "train.tsv")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    def core_fn(download_path, source_file_path, target_file_path):
        # line 0 contains language names
        tsv_lines = open(download_path).readlines()[1:]
        with open(source_file_path, "w") as src, open(target_file_path, "w") as tgt:
            for line in csv.reader(tsv_lines, delimiter="\t"):
                source_line, target_line = line
                src.write(source_line.strip())
                src.write("\n")
                tgt.write(target_line.strip())
                tgt.write("\n")

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2):
    def wrapped_func():
        filename1 = f"{corpus_name}.{lang_code1}"
        filename2 = f"{corpus_name}.{lang_code2}"
        lang_direction_path1 = os.path.join(dataset_directory, f'{lang_code1}-{lang_code2}')
        lang_direction_path2 = os.path.join(dataset_directory, f'{lang_code2}-{lang_code1}')
        os.makedirs(lang_direction_path1, exist_ok=True)
        os.makedirs(lang_direction_path2, exist_ok=True)
        source_file_path = os.path.join(lang_direction_path1, filename1)
        target_file_path = os.path.join(lang_direction_path1, filename2)

        core_fn(download_path, source_file_path, target_file_path)

        print(f"Wrote: {source_file_path}")
        print(f"Wrote: {target_file_path}")

        shutil.copyfile(source_file_path, os.path.join(lang_direction_path2, filename1))
        shutil.copyfile(target_file_path, os.path.join(lang_direction_path2, filename2))

        try:
            if download_path:
                os.remove(download_path)
                print(f"Deleted: {download_path}")
        except:
            pass

    return wrapped_func


def download_FonFrench(directory):
    """
    https://zenodo.org/record/4266935#.YaTu0fHMJDY
    """
    corpus_name = "french_fongbe"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "https://zenodo.org/record/4266935/files/French_to_fongbe.csv?download=1"
    )
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for French-Fongbe!")
    download_path = os.path.join(dataset_directory, "French_to_fongbe.csv")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    lang_code1 = 'fon_Latn'
    lang_code2 = 'fra_Latn'

    def core_fn(download_path, source_file_path, target_file_path):
        # line 0 contains language names
        csv_lines = open(download_path).readlines()[1:]
        with open(source_file_path, "w") as src, open(target_file_path, "w") as tgt:
            for line in csv.reader(csv_lines):
                source_line, target_line = line
                src.write(source_line.strip())
                src.write("\n")
                tgt.write(target_line.strip())
                tgt.write("\n")

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_FrenchEwe(directory):
    """
    https://zenodo.org/record/4266935#.YaTu0fHMJDY
    """
    corpus_name = "french_ewe"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "https://zenodo.org/record/4266935/files/French_to_ewe_dataset.xlsx?download=1"
    )
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for French-Ewe!")
    download_path = os.path.join(dataset_directory, "French_to_ewe_dataset.xlsx")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    lang_code1 = 'fra_Latn'
    lang_code2 = 'ewe_Latn'

    def core_fn(download_path, source_file_path, target_file_path):
        wb = openpyxl.load_workbook(download_path)
        french_sheet = wb["French"]
        ewe_sheet = wb["Ewe"]

        french_examples = []
        ewe_examples = []
        for french_row, ewe_row in zip(french_sheet.rows, ewe_sheet.rows):
            if french_row[1].value is None or ewe_row[1].value is None:
                continue
            # preserve file alignment by removing newlines
            french_sent = french_row[1].value.strip().replace("\n", " ")
            ewe_sent = ewe_row[1].value.strip().replace("\n", " ")
            french_examples.append(french_sent)
            ewe_examples.append(ewe_sent)

        with open(source_file_path, "w") as src, open(target_file_path, "w") as tgt:
            for fra, ewe in zip(french_examples, ewe_examples):
                src.write(fra)
                src.write("\n")
                tgt.write(ewe)
                tgt.write("\n")

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_Akuapem(directory):
    """
    https://arxiv.org/pdf/2103.15625.pdf
    """
    corpus_name = "akuapem"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "https://zenodo.org/record/4432117/files/verified_data.csv?download=1"
    )
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for Akuapem!")
    download_path = os.path.join(dataset_directory, "verified_data.csv")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    lang_code1 = 'eng_Latn'
    lang_code2 = 'aka_Latn'

    def core_fn(download_path, source_file_path, target_file_path):
        # line 0 contains language names
        csv_lines = open(download_path).readlines()[1:]
        with open(source_file_path, "w") as src, open(target_file_path, "w") as tgt:
            for line in csv.reader(csv_lines):
                source_line, target_line = line
                src.write(source_line.strip())
                src.write("\n")
                tgt.write(target_line.strip())
                tgt.write("\n")

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_GELR(directory):
    """
    https://www.ijert.org/research/gelr-a-bilingual-ewe-english-corpus-building-and-evaluation-IJERTV10IS080214.pdf
    """
    pass


def download_GiossaMedia(directory):
    """
    https://github.com/sgongora27/giossa-gongora-guarani-2021
    """
    corpus_name = "giossa"
    dataset_directory = init_routine(directory, corpus_name)

    guarani_examples = []
    spanish_examples = []

    lang_code1 = 'grn_Latn'
    lang_code2 = 'spa_Latn'

    def core_fn(_, source_file_path, target_file_path):
        for name, download_url in [
            (
                "parallel_march",
                "https://github.com/sgongora27/giossa-gongora-guarani-2021/blob/main/ParallelSet/parallel_march.zip?raw=true",
            ),
            (
                "parallel_april",
                "https://github.com/sgongora27/giossa-gongora-guarani-2021/blob/main/ParallelSet/parallel_april.zip?raw=true",
            ),
        ]:
            response = requests.get(download_url)
            if not response.ok:
                raise Exception(f"Could not download from {download_url} ... aborting!")
            download_path = os.path.join(dataset_directory, f"{name}.zip")
            open(download_path, "wb").write(response.content)
            print(f"Wrote: {download_path}")

            with zipfile.ZipFile(download_path, "r") as z:
                z.extractall(dataset_directory)
            subset_directory = os.path.join(dataset_directory, name)
            print(f"Extracted to: {subset_directory}")
            os.remove(download_path)
            print(f"Deleted: {download_path}")

            for filename in os.listdir(subset_directory):
                aligned_file = os.path.join(subset_directory, filename)
                with open(aligned_file) as f:
                    contents = f.read()

                aligned_pairs = contents.split("gn: ")
                for pair in aligned_pairs:
                    if len(pair.strip()) == 0:
                        continue
                    try:
                        grn, spa = pair.split("\nes: ")
                        grn = grn.strip().replace("\n", " ")
                        spa = spa.strip().replace("\n", " ")
                    except:
                        print(f"Expected pair separated by 'es: ' but got: {pair}!")
                        import pdb

                        pdb.set_trace()
                    # begins with "gn: "
                    grn = grn[4:]
                    guarani_examples.append(grn)
                    spanish_examples.append(spa)
            shutil.rmtree(subset_directory)
            print(f"Deleted tree: {subset_directory}")

        with open(source_file_path, "w") as f:
            for sent in guarani_examples:
                f.write(sent)
                f.write("\n")

        with open(target_file_path, "w") as f:
            for sent in spanish_examples:
                f.write(sent)
                f.write("\n")

    core_fn_wrapper(core_fn, None, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_KinyaSMT(directory):
    """
    https://github.com/pniyongabo/kinyarwandaSMT
    """
    corpus_name = "kinya_smt"
    dataset_directory = init_routine(directory, corpus_name)

    kin_examples = []
    eng_examples = []

    lang_code1 = 'kin_Latn'
    lang_code2 = 'eng_Latn'

    def core_fn(download_path, source_file_path, target_file_path):
        download_url = "https://github.com/sgongora27/giossa-gongora-guarani-2021/blob/main/ParallelSet/parallel_march.zip?raw=true"

        for name, download_url in [
            (
                "bible.en",
                "https://raw.githubusercontent.com/pniyongabo/kinyarwandaSMT/master/train-data/bible.en",
            ),
            (
                "bible.kn",
                "https://raw.githubusercontent.com/pniyongabo/kinyarwandaSMT/master/train-data/bible.kn",
            ),
            (
                "train.en",
                "https://raw.githubusercontent.com/pniyongabo/kinyarwandaSMT/master/train-data/train.en",
            ),
            (
                "train.kn",
                "https://raw.githubusercontent.com/pniyongabo/kinyarwandaSMT/master/train-data/train.kn",
            ),
        ]:
            response = requests.get(download_url)
            if not response.ok:
                raise Exception(f"Could not download from {download_url} ... aborting!")
            download_path = os.path.join(dataset_directory, f"{name}.zip")
            open(download_path, "wb").write(response.content)
            print(f"Wrote: {download_path}")

            with open(download_path) as f:
                if name.endswith("kn"):
                    kin_examples.extend(f.readlines())
                else:
                    eng_examples.extend(f.readlines())
            os.remove(download_path)

        assert len(kin_examples) == len(eng_examples)
        with open(source_file_path, "w") as f:
            for sent in kin_examples:
                f.write(sent.strip())
                f.write("\n")

        with open(target_file_path, "w") as f:
            for sent in eng_examples:
                f.write(sent.strip())
                f.write("\n")

    core_fn_wrapper(core_fn, None, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_translation_memories_from_Nynorsk(directory):
    """
    (including Nynorsk)
    https://www.nb.no/sprakbanken/en/resource-catalogue/oai-nb-no-sbr-47/
    """
    corpus_name = "nynorsk_memories"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = "https://www.nb.no/sbfil/tekst/2011_2019_tm_npk_ntb.tar.gz"
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting!")
    download_path = os.path.join(dataset_directory, f"011_2019_tm_npk_ntb.tar.gz")

    lang_code1 = 'nob_Latn'
    lang_code2 = 'nno_Latn'

    def core_fn(download_path, source_file_path, target_file_path):
        open(download_path, "wb").write(response.content)
        print(f"Wrote: {download_path}")

        with tarfile.open(download_path) as tar:
            tar.extractall(dataset_directory)
        tmx_file_path = os.path.join(dataset_directory, f"2011_2019_tm_npk_ntb.tmx")

        with open(tmx_file_path, "rb") as f:
            # Norwegian Bokmal to Norwegian Nynorsk
            tmx_data = tmxfile(f, "NB", "NN")
        os.remove(tmx_file_path)

        # Norwegian Bokmål
        with open(source_file_path, "w") as f:
            for node in tmx_data.unit_iter():
                f.write(node.source)
                f.write("\n")

        # Norwegian Nynorsk
        with open(target_file_path, "w") as f:
            for node in tmx_data.unit_iter():
                f.write(node.target)
                f.write("\n")

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_mukiibi(directory):
    """
    https://zenodo.org/record/5089560#.YaipovHMJDZ
    """
    corpus_name = "mukiibi"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "https://zenodo.org/record/5089560/files/English-Luganda.tsv?download=1"
    )
    download_path = os.path.join(dataset_directory, "English-Luganda.tsv")
    ok = download_file(download_url, download_path)
    if not ok:
        raise Exception("Aborting for Makerere MT (English - Luganda)!")

    lang_code1 = 'eng_Latn'
    lang_code2 = 'lug_Latn'

    def core_fn(download_path, source_file_path, target_file_path):
        # line 0 contains language names
        tsv_lines = open(download_path).readlines()[1:]
        with open(source_file_path, "w") as src, open(target_file_path, "w") as tgt:
            for line in csv.reader(tsv_lines, delimiter="\t"):
                # empty third "column" (line-ending tab)
                source_line, target_line, _ = line
                src.write(source_line.strip())
                src.write("\n")
                tgt.write(target_line.strip())
                tgt.write("\n")

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_umsuka(directory):
    """
    https://zenodo.org/record/5035171#.YaippvHMJDZ
    """
    corpus_name = "umsuka"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "https://zenodo.org/record/5035171/files/en-zu.training.csv?download=1"
    )
    download_path = os.path.join(dataset_directory, "en-zu.training.csv")
    ok = download_file(download_url, download_path)
    if not ok:
        raise Exception("Aborting for Umsuka (isiZulu - English)!")

    lang_code1 = 'eng_Latn'
    lang_code2 = 'zul_Latn'

    def core_fn(download_path, source_file_path, target_file_path):
        eng_examples = []
        zul_examples = []

        # line 0 contains columm names
        with open(download_path) as f:
            csv_lines = f.readlines()[1:]
        for line in csv.reader(csv_lines):
            # third column contains data source
            source_line, target_line, _ = line
            eng_examples.append(source_line.strip().replace("\n", " "))
            zul_examples.append(target_line.strip().replace("\n", " "))

        with open(source_file_path, "w") as src, open(target_file_path, "w") as tgt:
            for eng, zul in zip(eng_examples, zul_examples):
                src.write(eng)
                src.write("\n")
                tgt.write(zul)
                tgt.write("\n")

    core_fn_wrapper(core_fn, download_path, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_CMU_Haitian_Creole(directory):
    """
    http://www.speech.cs.cmu.edu/haitian/text/
    """
    corpus_name = "cmu_haitian"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "http://www.speech.cs.cmu.edu/haitian/text/1600_medical_domain_sentences.en"
    )

    lang_code1 = 'eng_Latn'
    lang_code2 = 'hat_Latn'

    def core_fn(download_url, source_file_path, target_file_path):
        ok = download_file(download_url, source_file_path)
        if not ok:
            raise Exception("Aborting for CMU Hatian Creole!")

        download_url = (
            "http://www.speech.cs.cmu.edu/haitian/text/1600_medical_domain_sentences.ht"
        )
        ok = download_file(download_url, target_file_path)
        if not ok:
            raise Exception("Aborting for CMU Hatian Creole!")

    core_fn_wrapper(core_fn, download_url, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_Bianet(directory):
    """
    https://opus.nlpl.eu/Bianet.php
    Ataman, D. (2018) Bianet: A Parallel News Corpus in Turkish, Kurdish and English. In Proceedings of the LREC 2018 Workshop MLP-Moment. pp. 14-17
    """
    corpus_name = "bianet"
    dataset_directory = init_routine(directory, corpus_name)

    # eng-kur
    lang_code1 = 'eng_Latn'
    lang_code2 = 'kmr_Latn'

    def core_fn(_, source_file_path, target_file_path):
        download_url = "https://opus.nlpl.eu/download.php?f=Bianet/v1/tmx/en-ku.tmx.gz"
        download_path = os.path.join(dataset_directory, "en-ku.tmx.gz")
        ok = download_file(download_url, download_path)
        if not ok:
            raise Exception("Aborting for Bianet!")
        tmx_file_path = gzip_extract_and_remove(download_path)
        with open(tmx_file_path, "rb") as f:
            # English to Kurdish
            tmx_data = tmxfile(f, "en", "ku")
        os.remove(tmx_file_path)

        with open(source_file_path, "w") as f:
            for node in tmx_data.unit_iter():
                f.write(node.source)
                f.write("\n")

        with open(target_file_path, "w") as f:
            for node in tmx_data.unit_iter():
                f.write(node.target)
                f.write("\n")

    core_fn_wrapper(core_fn, None, dataset_directory, corpus_name, lang_code1, lang_code2)()

    # kur-tur
    lang_code1 = 'kmr_Latn'
    lang_code2 = 'tur_Latn'

    def core_fn(_, source_file_path, target_file_path):
        download_url = "https://opus.nlpl.eu/download.php?f=Bianet/v1/tmx/ku-tr.tmx.gz"
        download_path = os.path.join(dataset_directory, "ku-tr.tmx.gz")
        ok = download_file(download_url, download_path)
        if not ok:
            raise Exception("Aborting for Bianet!")
        tmx_file_path = gzip_extract_and_remove(download_path)
        with open(tmx_file_path, "rb") as f:
            # English to Kurdish
            tmx_data = tmxfile(f, "ku", "tr")
        os.remove(tmx_file_path)

        with open(source_file_path, "w") as f:
            for node in tmx_data.unit_iter():
                f.write(node.source)
                f.write("\n")

        with open(target_file_path, "w") as f:
            for node in tmx_data.unit_iter():
                f.write(node.target)
                f.write("\n")

    core_fn_wrapper(core_fn, None, dataset_directory, corpus_name, lang_code1, lang_code2)()


def download_HornMT(directory):
    """
    https://github.com/asmelashteka/HornMT
    """
    corpus_name = "hornmt"
    dataset_directory = init_routine(directory, corpus_name)

    lang_files = {}
    for lang in ("aar", "amh", "eng", "orm", "som", "tir"):
        download_url = f"https://raw.githubusercontent.com/asmelashteka/HornMT/main/data/{lang}.txt"
        download_path = os.path.join(dataset_directory, f"{lang}.txt")
        ok = download_file(download_url, download_path)
        if not ok:
            raise Exception("Aborting for HornMT!")
        lang_files[lang] = download_path

    for source, target in [
        ("aar", "amh"),
        ("aar", "eng"),
        ("aar", "orm"),
        ("aar", "som"),
        ("aar", "tir"),
        ("amh", "eng"),
        ("amh", "orm"),
        ("amh", "som"),
        ("amh", "tir"),
        ("eng", "orm"),
        ("eng", "som"),
        ("eng", "tir"),
        ("orm", "som"),
        ("orm", "tir"),
        ("som", "tir"),
    ]:
        source_bcp47 = convert_into_bcp47(source)
        if source_bcp47 == UNSUPPORTED_CODE:
            continue
        target_bcp47 = convert_into_bcp47(target)
        if target_bcp47 == UNSUPPORTED_CODE:
            continue
        direction_directory = os.path.join(dataset_directory, f"{source_bcp47}-{target_bcp47}")
        os.makedirs(direction_directory, exist_ok=True)

        source_path = os.path.join(direction_directory, f"{corpus_name}.{source_bcp47}")
        shutil.copyfile(lang_files[source], source_path)
        print(f"Wrote: {source_path}")

        target_path = os.path.join(direction_directory, f"{corpus_name}.{target_bcp47}")
        shutil.copyfile(lang_files[target], target_path)
        print(f"Wrote: {target_path}")

    for filename in lang_files.values():
        os.remove(filename)


def download_minangNLP(directory):
    """
    https://github.com/fajri91/minangNLP
    """
    corpus_name = "minangnlp"
    dataset_directory = init_routine(directory, corpus_name)

    lang_code1 = 'min_Latn'
    lang_code2 = 'ind_Latn'

    direction_directory = os.path.join(dataset_directory, f"{lang_code1}-{lang_code2}")
    os.makedirs(direction_directory, exist_ok=True)

    # min_Latn
    download_url = "https://raw.githubusercontent.com/fajri91/minangNLP/master/translation/wiki_data/src_train.txt"
    download_path = os.path.join(direction_directory, f"{corpus_name}.{lang_code1}")
    ok = download_file(download_url, download_path)
    if not ok:
        raise Exception("Aborting for Minang NLP!")

    # ind
    download_url = "https://raw.githubusercontent.com/fajri91/minangNLP/master/translation/wiki_data/tgt_train.txt"
    download_path = os.path.join(direction_directory, f"{corpus_name}.{lang_code2}")
    ok = download_file(download_url, download_path)
    if not ok:
        raise Exception("Aborting for Minang NLP!")


def download_aau(directory):
    """
    https://github.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages
    """
    corpus_name = "aau"
    dataset_directory = init_routine(directory, corpus_name)

    lang_code1 = "amh_Ethi"
    lang_code2 = "eng_Latn"
    direction_directory = os.path.join(dataset_directory, f"{lang_code1}-{lang_code2}")
    os.makedirs(direction_directory, exist_ok=True)

    download_path = os.path.join(direction_directory, f"{corpus_name}.{lang_code1}")
    ok = concat_url_text_contents_to_file(
        [
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/History/amh_eng/p_amh_ea",
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/Legal/amh_eng/p_amh_ea.txt",
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/News/amh_eng/amh_ea.txt",
        ],
        download_path,
    )
    if not ok:
        raise Exception("Aborting for AAU!")

    download_path = os.path.join(direction_directory, f"{corpus_name}.{lang_code2}")
    ok = concat_url_text_contents_to_file(
        [
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/History/amh_eng/p_eng_ea",
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/Legal/amh_eng/p_eng_ea.txt",
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/News/amh_eng/eng_ea.txt",
        ],
        download_path,
    )
    if not ok:
        raise Exception("Aborting for AAU!")

    lang_code1 = "eng_Latn"
    lang_code2 = "gaz_Latn"
    direction_directory = os.path.join(dataset_directory, f"{lang_code1}-{lang_code2}")
    os.makedirs(direction_directory, exist_ok=True)

    download_path = os.path.join(direction_directory, f"{corpus_name}.{lang_code1}")
    ok = concat_url_text_contents_to_file(
        [
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/Legal/oro_eng/p_eng_eo.txt",
        ],
        download_path,
    )
    if not ok:
        raise Exception("Aborting for AAU!")

    download_path = os.path.join(direction_directory, f"{corpus_name}.{lang_code2}")
    ok = concat_url_text_contents_to_file(
        [
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/Legal/oro_eng/p_oro_eo.txt",
        ],
        download_path,
    )
    if not ok:
        raise Exception("Aborting for AAU!")

    lang_code1 = "eng_Latn"
    lang_code2 = "tir_Ethi"
    direction_directory = os.path.join(dataset_directory, f"{lang_code1}-{lang_code2}")
    os.makedirs(direction_directory, exist_ok=True)

    download_path = os.path.join(direction_directory, f"{corpus_name}.{lang_code1}")
    ok = concat_url_text_contents_to_file(
        [
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/Legal/tig_eng/p_eng_et.txt",
        ],
        download_path,
    )
    if not ok:
        raise Exception("Aborting for AAU!")

    download_path = os.path.join(direction_directory, f"{corpus_name}.{lang_code2}")
    ok = concat_url_text_contents_to_file(
        [
            "https://raw.githubusercontent.com/AAUThematic4LT/Parallel-Corpora-for-Ethiopian-Languages/master/Exp%20I-English%20to%20Local%20Lang/Legal/tig_eng/p_tig_et.txt",
        ],
        download_path,
    )
    if not ok:
        raise Exception("Aborting for AAU!")


def download_NLLBSeed(directory):
    """
    https://github.com/facebookresearch/flores/tree/main/nllb_seed
    """
    corpus_name = "NLLB-Seed"
    dataset_directory = init_routine(directory, corpus_name)

    download_url = (
        "https://tinyurl.com/NLLBSeed"
    )
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for NLLB Seed!")
    download_path = os.path.join(dataset_directory, "NLLB-Seed.zip")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    with zipfile.ZipFile(download_path, "r") as z:
        z.extractall(directory)
    os.remove(download_path)

    for root_dir, _, files in os.walk(dataset_directory):
        for filename in files:
            assert BCP47_REGEX.match(filename), f"Expected BCP47 filename but got: {filename}!"
            new_filename = f'{corpus_name}.{filename}'
            os.rename(os.path.join(root_dir, filename), os.path.join(root_dir, new_filename))


#
# Evaluation datasets.
#
def download_NLLBMD(directory):
    """
    https://github.com/facebookresearch/flores/blob/main/nllb_md/README.md
    """
    # TODO: see what format we want for our eval datasets.
    corpus_name = "NLLB-MD"
    dataset_directory = init_routine(directory, corpus_name)

    download_urls = (
        "https://tinyurl.com/NLLBMDchat",
        "https://tinyurl.com/NLLBMDnews",
        "https://tinyurl.com/NLLBMDhealth"
    )
    for download_url in download_urls:
        response = requests.get(download_url)
        if not response.ok:
            raise Exception(f"Could not download from {download_url} ... aborting for NLLB Seed!")
        download_path = os.path.join(dataset_directory, f"{download_url.split('/')[-1]}.zip")
        open(download_path, "wb").write(response.content)
        print(f"Wrote: {download_path}")

        with zipfile.ZipFile(download_path, "r") as z:
            z.extractall(directory)
        os.remove(download_path)


def download_Flores202(directory, eval_directions: list[str]):
    """
    https://github.com/facebookresearch/flores/blob/main/flores200/README.md
    """
    corpus_name = "flores202"
    dataset_directory = init_routine(directory, corpus_name)
    assert all([BCP47_REGEX.match(direction) for direction in eval_directions]), f"Expected BCP47 direction but got: {eval_directions}!"

    download_url = (
        "https://tinyurl.com/flores200dataset"
    )
    response = requests.get(download_url)
    if not response.ok:
        raise Exception(f"Could not download from {download_url} ... aborting for NLLB Seed!")
    download_path = os.path.join(dataset_directory, f"{corpus_name}.tar.gz")
    open(download_path, "wb").write(response.content)
    print(f"Wrote: {download_path}")

    with tarfile.open(download_path) as tar:
        tar.extractall(dataset_directory)
    os.remove(download_path)

    dataset_path = os.path.join(dataset_directory, "flores200_dataset")
    os.remove(os.path.join(dataset_path, "README"))
    os.remove(os.path.join(dataset_path, "metadata_dev.tsv"))
    os.remove(os.path.join(dataset_path, "metadata_devtest.tsv"))

    dev_path = os.path.join(dataset_path, "dev")
    devtest_path = os.path.join(dataset_path, "devtest")

    for direction in eval_directions:
        src, trg = direction.split("-")

        src_path_dev = os.path.join(dev_path, f"{src}.dev")
        trg_path_dev = os.path.join(dev_path, f"{trg}.dev")
        dev_direction_path = os.path.join(dev_path, f"{src}-{trg}")
        os.makedirs(dev_direction_path, exist_ok=True)
        shutil.copy(src_path_dev, os.path.join(dev_direction_path, f"{corpus_name}.{src}"))
        shutil.copy(trg_path_dev, os.path.join(dev_direction_path, f"{corpus_name}.{trg}"))

        src_path_devtest = os.path.join(devtest_path, f"{src}.devtest")
        trg_path_devtest = os.path.join(devtest_path, f"{trg}.devtest")
        devtest_direction_path = os.path.join(devtest_path, f"{src}-{trg}")
        os.makedirs(devtest_direction_path, exist_ok=True)
        shutil.copy(src_path_devtest, os.path.join(devtest_direction_path, f"{corpus_name}.{src}"))
        shutil.copy(trg_path_devtest, os.path.join(devtest_direction_path, f"{corpus_name}.{trg}"))

    # Delete files directly under dev and devtest directories (but keep the directories)
    for el in os.listdir(dev_path):
        el_path = os.path.join(dev_path, el)
        if os.path.isfile(el_path):
            os.remove(el_path)

    for el in os.listdir(devtest_path):
        el_path = os.path.join(devtest_path, el)
        if os.path.isfile(el_path):
            os.remove(el_path)

    # Rename dev and devtest to flores202_dev and flores202_devtest
    new_dev_path = os.path.join(dataset_path, "flores202_dev")
    new_devtest_path = os.path.join(dataset_path, "flores202_devtest")
    os.rename(dev_path, new_dev_path)
    os.rename(devtest_path, new_devtest_path)

    # Move them up to the root
    shutil.move(new_dev_path, directory)
    shutil.move(new_devtest_path, directory)
    # Remove dataset_path
    shutil.rmtree(dataset_directory)


# Eval datasets links (8 public benchmarks) + Flores 202 above are used for evaluation in the paper:
# https://github.com/facebookresearch/flores/raw/master/data/flores_test_sets.tgz <-flores v1
# https://docs.google.com/forms/d/e/1FAIpQLSfQqhxslVSkBN5ScQ2bvvM0xUVCUnjXxtvkAjupvxm3SSeZGw/viewform <- MADAR, we have to sign a form (found it here: https://camel.abudhabi.nyu.edu/madar-parallel-corpus/)
# https://huggingface.co/datasets/autshumato/blob/main/autshumato.py <- autshumato dataset
# https://huggingface.co/datasets/masakhane/mafand/blob/main/mafand.py and https://github.com/masakhane-io/lafand-mt/tree/main/data/json_files <- Mafand
# https://huggingface.co/datasets/iwslt2017/blob/main/iwslt2017.py <- IWSLT 2017, the paper say this was their test set (depending on the language they pick a different version/year)
# For WMT - similar thing as for IWSLT, depending on the lang they pick a different version (https://huggingface.co/datasets/wmt19)
# check out table 55 & table 56 in the paper
# WAT https://lotus.kuee.kyoto-u.ac.jp/WAT/WAT2019/ <- struggling to find the actual dataset, the answer is somewhere in there
# They used TICO for eval as well but not sure what's the split?

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Script to download individual public corpora for NLLB"
    )
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        required=True,
        help="directory to save downloaded data",
    )
    parser.add_argument(
        "--eval_datasets_path",
        "-e",
        type=str,
        required=False,
        help="directory to save downloaded data",
    )
    args = parser.parse_args()

    directory = args.directory
    non_train_datasets_path = os.path.join(directory, os.pardir, 'non_train_datasets')
    eval_datasets_path = args.eval_datasets_path

    os.makedirs(directory, exist_ok=True)
    if eval_datasets_path:
        os.makedirs(eval_datasets_path, exist_ok=True)
    os.makedirs(non_train_datasets_path, exist_ok=True)

    # Important:
    # By uncommenting the function below and downloading the
    # Mburisano_Covid corpus, you agree to the terms of use found here:
    # https://sadilar.org/index.php/en/guidelines-standards/terms-of-use
    # download_Mburisano_Covid(directory)

    # TODO(gordicaleksa): Should we add both directions for each language pair?
    # I do that for "flat" datasets. i.e. datasets whose structure is "datasetname/lang_files"
    # with no intermediate directory - but we're not consistent.
    download_TIL(directory)
    download_TICO(directory)
    download_IndicNLP(directory, non_train_datasets_path)
    download_Lingala_Song_Lyrics(directory)
    download_FFR(directory)
    download_Mburisano_Covid(directory)
    download_XhosaNavy(directory)
    download_Menyo20K(directory)
    download_FonFrench(directory)
    download_FrenchEwe(directory)
    download_Akuapem(directory)
    download_GiossaMedia(directory)
    download_KinyaSMT(directory)
    download_translation_memories_from_Nynorsk(directory)
    download_mukiibi(directory)
    download_umsuka(directory)
    download_CMU_Haitian_Creole(directory)
    download_Bianet(directory)
    download_HornMT(directory)
    download_minangNLP(directory)
    download_aau(directory)
    download_NLLBSeed(directory)

    # Makes sure that the datasets are in the expected format (see the script header).
    validate_downloaded_data(directory)

    if eval_datasets_path:
        # Evaluation datasets
        # download_NLLBMD(eval_datasets_path)
        download_Flores202(eval_datasets_path, ["eng_Latn-rus_Cyrl", "tur_Latn-uzn_Latn"])