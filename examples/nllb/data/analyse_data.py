import argparse
from collections import defaultdict
import pickle
import os

import matplotlib.pyplot as plt
import numpy as np

from dataset_utils import count_lines
from lang_code_mappings import retrieve_supported_files_and_iso_639_3_codes


def analyze_primary_data(args):
    datasets_root = args.datasets_root
    is_gz = args.is_gz

    cnt = 0
    for root_dir, _, files in os.walk(datasets_root):
        files_and_lang_directions = retrieve_supported_files_and_iso_639_3_codes(files, is_gz)
        cnt += len(files_and_lang_directions)

    print(f'Number of lang files we found: {cnt}')

    # Count number of lines for each lang
    lang_num_sentences = defaultdict(int)
    cnt_f = 0
    for root_dir, _, files in os.walk(datasets_root):
        files_and_lang_directions = retrieve_supported_files_and_iso_639_3_codes(files, is_gz)
        for (file, lang_code) in files_and_lang_directions:
            cnt_f += 1
            print(f'{cnt_f}/{cnt} Counting lines in {file}.')
            num_lines = count_lines(os.path.join(root_dir, file))
            lang_num_sentences[lang_code] += num_lines

    print(f'Found {len(lang_num_sentences)} langs out of 202.')
    with open('lang_num_sentences.pickle', 'wb') as handle:
        pickle.dump(lang_num_sentences, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Count number of lines for each lang direction.
    lang_direction_num_sentences = defaultdict(int)
    for root_dir, _, files in os.walk(datasets_root):
        files_and_lang_directions = retrieve_supported_files_and_iso_639_3_codes(files, is_gz)
        if len(files_and_lang_directions) == 0:
            continue

        assert len(files_and_lang_directions) == 2, f'Found {len(files_and_lang_directions)} files in {root_dir}.'

        file_0, lang_code_0 = files_and_lang_directions[0]
        file_1, lang_code_1 = files_and_lang_directions[1]

        num_lines_0 = count_lines(os.path.join(root_dir, file_0))
        num_lines_1 = count_lines(os.path.join(root_dir, file_1))

        if num_lines_0 != num_lines_1:
            print(f'Number of lines in {file_0} and {file_1} do not match.')
            continue

        # Note: We could also count the other direction.
        key = f'{lang_code_0}-{lang_code_1}'
        lang_direction_num_sentences[key] += num_lines_0

    print(f'Found {len(lang_direction_num_sentences)} lang directions.')

    # Plot the histogram
    # Plot log values otherwise we won't see the data for most langs.
    log_values = np.log(list(lang_direction_num_sentences.values()))
    plt.bar(lang_direction_num_sentences.keys(), log_values)
    plt.xticks(rotation=90)
    plt.show()


def analyze_dumps():
    with open("lang_num_sentences.pickle", 'rb') as handle:
        dict1 = pickle.load(handle)
    with open("lang_num_sentences_filtered.pickle", 'rb') as handle:
        dict2 = pickle.load(handle)

    relative_values = []
    for k in dict1.keys():
        v1 = dict1[k]
        v2 = dict2[k]
        print(k, abs(v1 - v2), f'{(abs(v1 - v2) / v1) * 100}%')
        relative_values.append((abs(v1 - v2) / v1) * 100)

    plt.bar(dict1.keys(), relative_values)
    plt.xticks(rotation=90)
    plt.show()
    print('ok')

if __name__ == '__main__':
    #
    # Note: expects that you've already run the `modify_datasets_structure.py` script.
    # The datasets should have the following structure:
    #   - datasets_root
    #       - dataset_name
    #           - lang_code_1-lang_code_2
    #               - data_file.lang_code_1
    #               - data_file.lang_code_2
    #           - lang_code_3-lang_code_4
    #               - data_file.lang_code_3
    #               - data_file.lang_code_4
    #
    parser = argparse.ArgumentParser(
        "Script to analyze certain statistics of the primary data."
    )
    parser.add_argument(
        "--datasets_root",
        "-d",
        type=str,
        required=True,
        help="Root directory where download_parallel_corpora.py downloaded the data.",
    )
    parser.add_argument("--is_gz", action="store_true",
					help="set this flag if your files are gzipped (will be the case for output of the filtering stage)")
    parser.add_argument(
        "--extended_langs_path",
        "-p",
        type=str,
        required=True,
        help="extended list of 202 639_3 ISO codes + some macro-language codes.",
    )
    args = parser.parse_args()
    analyze_primary_data(args)
    analyze_dumps()