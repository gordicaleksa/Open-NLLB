import argparse
from collections import defaultdict
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from enum import Enum
import gzip
import json
import math
import pickle
import pathlib
import os

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import yaml
import fasttext
from huggingface_hub import hf_hub_download

from dataset_utils import count_lines, FilteringCounts, DedupFilter, DatasetLine
from lang_code_mappings import retrieve_supported_files_and_iso_639_3_codes, ISO_639_3_TO_BCP_47


class FeatureType(Enum):
    dedup = 1
    line_lengths = 2
    num_sentences = 3
    lid = 4


UPPER_LINE_LEN_THRESHOLD = 1050
LOWER_LINE_LEN_THRESHOLD = 5


def lid_worker(lines, lang_code):
    # TODO: fasttext models are non-pickable so this was a suboptimal solution I came up with.
    model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
    lid_model = fasttext.load_model(model_path)

    lid_model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lid201-model.bin")
    open_lid_model = fasttext.load_model(lid_model_path)
    models = [["nllb-lid", lid_model], ["open-lid", open_lid_model]]

    data = []
    for line in lines:
        line = line.strip()
        output = {}
        for (model_name, model) in models:
            pred = model.predict(line, k=2)
            pred = [list(pred[0]), list(pred[1])]  # convert from numpy to list so that we can save it later on without pickle.
            if pred[0][0] != f'__label__{lang_code}' and pred[1][0] >= 0.95 and len(line) > 25:  # most LID models only become confident after 100 chars...
                output[model_name] = [line, pred]
        if output:
            data.append(output)

    return data


def lid_predict_parallel(models, lang_code, file_path, is_gz, lid_per_line_dict, corpus_name):
    num_chunks = 8
    assert isinstance(models, list), f'Expected a list of models, got {type(models)}.'
    with gzip.open(file_path, 'r') if is_gz else open(file_path, 'r') as f:
        num_lines = count_lines(file_path)
        num_lines_per_chunk = math.ceil(num_lines / num_chunks)
        src_lines = f.readlines()
        chunks = [src_lines[i:i + num_lines_per_chunk] for i in range(0, len(src_lines), num_lines_per_chunk)]

    with ProcessPoolExecutor(max_workers=num_chunks) as executor:
        futures = [
            executor.submit(lid_worker, chunk, lang_code)
            for chunk in chunks
        ]
        with tqdm(total=num_chunks) as pbar:
            for _ in concurrent.futures.as_completed(futures):
                pbar.update(1)
        for future in futures:
            data = future.result()
            lid_per_line_dict[f'{corpus_name}_{lang_code}'].extend(data)


def lid_predict_serial(models, lang_code, file_path, is_gz, lid_per_line_dict, corpus_name):
    assert isinstance(models, list), f'Expected a list of models, got {type(models)}.'
    with gzip.open(file_path, 'r') if is_gz else open(file_path, 'r') as f:
        for i, line in enumerate(tqdm(f, total=count_lines(file_path))):
            line = line.strip()
            for (model_name, model) in models:
                output = {}
                pred = model.predict(line, k=2)
                pred = [list(pred[0]), list(pred[1])]  # convert from numpy to list so that we can save it later on without pickle.
                if pred[0][0] != f'__label__{lang_code}' and pred[1][0] >= 0.95 and len(line) > 25:
                    output[model_name] = [line, pred]
            if output:
                lid_per_line_dict[f'{corpus_name}_{lang_code}'].append(output)


def compute_line_lengths(lang_code, file_path, length_factors, lang_line_lengths, verbose, is_gz):
    print(f'Analyzing sentence lengths in {file_path}.')
    length_factor1 = length_factors[lang_code]
    line_lengths1 = []
    with gzip.open(file_path, 'r') if is_gz else open(file_path, 'r') as f:
        for i, line in enumerate(f):
            len1 = len(line) * length_factor1
            line_lengths1.append(len1)
            if not (LOWER_LINE_LEN_THRESHOLD < len1 < UPPER_LINE_LEN_THRESHOLD) and verbose:
                print(f'Found a {i+1}. line outlier with length {len1} in {pathlib.Path(file_path).parent.parent.name} above our threshold {UPPER_LINE_LEN_THRESHOLD}.')
    lang_line_lengths[lang_code].extend(line_lengths1)


def analyze_primary_data(args, features: list[FeatureType], langs: list[str] = None):
    length_factors_path = args.length_factors_path
    datasets_root = args.datasets_root
    is_gz = args.is_gz
    verbose = args.verbose

    if FeatureType.lid in features:
        model_path = hf_hub_download(repo_id="facebook/fasttext-language-identification", filename="model.bin")
        lid_model = fasttext.load_model(model_path)

        lid_model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lid201-model.bin")
        open_lid_model = fasttext.load_model(lid_model_path)

        lid_out_dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lid_out_results")
        os.makedirs(lid_out_dir_path, exist_ok=True)

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
    duplicates_dict = defaultdict(lambda: defaultdict(int))
    cnt_pairs = 0
    duplicates_cnt = 0

    # If we put these 2 here we're doing global dedup, put them inside of the loop for corpus-level dedup.
    dataset_counts = FilteringCounts()  # filtering counts for the current dataset
    fltr = DedupFilter(dedup_pairs=True, max_source_dedup=None, max_target_dedup=None)

    lid_per_line_dict = defaultdict(list)

    langs_set = set()
    for i, (root_dir, _, files) in enumerate(os.walk(datasets_root)):
        files_and_lang_directions = retrieve_supported_files_and_iso_639_3_codes(files, is_gz)
        if len(files_and_lang_directions) == 0:
            continue
        assert len(files_and_lang_directions) % 2 == 0, f'Found {len(files_and_lang_directions)} files in {root_dir}. Expected an even number of files.'
        for i in range(0, len(files_and_lang_directions), 2):
            corpus_name = pathlib.Path(root_dir).parent.name
            lang_direction = pathlib.Path(root_dir).name
            file1 = files_and_lang_directions[i][0]
            file2 = files_and_lang_directions[i+1][0]
            lang_code1 = file1.split('.')[-1]
            lang_code2 = file2.split('.')[-1]
            langs_set.add(lang_code1)
            langs_set.add(lang_code2)
            file_path1 = os.path.join(root_dir, file1)
            file_path2 = os.path.join(root_dir, file2)

            cnt_pairs += 1
            if FeatureType.num_sentences in features:
                # print(f'{cnt_pairs*2}/{cnt} Counting lines in {file1} and {file2}.')
                if langs and lang_code1 in langs:
                    lang_num_sentences_dict[lang_code1] += count_lines(file_path1)

                if langs and lang_code2 in langs:
                    lang_num_sentences_dict[lang_code2] += count_lines(file_path2)

                if langs and lang_code1 in langs and lang_code2 in langs:
                    lang_direction_num_sentences[lang_direction] += count_lines(file_path1)
            if FeatureType.line_lengths in features:
                if langs is None or lang_code1 in langs:
                    compute_line_lengths(lang_code1, file_path1, length_factors, lang_line_lengths_dict, verbose, is_gz)

                if langs is None or lang_code2 in langs:
                    compute_line_lengths(lang_code2, file_path2, length_factors, lang_line_lengths_dict, verbose, is_gz)

            if FeatureType.lid in features:
                if langs is None or lang_code1 in langs:
                    lid_predict_parallel([["nllb-lid", lid_model], ["open-lid", open_lid_model]], lang_code1, file_path1, is_gz, lid_per_line_dict, corpus_name)

                if langs is None or lang_code2 in langs:
                    lid_predict_parallel([["nllb-lid", lid_model], ["open-lid", open_lid_model]], lang_code2, file_path2, is_gz, lid_per_line_dict, corpus_name)

                with open(os.path.join(lid_out_dir_path, f'lid_per_line_dict_{str(i).zfill(3)}.json'), 'w', encoding="utf-8") as fp:
                    json.dump(dict(lid_per_line_dict), fp, indent=4, ensure_ascii=False)

            if FeatureType.dedup in features:
                if langs is None or (lang_code1 in langs and lang_code2 in langs):  # pairwise dedup hence and operator.
                    with gzip.open(file_path1, 'r') if is_gz else open(file_path1, 'r') as f, gzip.open(file_path2, 'r') if is_gz else open(file_path2, 'r') as g:
                        for i, (line1, line2) in enumerate(tqdm(zip(f, g), total=count_lines(file_path1))):
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
                    duplicates_dict[corpus_name][lang_direction] += dataset_counts.pair_dedup
                    print(f'Found {dataset_counts.pair_dedup} duplicates for {root_dir}.')

    print(langs_set)
    if FeatureType.dedup in features:
        print(duplicates_dict)
        print(f'Found {duplicates_cnt} duplicates for {langs[0]}.')

    if FeatureType.num_sentences in features:
        print(f'Found {len(lang_num_sentences_dict)} langs out of 202.')
        print(f'Found {sum(lang_num_sentences_dict.values())} sentences.')
        print(f'Found {len(lang_direction_num_sentences)} lang directions.')
        # with open('lang_num_sentences.pickle', 'wb') as handle:
        #     pickle.dump(lang_num_sentences_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    #
    # Step 2: Visualize & analyze the information collected above
    #
    if FeatureType.line_lengths in features:
        for lang in lang_line_lengths_dict.keys():
            line_lengths = np.array(lang_line_lengths_dict[lang])
            k = 10
            ind = np.argpartition(line_lengths, -k)[-k:]
            print(f'max {k} elements = {line_lengths[ind]} avg = {np.average(line_lengths)}')

            num_outliers = sum(np.logical_or(line_lengths > UPPER_LINE_LEN_THRESHOLD, line_lengths < LOWER_LINE_LEN_THRESHOLD))
            num_outliers_relative = num_outliers / len(line_lengths)
            print(f'Found {num_outliers} sentence length outliers ({num_outliers_relative}%) in {lang}.')
            # Compute a numpy histogram
            non_outlier_line_lengths = line_lengths[np.logical_and(line_lengths < UPPER_LINE_LEN_THRESHOLD, line_lengths > LOWER_LINE_LEN_THRESHOLD)]
            hist, bin_edges = np.histogram(non_outlier_line_lengths, bins=500)
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


#
# Some helper functions (safe to ignore).
#
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


def duplicate_analysis():
    # Hacky.
    # You have to run the dedup analysis using `analyze_primary_data` and save some of the dictionaries.
    dups_corpus_direction_path = "/home/aleksa/Projects/nllb/fairseq/dedup_corpus_lang_dir.json"
    with open(dups_corpus_direction_path, "rt") as fin:
        dups_corpus_direction = json.load(fin)

    aggregate_dups = defaultdict(int)
    for key in dups_corpus_direction.keys():
        value = dups_corpus_direction[key]
        aggregate_dups[key] = sum(value.values())

    # sort the dictionary by value
    aggregate_dups = dict(sorted(aggregate_dups.items(), key=lambda item: item[1], reverse=True))
    for corpus_name in aggregate_dups.keys():
        print(corpus_name, aggregate_dups[corpus_name])

    dups_path = "/home/aleksa/Projects/nllb/fairseq/lang_directions_duplicates.json"
    num_sentences_path = "/home/aleksa/Projects/nllb/fairseq/lang_directions_num_sentences.json"

    with open(dups_path, "rt") as fin:
        dups = json.load(fin)

    with open(num_sentences_path, "rt") as fin:
        num_sentences = json.load(fin)

    percentage_dict = {}

    for lang_direction, num in num_sentences.items():
        percentage_dict[lang_direction] = (dups[lang_direction] / num)*100

    percentage_dict = dict(sorted(percentage_dict.items(), key=lambda item: item[1], reverse=True))
    with open("/home/aleksa/Projects/nllb/fairseq/lang_directions_duplicates_percentage.json", "wt") as fout:
        json.dump(percentage_dict, fout, indent=4)


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
    slavic_langs = [
        'bos_Latn',
        'hrv_Latn',
        'pol_Latn',
        'szl_Latn',
        'rus_Cyrl',
        'srp_Cyrl',
        'slk_Latn',
        'slv_Latn',
        'bul_Cyrl',
        'ces_Latn',
        'ukr_Cyrl',
        'mkd_Cyrl',
        'bel_Cyrl'
    ]
    hbs_langs = ['bos_Latn', 'hrv_Latn', 'srp_Cyrl']
    root = args.datasets_root
    slavic_without_hbs_langs = list(set(slavic_langs) - set(hbs_langs))
    for lang in slavic_without_hbs_langs:
        args.datasets_root = os.path.join(root, lang.split('_')[0])
        analyze_primary_data(args, [FeatureType.lid], langs=slavic_without_hbs_langs)
    # analyze_dumps()
    # duplicate_analysis()