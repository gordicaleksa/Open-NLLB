from datasets import load_dataset
import argparse
import os
from nllb_lang_pairs import NLLB_PAIRS, CCMATRIX_PAIRS

def download_lang_pair_dataset(target_directory: str, src_lang: str, tgt_lang: str) -> None:
    lang_directory = os.path.join(target_directory, f"{src_lang}-{tgt_lang}")
    os.makedirs(lang_directory, exist_ok=True)
    dataset = load_dataset("allenai/nllb", f"{src_lang}-{tgt_lang}")
    f_src = open(os.path.join(lang_directory, f"allenai.nllb.{src_lang}"), 'w', encoding='utf-8')
    f_tgt = open(os.path.join(lang_directory, f"allenai.nllb.{tgt_lang}"), 'w', encoding='utf-8')
    for d in dataset["train"]["translation"]:
        f_src.write(f"{d[src_lang]}\n")
        f_tgt.write(f"{d[tgt_lang]}\n")
    f_src.close()
    f_tgt.close()
    print(f"Wrote {src_lang}-{tgt_lang}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Script to download allenai nllb data from HF hub."
    )
    parser.add_argument(
        "--directory",
        "-d",
        type=str,
        required=True,
        help="directory to save downloaded data",
    )
    parser.add_argument(
        "--minimal",
        "-m",
        help="launch a minimal test to see if everything is ok (two lang pairs)",
        action="store_true"
    )
    args = parser.parse_args()
    target_directory = os.path.join(args.directory, "nllb")
    os.makedirs(target_directory, exist_ok=True)
    if args.minimal:
        for src_lang, tgt_lang in [("ace_Latn", "ban_Latn"), ("amh_Ethi", "nus_Latn")]:
            download_lang_pair_dataset(target_directory, src_lang, tgt_lang)
    else:
        for src_lang, tgt_lang in NLLB_PAIRS + CCMATRIX_PAIRS:
            download_lang_pair_dataset(target_directory, src_lang, tgt_lang)
    print("done")