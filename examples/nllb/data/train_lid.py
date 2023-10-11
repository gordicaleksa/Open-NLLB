from collections import defaultdict
import os
import random
from tqdm import tqdm
from typing import Dict, List
import yaml
import pickle

from pathlib import Path
import fasttext

from dataset_utils import normalize_for_lid, count_lines, DedupFilter, LengthFilter, FilteringCounts, DatasetLine


random.seed(42)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lid_data")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def process_lines(lines: List[str]):
    clean_lines = []

    for line in tqdm(lines):
        line = normalize_for_lid(line)
        if line:
            clean_lines.append(line)

    return clean_lines


def random_subsample(data: Dict[str, List[str]], target_cnt_per_lang: int):
    for key in data.keys():
        num_lines = len(data[key])
        # Use 2 as a margin because we'll be further removing the data in the next steps...
        permutation = random.sample(range(num_lines), min(target_cnt_per_lang * 2, num_lines))
        data[key] = [data[key][i] for i in permutation]

    return data


def filter_data(data: Dict[str, List[str]]):
    with open(Path(OUTPUT_DIR) / "length_factors.yaml", "rt") as fin:
        length_factors = yaml.safe_load(fin)

    for key in data.keys():
        lines = data[key]
        filters = [
            LengthFilter(min_len=5, max_len=1050, max_len_ratio=1.5, length_factors=length_factors, src_lang=key, tgt_lang=""),
            DedupFilter(dedup_pairs=False, max_source_dedup=1, max_target_dedup=None)
        ]
        dataset_counts = FilteringCounts()  # dummy - we don't use it, expected by the filter_line.
        clean_lines = []
        for line in tqdm(lines):
            dataset_counts.total_before += 1
            line = DatasetLine(src=line, tgt=None)
            for fltr in filters:
                line = fltr.filter_line(line, dataset_counts)
                if line is None:
                    break
            if line is None:
                continue
            dataset_counts.total_after += 1
            clean_lines.append(line.src)
        data[key] = clean_lines

    return data


def postprocess_and_add_label(data: Dict[str, List[str]], target_cnt_per_lang: int, is_hbs=True):
    all_lines = []
    for key in data.keys():
        # Subsample
        lines = data[key]
        num_lines = len(lines)
        permutation = random.sample(range(num_lines), min(target_cnt_per_lang, num_lines))
        lines = [lines[i] for i in permutation]
        # Process the lines
        lines = process_lines(lines)
        # Prepend the label, https://github.com/sumanp/text-classification-fastText/blob/master/cooking.train ← example file format that fasttext expects
        lines = [f"__label__{'hbs' if is_hbs else 'non_hbs'} {line}" for line in lines]
        all_lines.extend(lines)

    return all_lines


def generate_hbs_train_data():
    target_cnt_per_lang = 800000  # 3500000
    lang_codes = ["srp_Cyrl", "hrv_Latn", "bos_Latn"]
    primary_data_root = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/HBS_data/primary"
    data = defaultdict(list)
    cnts = defaultdict(int)

    random_subsample_path = os.path.join(OUTPUT_DIR, f"hbs_random_subsample_{target_cnt_per_lang}.pkl")
    if os.path.exists(random_subsample_path):
        with open(random_subsample_path, "rb") as f:
            data = pickle.load(f)
    else:
        # Step 1: collect the data
        for dataset_name in tqdm(os.listdir(primary_data_root)):
            # Don't use QED, KDE4, DGT from primary datasets as they are low quality.
            if dataset_name in ["QED", "KDE4", "DGT"]:
                continue
            dataset_path = os.path.join(primary_data_root, dataset_name)
            for lang_dir in os.listdir(dataset_path):
                tgt_lang = lang_dir.split('-')[-1]
                if tgt_lang in lang_codes:
                    lang_path = os.path.join(dataset_path, lang_dir)
                    for filename in os.listdir(lang_path):
                        if filename.endswith(tgt_lang):
                            file_path = os.path.join(lang_path, filename)
                            with open(file_path, "r") as f:
                                lines = f.readlines()
                            cnts[tgt_lang] += len(lines)
                            data[tgt_lang].extend(lines)

        # Step 2: randomly subsample
        print(f'Subsampling to {target_cnt_per_lang * 2} lines per language.')
        data = random_subsample(data, target_cnt_per_lang)
        with open(random_subsample_path, "wb") as f:
            pickle.dump(data, f)

    # Step 3: length & exact dedup filtering
    print(f'Filtering data...')
    filter_data_path = os.path.join(OUTPUT_DIR, f"hbs_filter_data_{target_cnt_per_lang}.pkl")
    if os.path.exists(filter_data_path):
        with open(filter_data_path, "rb") as f:
            data = pickle.load(f)
    else:
        data = filter_data(data)
        with open(filter_data_path, "wb") as f:
            pickle.dump(data, f)

    # Step 4: postprocess and add label
    print(f'Postprocessing data...')
    postprocess_data_path = os.path.join(OUTPUT_DIR, f"hbs_postprocess_data_{target_cnt_per_lang}.pkl")
    if os.path.exists(postprocess_data_path):
        with open(postprocess_data_path, "rb") as f:
            all_lines = pickle.load(f)
    else:
        all_lines = postprocess_and_add_label(data, target_cnt_per_lang, is_hbs=True)
        with open(postprocess_data_path, "wb") as f:
            pickle.dump(all_lines, f)

    return all_lines


def generate_non_hbs_train_data():
    non_eng_lang_codes = ["deu_Latn", "tur_Latn", "rus_Cyrl", "ell_Grek", "fra_Latn", "pol_Latn", "arb_Arab", "spa_Latn"]
    target_cnt_per_lang = 2500000 // (len(non_eng_lang_codes) + 1)
    data_root_eng = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/HBS_data/primary"
    data_root_non_eng = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/train_datasets"  # Russian, Turkish
    data_root_deu = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/OPUS/Opus_de"
    data_root_ell = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/OPUS/Opus_el"
    data_root_fra = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/OPUS/Opus_fr"
    data_root_pol = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/OPUS/Opus_pl"
    data_root_arb = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/OPUS/Opus_ar"
    data_root_spa = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/OPUS/Opus_es"
    data = defaultdict(list)
    cnts = defaultdict(int)

    random_subsample_path = os.path.join(OUTPUT_DIR, f"non_hbs_random_subsample_{target_cnt_per_lang}.pkl")
    if os.path.exists(random_subsample_path):
        with open(random_subsample_path, "rb") as f:
            data = pickle.load(f)
    else:
        # Step 1: collect the data
        for dataset_name in tqdm(os.listdir(data_root_eng)):
            # Don't use QED, KDE4, DGT from primary datasets.
            if dataset_name in ["QED", "KDE4", "DGT"]:
                continue
            dataset_path = os.path.join(data_root_eng, dataset_name)
            for lang_dir in os.listdir(dataset_path):
                src_lang = lang_dir.split('-')[0]
                assert src_lang == "eng_Latn"
                lang_path = os.path.join(dataset_path, lang_dir)
                for filename in os.listdir(lang_path):
                    if filename.endswith(src_lang):
                        file_path = os.path.join(lang_path, filename)
                        with open(file_path, "r") as f:
                            lines = f.readlines()
                        cnts[src_lang] += len(lines)
                        data[src_lang].extend(lines)
                break  # all lang direction directories will have the same English data.

        for root in [data_root_deu, data_root_ell, data_root_non_eng, data_root_fra, data_root_pol, data_root_arb, data_root_spa]:
            for dataset_name in tqdm(os.listdir(root)):
                dataset_path = os.path.join(root, dataset_name)
                for lang_dir in os.listdir(dataset_path):
                    src_lang, tgt_lang = lang_dir.split('-')
                    if src_lang in non_eng_lang_codes or tgt_lang in non_eng_lang_codes:
                        lang_path = os.path.join(dataset_path, lang_dir)
                        for filename in os.listdir(lang_path):
                            if filename.split('.')[-1] in non_eng_lang_codes:
                                file_path = os.path.join(lang_path, filename)
                                with open(file_path, "r") as f:
                                    lines = f.readlines()
                                cnts[filename.split('.')[-1]] += len(lines)
                                data[filename.split('.')[-1]].extend(lines)

        # Step 2: randomly subsample
        print(f'Subsampling to {target_cnt_per_lang * 2} lines per language.')
        data = random_subsample(data, target_cnt_per_lang)
        with open(random_subsample_path, "wb") as f:
            pickle.dump(data, f)

    # Step 3: length & exact dedup filtering
    filter_data_path = os.path.join(OUTPUT_DIR, f"non_hbs_filter_data_{target_cnt_per_lang}.pkl")
    if os.path.exists(filter_data_path):
        with open(filter_data_path, "rb") as f:
            data = pickle.load(f)
    else:
        data = filter_data(data)
        with open(filter_data_path, "wb") as f:
            pickle.dump(data, f)

    # Step 4: postprocess and add label
    postprocess_data_path = os.path.join(OUTPUT_DIR, f"non_hbs_postprocess_data_{target_cnt_per_lang}.pkl")
    if os.path.exists(postprocess_data_path):
        with open(postprocess_data_path, "rb") as f:
            all_lines = pickle.load(f)
    else:
        all_lines = postprocess_and_add_label(data, target_cnt_per_lang, is_hbs=False)
        with open(postprocess_data_path, "wb") as f:
            pickle.dump(all_lines, f)

    return all_lines


def generate_lid_data(train_path):
    hbs_lines = generate_hbs_train_data()
    non_hbs_lines = generate_non_hbs_train_data()
    # merge and shuffle
    all_lines = hbs_lines + non_hbs_lines
    random.shuffle(all_lines)

    new_filename = f"{len(all_lines)}_{os.path.basename(train_path)}"
    basepath = os.path.dirname(train_path)
    with open(os.path.join(basepath, new_filename), "w") as f:
        f.write("\n".join(all_lines))

    return len(all_lines)


def train_and_save_model(generate_data=True, train_model=True, do_eval=True):
    train_path = os.path.join(OUTPUT_DIR, "hbs_lid.train")
    if generate_data:
        _ = generate_lid_data(train_path)

    model = None
    training_config = {
        "lr": 0.8,
        "epoch": 10,
        "minn": 2,
        "maxn": 5,
        "wordNgrams": 1,
        "minCount": 50,
        "bucket": 1000000,
        "dim": 256
    }
    prefix = "hbs_lid_model"
    for key, value in training_config.items():
        prefix += f"_{key}_{value}"
    model_path = os.path.join(OUTPUT_DIR, f"{prefix}.bin")
    if train_model:
        model = fasttext.train_supervised(
            input=model_path,
            **training_config
        )
        model.save_model(model_path)

    if do_eval:
        if model is None:
            model = fasttext.load_model(model_path)

        target_langs = ["srp_Cyrl", "bos_Latn", "hrv_Latn", "deu_Latn", "tur_Latn", "rus_Cyrl", "ell_Grek", "fra_Latn", "pol_Latn", "arb_Arab", "spa_Latn"]
        hbs_langs = ["srp_Cyrl", "bos_Latn", "hrv_Latn"]
        flores_input_dir = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/eval_datasets/flores202_dev/"
        all_lines = {}
        eng_processed_flag = False
        for lang_dir in os.listdir(flores_input_dir):
            _, target_lang = lang_dir.split('-')
            if target_lang not in target_langs:
                continue
            lang_dir_path = os.path.join(flores_input_dir, lang_dir)
            for filename in os.listdir(lang_dir_path):
                if filename.endswith(target_lang) or (not eng_processed_flag and filename.endswith("eng_Latn")):
                    if filename.endswith("eng_Latn"):
                        eng_processed_flag = True
                    flores_val_raw = os.path.join(lang_dir_path, filename)
                    with open(flores_val_raw, "r") as f:
                        lines = f.readlines()
                        lines = process_lines(lines)
                        lines = [f"__label__{'hbs' if target_lang in hbs_langs else 'non_hbs'} {line.strip()}" for line in lines]
                        all_lines[filename.split('.')[-1]] = lines

        for lang_dir, lines in all_lines.items():
            flores_val = os.path.join(OUTPUT_DIR, f"flores_val_{lang_dir}.txt")
            with open(flores_val, "w") as f:
                f.write("\n".join(lines))
            res = model.test(flores_val)
            print(f"{lang_dir}: {res}")

        print('done')


if __name__ == "__main__":
    train_and_save_model()
