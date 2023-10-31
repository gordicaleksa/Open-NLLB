import os
from collections import defaultdict


import fairseq.data.indexed_dataset as indexed_dataset


root = "/home/aleksa/Projects/nllb/stopes/stopes/pipelines/prepare_data/processed_data_hbs_primary_and_mined_and_valid/data_bin"


num_tokens_dict = defaultdict(list)
num_tokens_wo_eos_dict = defaultdict(list)
num_sentences_dict = defaultdict(list)

for shard_name in os.listdir(root):
    shard_path = os.path.join(root, shard_name)
    files = [file for file in os.listdir(shard_path) if file.endswith('.idx') and file.startswith('train')]
    file_paths = [os.path.join(shard_path, file) for file in files]
    for file_path in file_paths:
        ds = indexed_dataset.MMapIndexedDataset(file_path[:-4])
        num_tokens = sum(ds.sizes)
        num_tokens_wo_eos = num_tokens - len(ds.sizes)
        lang_code = file_path.split('/')[-1].split('.')[-2].split('_')[0]
        num_sentences_dict[lang_code].append(len(ds.sizes))
        num_tokens_dict[lang_code].append(num_tokens)
        num_tokens_wo_eos_dict[lang_code].append(num_tokens_wo_eos)


aggregated_dict = {}
for key in num_tokens_dict:
    aggregated_dict[key] = {
        'num_tokens': sum(num_tokens_dict[key]),
        'num_tokens_wo_eos': sum(num_tokens_wo_eos_dict[key]),
        'num_sentences': sum(num_sentences_dict[key]),
    }
