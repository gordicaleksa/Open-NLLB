import argparse
import os
import re
import string
import shutil

from tqdm import tqdm


from dataset_utils import count_lines


# This dictionary is a mapping between Serbian Cyrillic and Latin.
# Found it here: https://github.com/opendatakosovo/cyrillic-transliteration/blob/master/cyrtranslit/mapping.py
SR_CYR_TO_LAT_DICT = {
    u'А': u'A', u'а': u'a',
    u'Б': u'B', u'б': u'b',
    u'В': u'V', u'в': u'v',
    u'Г': u'G', u'г': u'g',
    u'Д': u'D', u'д': u'd',
    u'Ђ': u'Đ', u'ђ': u'đ',
    u'Е': u'E', u'е': u'e',
    u'Ж': u'Ž', u'ж': u'ž',
    u'З': u'Z', u'з': u'z',
    u'И': u'I', u'и': u'i',
    u'Ј': u'J', u'ј': u'j',
    u'К': u'K', u'к': u'k',
    u'Л': u'L', u'л': u'l',
    u'Љ': u'Lj', u'љ': u'lj',
    u'М': u'M', u'м': u'm',
    u'Н': u'N', u'н': u'n',
    u'Њ': u'Nj', u'њ': u'nj',
    u'О': u'O', u'о': u'o',
    u'П': u'P', u'п': u'p',
    u'Р': u'R', u'р': u'r',
    u'С': u'S', u'с': u's',
    u'Т': u'T', u'т': u't',
    u'Ћ': u'Ć', u'ћ': u'ć',
    u'У': u'U', u'у': u'u',
    u'Ф': u'F', u'ф': u'f',
    u'Х': u'H', u'х': u'h',
    u'Ц': u'C', u'ц': u'c',
    u'Ч': u'Č', u'ч': u'č',
    u'Џ': u'Dž', u'џ': u'dž',
    u'Ш': u'Š', u'ш': u'š',
}


# Copied all below from Open-NLLB-stopes: https://github.com/gordicaleksa/Open-NLLB-stopes
UNICODE_PUNCT = {
    "，": ",",
    "。": ".",
    "、": ",",
    "„": '"',
    "”": '"',
    "“": '"',
    "«": '"',
    "»": '"',
    "１": '"',
    "」": '"',
    "「": '"',
    "《": '"',
    "》": '"',
    "´": "'",
    "∶": ":",
    "：": ":",
    "？": "?",
    "！": "!",
    "（": "(",
    "）": ")",
    "；": ";",
    "–": "-",
    "—": " - ",
    "．": ". ",
    "～": "~",
    "’": "'",
    "…": "...",
    "━": "-",
    "〈": "<",
    "〉": ">",
    "【": "[",
    "】": "]",
    "％": "%",
    "►": "-",
}


NON_PRINTING_CHARS_RE = re.compile(
    f"[{''.join(map(chr, list(range(0,32)) + list(range(127,160))))}]"
)


UNICODE_PUNCT_RE = re.compile(f"[{''.join(UNICODE_PUNCT.keys())}]")


PUNCT_OR_NON_PRINTING_CHARS_RE = re.compile(
    (UNICODE_PUNCT_RE.pattern + NON_PRINTING_CHARS_RE.pattern).replace("][", "")
)


def process_line(line):
    line = PUNCT_OR_NON_PRINTING_CHARS_RE.sub("", line)
    line = re.sub(r'\s', '', line)  # Remove all white spaces.
    line = line.replace('-', '')  # Remove all dashes.
    line = line.replace('_', '')  # Remove all underscores.
    line = line.translate(str.maketrans('', '', string.punctuation))  # Remove all punctuation.
    line = line.translate(str.maketrans('', '', '0123456789'))  # Remove all digits.
    return line


def sort_eng_files_first(paths):
    paths.sort(key=lambda x: 0 if "eng" in os.path.basename(x).split('.')[-1] else 1)
    return paths


def place_Cyrillic_and_Latin_files(root_directory, src_lang_iso_639_3, trg_lang_iso_639_3):
    assert src_lang_iso_639_3 == "eng", f'Expected src_lang_iso_639_3 to be "eng" but got {src_lang_iso_639_3}'
    src_lang_script = "Latn"

    visited = set()
    for root_dir, _, files in os.walk(root_directory):
        if len(files) == 0 or len(files) == 2:  # If either empty or already processed.
            continue

        if root_dir in visited:
            continue

        print('*' * 100)
        print(f'Processing: {root_dir}')
        print('*' * 100)

        # 2 original files + 4 tmp files
        assert len(files) == 6, f'Expected 6 files in the directory: {root_dir} but got {len(files)}'

        parent_dir_path = os.path.abspath(os.path.join(root_dir, os.pardir))
        corpus_name = os.path.basename(parent_dir_path)
        child_dir_paths = [os.path.join(parent_dir_path, child_dir) for child_dir in os.listdir(parent_dir_path)]
        assert len(child_dir_paths) <= 2, f'Expected 2 child dirs in the parent dir: {parent_dir_path} but got {len(child_dir_paths)}'
        for child_dir_path in child_dir_paths:
            visited.add(child_dir_path)

        # Prepare the output directories and files.
        lang_direction_latn = f'{src_lang_iso_639_3}_{src_lang_script}-{trg_lang_iso_639_3}_Latn'
        lang_direction_latn_path = os.path.join(parent_dir_path, lang_direction_latn)
        os.makedirs(lang_direction_latn_path, exist_ok=True)
        lang_direction_cyrl = f'{src_lang_iso_639_3}_{src_lang_script}-{trg_lang_iso_639_3}_Cyrl'
        lang_direction_cyrl_path = os.path.join(parent_dir_path, lang_direction_cyrl)
        os.makedirs(lang_direction_cyrl_path, exist_ok=True)

        out_files_latn_dir = [os.path.join(lang_direction_latn_path, el) for el in [f"{corpus_name}.{src_lang_iso_639_3}_{src_lang_script}", f"{corpus_name}.{trg_lang_iso_639_3}_Latn"]]
        out_files_cyrl_dir = [os.path.join(lang_direction_cyrl_path, el) for el in [f"{corpus_name}.{src_lang_iso_639_3}_{src_lang_script}", f"{corpus_name}.{trg_lang_iso_639_3}_Cyrl"]]

        # Collect ALL current files in Latn/Cyrl directories.
        files_latn_dir = [os.path.join(lang_direction_latn_path, el) for el in os.listdir(lang_direction_latn_path)]
        files_cyrl_dir = [os.path.join(lang_direction_cyrl_path, el) for el in os.listdir(lang_direction_cyrl_path)]

        # Get the non-tmp original files, count the number of lines in them (for later verification) and remove them.
        orig_num_lines_src = 0
        orig_num_lines_trg = 0
        non_tmp_files_latn_dir = sort_eng_files_first([f for f in files_latn_dir if not os.path.basename(f).startswith("tmp")])
        if len(non_tmp_files_latn_dir) > 0:
            orig_num_lines_src += count_lines(non_tmp_files_latn_dir[0])
            orig_num_lines_trg += count_lines(non_tmp_files_latn_dir[1])
        for fpath in non_tmp_files_latn_dir: os.remove(fpath)
        non_tmp_files_cyrl_dir = sort_eng_files_first([f for f in files_cyrl_dir if not os.path.basename(f).startswith("tmp")])
        if len(non_tmp_files_cyrl_dir) > 0:
            orig_num_lines_src += count_lines(non_tmp_files_cyrl_dir[0])
            orig_num_lines_trg += count_lines(non_tmp_files_cyrl_dir[1])
        for fpath in non_tmp_files_cyrl_dir: os.remove(fpath)

        # Collect current tmp files.
        cyrl_files_from_latn_dir = sort_eng_files_first([f for f in files_latn_dir if os.path.basename(f).startswith("tmp") and "Cyrl" in os.path.basename(f).split('.')[-1]])
        cyrl_files_from_cyrl_dir = sort_eng_files_first([f for f in files_cyrl_dir if os.path.basename(f).startswith("tmp") and "Cyrl" in os.path.basename(f).split('.')[-1]])
        latn_files_from_latn_dir = sort_eng_files_first([f for f in files_latn_dir if os.path.basename(f).startswith("tmp") and "Latn" in os.path.basename(f).split('.')[-1]])
        latn_files_from_cyrl_dir = sort_eng_files_first([f for f in files_cyrl_dir if os.path.basename(f).startswith("tmp") and "Latn" in os.path.basename(f).split('.')[-1]])

        for files in [cyrl_files_from_latn_dir, cyrl_files_from_cyrl_dir, latn_files_from_latn_dir, latn_files_from_cyrl_dir]:
            assert len(files) == 0 or len(files) == 2, f'Expected 0 or 2 files but got {len(files)}'

        # Grab partial data from the tmp files and merge it.
        for out_files, in_files in [
            (out_files_latn_dir, [latn_files_from_cyrl_dir, latn_files_from_latn_dir]),
            (out_files_cyrl_dir, [cyrl_files_from_cyrl_dir, cyrl_files_from_latn_dir])
            ]:
            src_latn_out_path = out_files[0]
            trg_latn_out_path = out_files[1]
            with open(src_latn_out_path, "w") as out_src_f, open(trg_latn_out_path, "w") as out_trg_f:
                for current_in_files in in_files:
                    if len(current_in_files) > 0:
                        src_file_path = current_in_files[0]
                        trg_file_path = current_in_files[1]
                        with open(src_file_path, "r") as in_src_f, open(trg_file_path, "r") as in_trg_f:
                            src_lines = in_src_f.readlines()
                            trg_lines = in_trg_f.readlines()
                            for (src_line, trg_line) in tqdm(zip(src_lines, trg_lines), total=len(src_lines)):
                                out_src_f.write(src_line)
                                out_trg_f.write(trg_line)

        #
        # Make sure that the new number of lines is the same as the original number of lines (before Cyrillic/Latin separation)
        #
        new_num_lines = 0
        for fpath in [out_files_latn_dir[0], out_files_cyrl_dir[0]]:
            new_num_lines += count_lines(fpath)

        assert orig_num_lines_src == orig_num_lines_trg == new_num_lines, f'Expected the same number of lines in the original files and the new files but got {orig_num_lines_src} and {new_num_lines}'

        new_num_lines = 0
        for fpath in [out_files_latn_dir[1], out_files_cyrl_dir[1]]:
            new_num_lines += count_lines(fpath)

        assert orig_num_lines_src == orig_num_lines_trg == new_num_lines, f'Expected the same number of lines in the original files and the new files but got {orig_num_lines_src} and {new_num_lines}'

        #
        # Remove all unnecessary files
        #

        # Remove all tmp files.
        for tmp_file in cyrl_files_from_latn_dir + cyrl_files_from_cyrl_dir + latn_files_from_latn_dir + latn_files_from_cyrl_dir:
            os.remove(tmp_file)

        # If latn directory is empty, remove it.
        num_lines = 0
        for fpath in out_files_latn_dir:
            num_lines += count_lines(fpath)
        if num_lines == 0:
            shutil.rmtree(lang_direction_latn_path)

        # If cyrl directory is empty, remove it.
        num_lines = 0
        for fpath in out_files_cyrl_dir:
            num_lines += count_lines(fpath)
        if num_lines == 0:
            shutil.rmtree(lang_direction_cyrl_path)


def split_corpora_into_Cyrillic_and_Latin(args):
    src_lang = "eng"
    root_directory = args.root_directory
    trg_lang = args.trg_lang

    for root_dir, _, files in os.walk(root_directory):
        if len(files) == 0:
            continue

        assert len(files) == 2, f'Expected 2 files in the directory: {root_dir} but got {len(files)}'

        tmp_src = [f for f in files if src_lang in f]
        assert len(tmp_src) == 1, f'Expected 1 file with src_lang in the name but got {len(src_lang)}'

        tmp_trg = [f for f in files if trg_lang in f]
        assert len(tmp_trg) == 1, f'Expected 1 file with trg_lang in the name but got {len(tmp_trg)}'

        src_file = tmp_src[0]
        trg_file = tmp_trg[0]
        src_path = os.path.join(root_dir, src_file)
        target_path = os.path.join(root_dir, trg_file)
        corpus_name = trg_file.split('.')[0]
        print(f'Processing: {target_path}')

        latn_lines_and_indices = []
        cyrl_lines_and_indices = []

        # Split into Cyrillic and Latin
        with open(target_path, "r") as trg_f, open(src_path, "r") as src_f:
            src_lines = src_f.readlines()
            trg_lines = trg_f.readlines()

            for (src_line, trg_line) in tqdm(zip(src_lines, trg_lines), total=len(src_lines)):
                processed_line = process_line(trg_line)
                cyrl_cnt = sum(list(map(lambda c: c in SR_CYR_TO_LAT_DICT.keys(), processed_line)))
                if cyrl_cnt > len(processed_line) - cyrl_cnt:
                    cyrl_lines_and_indices.append((src_line, trg_line))
                else:
                    latn_lines_and_indices.append((src_line, trg_line))

        trg_data_path_latn = os.path.join(root_dir, f"tmp_{corpus_name}.{trg_lang}_Latn")
        src_data_path_latn_paired = os.path.join(root_dir, f"tmp_{corpus_name}.{src_lang}_Latn")
        trg_data_path_cyrl = os.path.join(root_dir, f"tmp_{corpus_name}.{trg_lang}_Cyrl")
        # kinda hacky: eng_Cyrl (such a thing doesn't exist) but just for being able to discriminate that it's paired with Cyrillic text
        src_data_path_cyrl_paired = os.path.join(root_dir, f"tmp_{corpus_name}.{src_lang}_Cyrl")

        for (trg_fpath, src_fpath, lines_and_indices) in [
            (trg_data_path_latn, src_data_path_latn_paired, latn_lines_and_indices),
            (trg_data_path_cyrl, src_data_path_cyrl_paired, cyrl_lines_and_indices)]:

            with open(trg_fpath, "w") as trg_f, open(src_fpath, "w") as src_f:
                for (src_line, trg_line) in tqdm(lines_and_indices):
                    src_f.write(f'{src_line}')
                    trg_f.write(f'{trg_line}')


#
# EXPERIMENTAL SECTION
#
def analyze_Cyrillic_Latin_mix():
    # Experimental function that I used to understand the nature of Cyrillic/Latin mix and unicode idiocyncracies.
    target_path = "/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/Opus_sr/GoURMET/eng_Latn-srp_Cyrl/GoURMET.srp_Cyrl"

    print(set(string.punctuation))

    with open(target_path, "r") as f:
        lines = f.readlines()
        num_lines = len(lines)
        mix_lines = []
        for i, line in enumerate(tqdm(lines)):
            line = process_line(line)
            cyrl_cnt = sum(list(map(lambda c: c in SR_CYR_TO_LAT_DICT.keys(), line)))

            if not (cyrl_cnt == 0 or cyrl_cnt == len(line)):
                print(f'{i}/{num_lines} The line is not fully cyrillic or latin: {line}')
                mix_lines.append((line, cyrl_cnt))


    print(f'Number of mix lines: {len(mix_lines)}/{len(lines)}')
    for (line, cyrl_cnt) in mix_lines:
        print(line)
        mostly_cyrl = cyrl_cnt > len(line) - cyrl_cnt
        for c in line:
            if mostly_cyrl:
                if c not in SR_CYR_TO_LAT_DICT.keys():
                    print(f'Found a non-Cyrillic char in the Cyrillic sentence: {c} utf-8: {c.encode("utf-8")}')
            else:
                if c in SR_CYR_TO_LAT_DICT.keys():
                    print(f'Found a Cyrillic char in the Latin sentence: {c} utf-8: {c.encode("utf-8")}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            "Script to separate the Serbian/Bosnian corpora into Cyrillic and Latin parts."
    )
    parser.add_argument(
        "--root_directory",
        "-d",
        type=str,
        default="/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/Opus_bs",
        required=False,
        help="directory to save downloaded data",
    )
    parser.add_argument(
        "--trg_lang",
        "-t",
        type=str,
        default="bos",
        choices=["bos", "srp"],
        help="target language in ISO 639-3 format",
    )
    args = parser.parse_args()
    trg_lang = args.trg_lang
    assert len(trg_lang) == 3, f"Expected trg_lang to be in ISO 639-3 format but got {trg_lang}"

    split_corpora_into_Cyrillic_and_Latin(args)
    place_Cyrillic_and_Latin_files(args.root_directory, "eng", trg_lang)