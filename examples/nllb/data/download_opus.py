"""
Taken from: https://github.com/UKPLab/sentence-transformers/blob/master/examples/training/multilingual/get_parallel_data_opus.py
and subsequently modified.

OPUS (http://opus.nlpl.eu/) is a great collection of different parallel datasets for more than 400 languages.
On the website, you can download parallel datasets for many languages in different formats. I found that
the format "Bottom-left triangle: download plain text files (MOSES/GIZA++)"  requires minimal
overhead for post-processing to get it into a suitable format for this library.

You can use the OPUS dataset to create multilingual sentence embeddings. This script contains code to download
OPUS datasets for the desired languages and to create training files in the right format.

1) First, you need to install OpusTools (https://github.com/Helsinki-NLP/OpusTools/tree/master/opustools_pkg):
pip install opustools

2) Once you have OpusTools installed, you can download data in the right format via:
mkdir parallel-sentences
opus_read -d [CORPUS] -s [SRC_LANG] -t [TRG_LANG] --write parallel-sentences/[FILENAME].tsv.gz   -wm moses -dl opus -p raw

For example:
mkdir parallel-sentences
opus_read -d JW300 -s en -t de --write parallel-sentences/JW300-en-de.tsv.gz -wm moses -dl opus -p raw

This downloads the JW300 Corpus (http://opus.nlpl.eu/JW300.php) for English (en) and German (de) and write the output to
parallel-sentences/JW300-en-de.tsv.gz


####################

This python code automates the download and creation of the parallel sentences files.


"""
import argparse
from collections import defaultdict
import os
import re


from opustools import OpusRead, OpusGet
from tqdm import tqdm


from lang_code_mappings import ISO_639_1_TO_BCP_47_func
from download_parallel_corpora import gzip_extract_and_remove

slavic_langs_codes_minus_hbs = ['be', 'bg', 'cs', 'mk', 'pl', 'ru', 'sk', 'sl', 'uk', 'szl']

german_datasets = [
    "Wikipedia",
    "Europarl",
    "WikiTitles",
    "EMEA",
    "ELRC-5067-SciPar",
    "GNOME",
    "ELRC-2714-EMEA",
    "JRC-Acquis",
    "ELRC_2682",
    "QED",
    "Tanzil",
    "ELRC-1077-EUIPO_law",
    "ELRC-EUIPO_law",
    "News-Commentary",
    "Tatoeba",
    "TED2020",
    "ELITR-ECA",
    "KDE4",
    "MultiUN",
    "NeuLab-TedTalks",
    "ELRC-1121-CORDIS_Results_Brief",
    "ELRC-CORDIS_Results",
    "wikimedia",
    "TED2013",
    "ELRC-EUIPO_list",
    "ECB",
    "ELRC-1117-CORDIS_News",
    "ELRC-CORDIS_News",
    "ELRA-W0201",
    "ELRC-638-Luxembourg.lu",
    "Mozilla-I10n",
    "GlobalVoices",
    "bible-uedin"
]

greek_datasets = [
    "LinguaTools-WikiTitles",
    "Europarl",
    "EMEA",
    "GNOME",
    "ELRC-2711-EMEA",
    "ELRC_2682",
    "ELRC-5067-SciPar",
    "QED",
    "wikimedia",
    "ELITR-ECA",
    "TED2020",
    "SETIMES",
    "ELRC-presscorner_covid",
    "KDE4",
    "NeuLab-TedTalks",
    "ELRC-Press_Releases",
    "GlobalVoices",
    "Wikipedia"
]

french_datasets = [
    "ELRC-EUIPO_law",
    "Europarl",
    "wikimedia",
    "EMEA",
    "ELRC-5067-SciPar",
    "QED",
    "GNOME",
    "JRC-Acquis",
    "Wikipedia",
    "ELRC-2720-EMEA",
    "ELITR-ECA",
    "TED2020",
    "GlobalVoices",
    "News-Commentary",
    "Tatoeba",
    "ELRC-1122-CORDIS_Results_Brief",
    "ELRC-CORDIS_Results",
    "MDN_Web_Docs",
    "KDE4",
    "NeuLab-TedTalks",
    "ECB",
    "ELRC-EUIPO_list",
    "TED2013",
    "Tanzil",
    "ELRC-1118-CORDIS_News",
    "ELRC-CORDIS_News"
]

polish_datasets = [
    "TildeMODEL",
    "ELRC-CORDIS_News",
    "JRC-Acquis",
    "EMEA",
    "ELRC-5067-SciPar",
    "ELRC-2726-EMEA",
    "Europarl v8",
    "QED",
    "GNOME",
    "EUbookshop",
    "EuroPat",
    "ELITR-ECA",
    "TED2020",
    "KDE4",
    "ELRC-1124-CORDIS_Results_Brief",
    "NeuLab-TedTalks",
    "ELRC-presscorner_covid",
    "Wikipedia",
    "TED2013",
    "Tanzil",
]

arabic_datasets = [
    "QED",
    "wikimedia",
    "GNOME",
    "TED2020",
    "Tanzil",
    "NeuLab-TedTalks",
    "News-Commentary",
    "TED2013",
    "Wikipedia",
    "KDE4",
    "bible-uedin",
    "GlobalVoices",
    "infopankki"
]

spanish_datasets = [
    "wikimedia",
    "Europarl",
    "Wikipedia",
    "QED",
    "EMEA",
    "GNOME",
    "JRC-Acquis",
    "ELRC-2722-EMEA",
    "GlobalVoices",
    "ELITR-ECA",
    "SciELO",
    "TED2020",
    "News-Commentary",
    "ELRC-5067-SciPar v1",
]


# Not used atm - experimental.
def get_corpora_names_for_lang_direction_from_opus_website():
    # Note some of the corpora names are not even displayed on the website: e.g. Ubuntu for
    # Croatian, Serbian, and Bosnian can't be seen on the website but the opus tool can fetch it.
    from bs4 import BeautifulSoup

    # TODO: download the html source from the Opus website for analysis here.
    # we can't just scrape from a URL because it doesn't change when we specify the language direction.
    html_path = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/tmp.html"
    with open(html_path, 'r') as f:
        text = f.read()

    soup = BeautifulSoup(text, 'html.parser')
    tables = soup.find_all('table')
    target_string = "other files"  # Our target table has this string in the header
    target_table = None
    for table in tables:
        for row in table.find_all('tr'):
            row_text = row.get_text()
            if target_string in row_text:
                target_table = table

    corpora_names = []
    for i, row in enumerate(target_table.find_all('tr')):
        if i == 0:
            continue  # skipping the table header

        tds = row.find_all('td')
        if len(tds) == 0:
            continue

        cell = tds[0]  # Grab the first cell from the row as it contains the corpora name
        corpora_name = cell.get_text()
        corpora_names.append(corpora_name)

    corpora_names = [re.split(r'\\', repr(el))[0][1:] for el in corpora_names]
    return corpora_names


def get_ignore_corpora_lists():
    # Opus tool doesn't work well for bigger datasets hence adding them to ignore list.
    ignore_corpora_list = defaultdict(list)
    ignore_corpora_list['hr'] = ["OpenSubtitles", "NLLB", "CCMatrix"]
    ignore_corpora_list['bs'] = ["OpenSubtitles", "NLLB"]
    ignore_corpora_list['sr'] = ["OpenSubtitles", "NLLB", "CCMatrix"]
    ignore_corpora_list['be'] = ["NLLB"]
    ignore_corpora_list['bg'] = ["CCMatrix", "OpenSubtitles", "NLLB", "ELRC-EMEA", "ParaCrawl", "CCAligned"]
    ignore_corpora_list['cs'] = ["CCMatrix", "OpenSubtitles", "NLLB", "ELRC-EMEA", "ParaCrawl", "CCAligned", "StanfordNLP-NMT", "DGT"]
    ignore_corpora_list['mk'] = ["CCMatrix", "OpenSubtitles", "NLLB", "CCAligned"]
    ignore_corpora_list['pl'] = ["CCMatrix", "OpenSubtitles", "NLLB", "ELRC-EMEA", "ParaCrawl", "CCAligned", "LinguaTools-WikiTitles", "DGT", "XLEnt"]
    ignore_corpora_list['ru'] = ["CCMatrix", "OpenSubtitles", "NLLB", "ParaCrawl", "CCAligned", "XLEnt", "UNPC", "LinguaTools-WikiTitles", "MultiUN", "WikiMatrix"]
    ignore_corpora_list['sk'] = ["CCMatrix", "OpenSubtitles", "NLLB", "ELRC-EMEA", "ParaCrawl", "CCAligned", "DGT", "ELRC-4154-NTEU_TierA"]
    ignore_corpora_list['sl'] = ["CCMatrix", "OpenSubtitles", "NLLB", "ELRC-EMEA", "ParaCrawl", "CCAligned", "DGT"]
    ignore_corpora_list['uk'] = ["CCMatrix", "NLLB", "ParaCrawl", "CCAligned"]
    ignore_corpora_list['szl'] = ["NLLB"]

    for key in ignore_corpora_list.keys():
        ignore_corpora_list[key] = [el.lower() for el in ignore_corpora_list[key]]
    return ignore_corpora_list


def download_data_from_opus(args):
    # NOTES FOR HBS LANGS:
    # For EUBookshop because of bad alignment file we have to manually download the moses format from Opus website.

    # We don't know what's the referent number of lines for Ubuntu as it is not displayed on the website. It has the similar XML tag parsing issues like GNOME.
    # With careful cleaning we could remove those problematic XML tags before calling the opus tool and
    # thus get some more data but for now we just use the opus tool without any cleaning as it doesn't seem worth the additional effort.

    # GNOME has some XML tags that are messing up the parsing.
    # For Croatian we get more data by just using the opus tool as opposed to downloading a moses file from the website.
    # For Bosnian there is more data in the moses file from the website.
    # For Serbian GNOME has only 147 sentences in the moses file from the website (even though the website reports 0.6M) and the opus tool can't parse it successfully.
    # Edit: I managed to get it to work - turns out the issues was <s> tag being a part of content and messing up the parser.
    # I just added try except around sentence parsing and we ignore such sentences.
    root_directory = os.path.join(args.root_directory, args.trg_lang)
    opus_download_folder = os.path.join(root_directory, 'opus_download')
    use_caching = args.use_caching
    src_lang = args.src_lang
    trg_lang = args.trg_lang

    opus_getter = OpusGet(
        source=src_lang,
        target=trg_lang,
        list_corpora=True,
        suppress_prompts=True
    )
    corpora_list = opus_getter.get_files()

    ignore_corpora_list = get_ignore_corpora_lists()
    ignore_list = ignore_corpora_list[trg_lang]

    allow_list = args.corpora_list
    allow_list = [el.lower() for el in allow_list]
    if len(allow_list) == 1 and allow_list[0] == 'all':
        allow_list = [corpus for corpus in corpora_list if corpus not in ignore_list]
        allow_list = [el.lower() for el in allow_list]

    bad_corpora_list = []
    for cnt, corpus in enumerate(tqdm(corpora_list, total=len(corpora_list))):

        print('*' * 100)
        print(f"{cnt} {'SKIPPING' if corpus in ignore_list else 'Processing'} Corpus: {corpus}, src_lang: {src_lang}, trg_lang: {trg_lang}")
        print('*' * 100)

        if corpus.lower() not in allow_list or corpus.lower() in ignore_list:
            continue

        src_bcp_47 = ISO_639_1_TO_BCP_47_func(src_lang)
        trg_bcp_47 = ISO_639_1_TO_BCP_47_func(trg_lang)

        output_folder = os.path.join(root_directory, corpus, f'{src_bcp_47}-{trg_bcp_47}')
        os.makedirs(output_folder, exist_ok=True)

        output_filename_src = os.path.join(output_folder, "{}.{}.gz".format(corpus, src_bcp_47))
        output_filename_trg = os.path.join(output_folder, "{}.{}.gz".format(corpus, trg_bcp_47))

        if not use_caching or (use_caching and (not os.path.exists(output_filename_src[:-3]) or not os.path.exists(output_filename_trg[:-3]))):
            print(f"Create: {output_filename_src} and {output_filename_trg}")
            try:
                read = OpusRead(
                    directory=corpus,
                    source=src_lang,
                    target=trg_lang,
                    write=[output_filename_src, output_filename_trg],
                    download_dir=opus_download_folder,
                    preprocess='raw',
                    write_mode='moses',
                    suppress_prompts=True
                )
                read.printPairs()
                gzip_extract_and_remove(output_filename_src)
                gzip_extract_and_remove(output_filename_trg)
            except Exception as e:
                bad_corpora_list.append(corpus)

    # Save the bad corpora list:
    bad_corpora_list.sort()
    with open(os.path.join(root_directory, f'bad_corpora_list_{src_lang}-{trg_lang}.txt'), 'w') as f:
        f.write('\n'.join(bad_corpora_list))


def prepare_opus_data_structure():
    in_root_path = "/hdd/open-nllb-data/slavic_data/"
    out_path_mined = "/hdd/open-nllb-data/slavic_data/tmp_out/mined"
    out_path_primary = "/hdd/open-nllb-data/slavic_data/tmp_out/primary"
    mined_datasets = ["CCAligned", "CCMatrix", "NLLB", "ParaCrawl", "WikiMatrix", "XLEnt"]
    for dir_name in os.listdir(in_root_path):
        if dir_name.startswith('tmp'):
            continue

        dir_path = os.path.join(in_root_path, dir_name)
        for subdir_name in os.listdir(dir_path):
            subdir_path = os.path.join(dir_path, subdir_name)
            assert len(os.listdir(subdir_path)) == 1, f'Expected 1 file, got {len(os.listdir(subdir_path))} {os.listdir(subdir_path)}'
            if subdir_name in mined_datasets:
                # move to mined
                target_path = os.path.join(out_path_mined, subdir_name)
                os.makedirs(target_path, exist_ok=True)
                for file in os.listdir(subdir_path):
                    shutil.move(os.path.join(subdir_path, file), target_path)
                os.rmdir(subdir_path)
            else:
                # move to primary
                target_path = os.path.join(out_path_primary, subdir_name)
                os.makedirs(target_path, exist_ok=True)
                for file in os.listdir(subdir_path):
                    shutil.move(os.path.join(subdir_path, file), target_path)
                os.rmdir(subdir_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            "Script to download OPUS data"
        )
    parser.add_argument(
        "--root_directory",
        "-d",
        type=str,
        required=True,
        help="directory to save downloaded data",
    )
    parser.add_argument(
        "--src_lang",
        "-s",
        type=str,
        default="en",
        help="source language in ISO 639-1 format",
    )
    parser.add_argument(
        "--trg_lang",
        "-t",
        type=str,
        default=slavic_langs_codes_minus_hbs,
        help="target language in ISO 639-1 format", nargs="+",
    )
    parser.add_argument("--corpora_list", default=['all'], type=str, nargs="+")
    parser.add_argument(
        '--use_caching',
        '-c',
        action='store_false',
        help='with caching enabled if the output files already exist we skip download & process step for that corpus'
    )

    args = parser.parse_args()

    root_directory = args.root_directory
    os.makedirs(root_directory, exist_ok=True)

    src_lang = args.src_lang
    trg_lang = args.trg_lang

    trg_langs = args.trg_lang
    for trg_lang in trg_langs:
        args.trg_lang = trg_lang
        download_data_from_opus(args)