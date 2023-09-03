import argparse
from collections import defaultdict
from enum import Enum
import gzip
import pickle
import pathlib
import os

import matplotlib.pyplot as plt
import numpy as np
import yaml

from dataset_utils import count_lines, FilteringCounts, DedupFilter, DatasetLine
from lang_code_mappings import retrieve_supported_files_and_iso_639_3_codes, ISO_639_3_TO_BCP_47


class FeatureType(Enum):
    dedup = 1
    line_lengths = 2
    num_sentences = 3


UPPER_LINE_LEN_THRESHOLD = 1050
LOWER_LINE_LEN_THRESHOLD = 5

outlier_datasets = defaultdict(int)

def compute_line_lengths(lang_code, file_path, length_factors, lang_line_lengths, verbose, is_gz):
    print(f'Analyzing sentence lengths in {file_path}.')
    length_factor1 = length_factors[lang_code]
    line_lengths1 = []
    with gzip.open(file_path, 'r') if is_gz else open(file_path, 'r') as f:
        for i, line in enumerate(f):
            len1 = len(line) * length_factor1
            line_lengths1.append(len1)
            if (LOWER_LINE_LEN_THRESHOLD < len1 < UPPER_LINE_LEN_THRESHOLD) and verbose:
                outlier_datasets[pathlib.Path(file_path).parent.parent.name] += 1
                print(f'Found a {i+1}. line outlier with length {len1} in {pathlib.Path(file_path).parent.parent.name} above our threshold {UPPER_LINE_LEN_THRESHOLD}.')
    lang_line_lengths[lang_code].extend(line_lengths1)


def analyze_primary_data(args, features: list[FeatureType], langs: list[str] = None):
    length_factors_path = args.length_factors_path
    datasets_root = args.datasets_root
    is_gz = args.is_gz
    verbose = args.verbose

    if FeatureType.dedup in features:
        assert len(langs) == 1, 'Only one lang is supported for deduplication analysis for now.'

    if FeatureType.line_lengths in features:
        length_factors_file_path = length_factors_path
        with open(length_factors_file_path, "rt") as fin:
            length_factors = yaml.safe_load(fin)

    cnt = 0
    for root_dir, _, files in os.walk(datasets_root):
        files_and_lang_directions = retrieve_supported_files_and_iso_639_3_codes(files, is_gz)
        cnt += len(files_and_lang_directions)

    print(f'Number of lang files we found: {cnt}')

    #
    # Step 1: data collection
    #
    lang_num_sentences_dict = defaultdict(int)
    lang_direction_num_sentences = defaultdict(int)
    lang_line_lengths_dict = defaultdict(list)
    cnt_pairs = 0
    duplicates_cnt = 0
    for root_dir, _, files in os.walk(datasets_root):
        files_and_lang_directions = retrieve_supported_files_and_iso_639_3_codes(files, is_gz)
        if len(files_and_lang_directions) == 0:
            continue
        assert len(files_and_lang_directions) % 2 == 0, f'Found {len(files_and_lang_directions)} files in {root_dir}. Expected an even number of files.'
        for i in range(0, len(files_and_lang_directions), 2):
            file1, lang_code1 = files_and_lang_directions[i]
            file2, lang_code2 = files_and_lang_directions[i+1]
            lang_code1 = ISO_639_3_TO_BCP_47[lang_code1][0]
            lang_code2 = ISO_639_3_TO_BCP_47[lang_code2][0]
            file_path1 = os.path.join(root_dir, file1)
            file_path2 = os.path.join(root_dir, file2)

            dataset_counts = FilteringCounts()  # filtering counts for the current dataset
            fltr = DedupFilter(dedup_pairs=True, max_source_dedup=None, max_target_dedup=None)

            cnt_pairs += 1
            if FeatureType.num_sentences in features:
                print(f'{cnt_pairs*2}/{cnt} Counting lines in {file1} and {file2}.')
                lang_num_sentences_dict[lang_code1] += count_lines(file_path1)
                lang_num_sentences_dict[lang_code2] += count_lines(file_path2)
                lang_direction_num_sentences[f'{lang_code1}-{lang_code2}'] += count_lines(file_path1)
            if FeatureType.line_lengths in features:
                if langs is None or lang_code1 in langs:
                    compute_line_lengths(lang_code1, file_path1, length_factors, lang_line_lengths_dict, verbose, is_gz)

                if langs is None or lang_code2 in langs:
                    compute_line_lengths(lang_code2, file_path2, length_factors, lang_line_lengths_dict, verbose, is_gz)

            if FeatureType.dedup in features:
                if lang_code1 in langs or lang_code2 in langs:
                    with gzip.open(file_path1, 'r') if is_gz else open(file_path1, 'r') as f, gzip.open(file_path2, 'r') if is_gz else open(file_path2, 'r') as g:
                        for i, (line1, line2) in enumerate(zip(f, g)):
                            if is_gz:
                                # Convert from bytes to string
                                line1 = line1.decode('utf-8')
                                line2 = line2.decode('utf-8')
                            line = DatasetLine(src=line1, tgt=line2)
                            dataset_counts.total_before += 1
                            line = fltr.filter_line(line, dataset_counts)
                            if line is None:
                                continue
                            dataset_counts.total_after += 1

                    duplicates_cnt += dataset_counts.pair_dedup
                    print(f'Found {dataset_counts.pair_dedup} duplicates for {root_dir}.')

    if FeatureType.dedup in features:
        assert len(langs) == 1, 'Only one lang is supported for deduplication analysis for now.'
        print(f'Found {duplicates_cnt} duplicates for {langs[0]}.')

    if FeatureType.num_sentences in features:
        print(f'Found {len(lang_num_sentences_dict)} langs out of 202.')
        print(f'Found {sum(lang_num_sentences_dict.values())} sentences.')
        print(f'Found {len(lang_direction_num_sentences)} lang directions.')
        with open('lang_num_sentences.pickle', 'wb') as handle:
            pickle.dump(lang_num_sentences_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    #
    # Step 2: Visualize & analyze the information collected above
    #
    if FeatureType.line_lengths in features:
        print(f'Datasets containing length outliers: {outlier_datasets}')
        for lang in lang_line_lengths_dict.keys():
            line_lengths = np.array(lang_line_lengths_dict[lang])
            k = 10
            ind = np.argpartition(line_lengths, -k)[-k:]
            print(f'max {k} elements = {line_lengths[ind]} avg = {np.average(line_lengths)}')

            num_outliers = sum(np.logical_or(line_lengths > UPPER_LINE_LEN_THRESHOLD, line_lengths < LOWER_LINE_LEN_THRESHOLD))
            num_outliers_relative = num_outliers / len(line_lengths)
            print(f'Found {num_outliers} sentence length outliers ({num_outliers_relative}%) in {lang}.')
            # Compute a numpy histogram
            hist, bin_edges = np.histogram(line_lengths, bins=500)
            # Compute the bin centers
            bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
            # Plot the histogram in matplotlib
            plt.plot(bin_centers, hist, label=lang)
            plt.legend()
            plt.show()
            plt.close()

    if FeatureType.num_sentences in features:
        for lang_dict in [lang_num_sentences_dict, lang_direction_num_sentences]:
            log_values = np.log(list(lang_dict.values()))
            keys_log_values = sorted(zip(lang_dict.keys(), log_values), key=lambda x: x[1], reverse=True)
            print(f'Top 10: {keys_log_values[:10]}')
            plt.bar(lang_dict.keys(), log_values)
            plt.xticks(rotation=90)
            plt.show()
            print('ok')


def analyze_dumps():
    # Run analyze_primary_data with raw & filtered data.
    # Then run this function and compare the pickles to see the difference in number of sentences.
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
    parser.add_argument("--verbose", action="store_true",
					help="set this to True to get more information")
    parser.add_argument(
        "--length_factors_path",
        type=str,
        help="Path to the length factors file (created in the stopes repo).",
    )
    args = parser.parse_args()
    analyze_primary_data(args, [FeatureType.num_sentences, FeatureType.line_lengths], langs=None)  # ,'ory_Latn', 'hin_Deva', 'spa_Latn', 'grn_Latn', 'fra_Latn', 'fon_Latn'
    # analyze_dumps()