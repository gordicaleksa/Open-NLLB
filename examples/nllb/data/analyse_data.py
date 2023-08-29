import argparse
from collections import defaultdict
import os

import numpy as np

from examples.nllb.data.utils import count_lines
from examples.nllb.data.iso_code_mappings import ISO_CODE_MAPPER_1_TO_3, FILTERED_LANG_CODES


def analyze_primary_data(args):
    datasets_root = args.datasets_root
    extended_langs_path = args.extended_langs_path

    with open(extended_langs_path, 'r') as f:
        SUPPORTED_ISO_3_LANG_CODES_AND_SCRIPT = f.readlines()[0].strip().split(',')
        SUPPORTED_ISO_3_LANG_CODES = [lang.split('_')[0] for lang in SUPPORTED_ISO_3_LANG_CODES_AND_SCRIPT]

    def retrieve_supported_files_and_directions(files):
        new_files = []

        for file in files:
            suffix = file.split('.')[-1]
            if suffix in FILTERED_LANG_CODES:
                continue
            if file in SUPPORTED_ISO_3_LANG_CODES_AND_SCRIPT:
                new_files.append((file, file.split('_')[0]))
            elif suffix in SUPPORTED_ISO_3_LANG_CODES_AND_SCRIPT:
                new_files.append((file, suffix.split('_')[0]))
            elif suffix in SUPPORTED_ISO_3_LANG_CODES:
                new_files.append((file, suffix))
            elif suffix in ISO_CODE_MAPPER_1_TO_3.keys():
                new_files.append((file, ISO_CODE_MAPPER_1_TO_3[suffix]))
            else:
                print(f'Skipping {os.path.join(root_dir, file)}.')

        return new_files

    cnt = 0
    for root_dir, _, files in os.walk(datasets_root):
        files_and_lang_directions = retrieve_supported_files_and_directions(files)
        cnt += len(files_and_lang_directions)

    print(f'Number of lang files we found: {cnt}')

    # Count number of lines for each lang
    lang_num_sentences = defaultdict(int)
    cnt_f = 0
    for root_dir, _, files in os.walk(datasets_root):
        files_and_lang_directions = retrieve_supported_files_and_directions(files)
        for (file, lang_code) in files_and_lang_directions:
            cnt_f += 1
            print(f'{cnt_f}/{cnt} Counting lines in {file}.')
            num_lines = count_lines(os.path.join(root_dir, file))
            lang_num_sentences[lang_code] += num_lines

    print(f'Found {len(lang_num_sentences)} langs out of 202.')

    # Count number of lines for each lang direction.
    lang_direction_num_sentences = defaultdict(int)
    for root_dir, _, files in os.walk(datasets_root):
        if len(files) == 0:
            continue

        files_and_lang_directions = retrieve_supported_files_and_directions(files)

        for i in range(len(files_and_lang_directions)):
            for j in range(len(files_and_lang_directions)):
                if i == j:
                    continue

                file_i, lang_code_i = files_and_lang_directions[i]
                file_j, lang_code_j = files_and_lang_directions[j]

                num_lines_i = count_lines(os.path.join(root_dir, file_i))
                num_lines_j = count_lines(os.path.join(root_dir, file_j))
                if num_lines_i != num_lines_j:
                    print(f'Number of lines in {file_i} and {file_j} do not match.')
                    continue

                key = f'{lang_code_i}-{lang_code_j}'
                lang_direction_num_sentences[key] += num_lines_i

    print(f'Found {len(lang_direction_num_sentences)} lang directions.')

    # Plot the histogram
    import matplotlib.pyplot as plt

    # Plot log values otherwise we won't see the data for most langs.
    log_values = np.log(list(lang_direction_num_sentences.values()))
    plt.bar(lang_direction_num_sentences.keys(), log_values)
    plt.xticks(rotation=90)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Script to download individual public copora for NLLB"
    )
    parser.add_argument(
        "--datasets_root",
        "-d",
        type=str,
        required=True,
        help="Root directory where download_parallel_corpora.py downloaded the data.",
    )
    parser.add_argument(
        "--extended_langs_path",
        "-p",
        type=str,
        required=True,
        help="extended list of 202+ ISO codes - added by manual inspection, added macro-langs.",
    )
    args = parser.parse_args()
    analyze_primary_data(args)