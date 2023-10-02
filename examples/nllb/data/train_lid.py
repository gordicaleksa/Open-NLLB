# steps:
# 1. choose the data sources
# 2. preprocess the data
# 3. pick the hyperparameters using flores dev set
# 4. step into the source code of fasttext

# ```
# # Replace ipss = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ' _ip_ ', s)
# ```

# ```
# # Remove some special characterss = re.sub(r'([\;\:\|•«\n])', ' ', s)
# ```

# ```
# s = s.replace('&', ' and ')
#     s = s.replace('@', ' at ')
#     s = s.replace('0', ' zero ')
#     s = s.replace('1', ' one ')
#     s = s.replace('2', ' two ')
#     s = s.replace('3', ' three ')
#     s = s.replace('4', ' four ')
#     s = s.replace('5', ' five ')
#     s = s.replace('6', ' six ')
#     s = s.replace('7', ' seven ')
#     s = s.replace('8', ' eight ')
#     s = s.replace('9', ' nine ')
# ```

# or just remove the digits alltogether

# what’s *wordNgrams setting for existing LID models I was using?*

# potentially: analyze the fasttext source code once I start training the supervised model

# Training Parameters. Our best model was trained with softmax loss over two epochs
# with a learning rate of 0.8 and embeddings with 256 dimensions. We discarded words with
# less than a thousand occurrences after upsampling and picked a minimum and maximum
# character n-gram length of two and five respectively, which were assigned a slot in buckets
# of size 1,000,000. All hyperparameters were tuned on Flores-200 dev.

from collections import defaultdict
import os
import random
from tqdm import tqdm

import fasttext

random.seed(42)


def generate_hbs_train_data():
    output_dir = os.path.dirname(os.path.realpath(__file__))

    target_cnt_per_hbs_lang = 3500000
    lang_codes = ["srp_Cyrl", "hrv_Latn", "bos_Latn"]
    primary_data_root = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/HBS_data/primary"
    hbs_data = defaultdict(list)
    cnts = defaultdict(int)
    for dataset_name in tqdm(os.listdir(primary_data_root)):
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
                            # TODO: do all the necessary processing here
                            lines = [f"__label__{tgt_lang} {line.strip()}" for line in lines]
                        cnts[tgt_lang] += len(lines)
                        hbs_data[tgt_lang].extend(lines)

    for key in hbs_data.keys():
        num_lines = len(hbs_data[key])
        permutation = random.sample(range(num_lines), target_cnt_per_hbs_lang)
        hbs_data[key] = [hbs_data[key][i] for i in permutation]

    hbs_lines = []
    for key in hbs_data.keys():
        hbs_lines.extend(hbs_data[key])

    hbs_train_path = os.path.join(output_dir, "hbs.train")
    with open(hbs_train_path, "w") as f:
        f.write("\n".join(hbs_lines))

# srp_path = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/HBS_data/primary/Tatoeba/eng_Latn-srp_Cyrl/Tatoeba.srp_Cyrl"
# eng_path = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/HBS_data/primary/Tatoeba/eng_Latn-srp_Cyrl/Tatoeba.eng_Latn"

# get current file's directory
out_train_path = os.path.join(output_dir, "test.train")

# all_lines = []
# for filepath, label in [(srp_path, "__label__srp_Cyrl"), (eng_path, "__label__eng_Latn")]:
#     with open(filepath, "r") as f:
#         lines = f.readlines()
#         lines = [f"{label} {line.strip()}" for line in lines]
#     all_lines.extend(lines)

# # randomly permute the lines
# import random
# random.shuffle(all_lines)

# with open(out_train_path, "w") as f:
#     f.write("\n".join(all_lines))

# model = fasttext.train_supervised(
#     input=out_train_path, lr=0.5, epoch=25, wordNgrams=2, bucket=200000, dim=256)

model_path = os.path.join(output_dir, "test_lid_model.bin")
# model.save_model(model_path)

model = fasttext.load_model(model_path)

# print(model.predict("This is a test sentence."))
# print(model.predict("Ovo je test rečenica."))

# Don't use QED, KDE4, DGT from primary datasets. That leaves us with how many lines?

flores_val_raw = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/eval_datasets/flores202_dev/eng_Latn-srp_Cyrl/flores202.srp_Cyrl"
with open(flores_val_raw, "r") as f:
    lines = f.readlines()
    lines = [f"{'__label__srp_Cyrl'} {line.strip()}" for line in lines]
flores_val = os.path.join(output_dir, "flores_val.txt")
with open(flores_val, "w") as f:
    f.write("\n".join(lines))

res = model.test(flores_val)
print(res)

print('done')