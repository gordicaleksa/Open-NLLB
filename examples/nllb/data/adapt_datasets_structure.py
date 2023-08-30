import os
import re
import shutil

from iso_code_mappings import FILTERED_LANG_CODES, AMBIGUOUS_ISO_639_3_CODES, ISO_CODE_MAPPER_1_TO_3, ISO_639_3_TO_BCP_47, retrieve_supported_files_and_directions

datasets_root = '/home/aleksa/Projects/nllb/fairseq/examples/nllb/data/datasets'
non_train_datasets_path = os.path.join(datasets_root, os.pardir, 'non_train_datasets')

# TODO(gordicaleksa): instead of 3 letter codes (ISO 639-3) let's use the format xxx_<script> a la Flores dataset, so-called BCP 47 code.
# this is important so that we have uniform naming scheme throughout the datasets.
# TODO(gordicaleksa): potentially add both directions for each language pair.
# TODO(gordicaleksa): for minangnlp remove script (Latn) from lang direction name to make it consistent with the rest of the datasets.
# NLLB-Seed, minangnlp

bcp47_regex_pattern = re.compile(r'[a-z]{3}_[a-zA-Z]{4}')

# Notes:
# Manually renamed tir_ET to tir_Ethi in tico dataset.
# I've also modified ISO_639_3_TO_BCP_47 and added new language mappings from macro-language to specific language (making assumptions for the given datasets we currently have)
# NLLB-Seed/eng_Latn-kas_Deva/kas_Deva.kas_Deva <- had to manually rename teh suffix to kas_Deva, not sure what failed?
# NLLB-Seed/bjn_Latn-eng_Latn/bjn_Latn.bjn_Latn <- ditto
# NLLB-Seed/eng_Latn-knc_Latn/knc_Latn.knc_Latn <- ditto
# /nllb/data/datasets/NLLB-Seed/eng_Latn-taq_Tfng/taq_Tfng.taq_Tfng <- ditto
# nllb/data/datasets/NLLB-Seed/ace_Latn-eng_Latn/ace_Latn.ace_Latn <- ditto
# nllb/data/datasets/mtenglish2odia/eng_Latn-ory_Orya/train.ory_Orya <- ditto

# Some datasets are ambiguous like e.g. "bianet" because it uses "kur" which stands for Kurdish which has 3 specific langs in it.
# NLLB supports central & northern Kurdish, and you can recognize the difference based on the script (Arab vs Latn).
# I manually mapped "kur" -> "kmr_Latn" for Northern Kurdish (if I see Latn script).

# I also manually had to map "ori" to "ory_Orya" because "ori" is a macro-language (consists out of 2 langs)
# NLLB only support Odia (ory) which is written in Odia script (Orya).
# TODO: someone to confirm that mtenglish2odia dataset indeed has Odia and not the other language.
def map_to_bcp47():
    for dataset_name in os.listdir(datasets_root):
        print(f'Processing {dataset_name}. dataset.')
        dataset_path = os.path.join(datasets_root, dataset_name)
        for lang_direction in os.listdir(dataset_path):
            el_path = os.path.join(dataset_path, lang_direction)
            if not os.path.isdir(el_path):
                print(f'Skipping file {lang_direction} in {dataset_name} dataset.')
                continue
            src, trg = lang_direction.split('-')
            if len(src) == 2:
                src = ISO_CODE_MAPPER_1_TO_3[src]
            if len(trg) == 2:
                trg = ISO_CODE_MAPPER_1_TO_3[trg]

            if src in FILTERED_LANG_CODES or trg in FILTERED_LANG_CODES:
                print(f'Found unsupported lang code ({src} or {trg}) in {dataset_name} dataset.')
                target_path = os.path.join(non_train_datasets_path, dataset_name)
                os.makedirs(target_path, exist_ok=True)
                shutil.move(os.path.join(dataset_path, lang_direction), target_path)
                continue

            zho_ambiguity_flag = False
            knc_ambiguous_flag = False
            if src in AMBIGUOUS_ISO_639_3_CODES or trg in AMBIGUOUS_ISO_639_3_CODES:
                if (src == "zho" or trg == "zho") and dataset_name == "tico":
                    zho_ambiguity_flag = True
                elif (src == "knc" or trg == "knc") and dataset_name == "tico":
                    knc_ambiguous_flag = True
                else:
                    raise Exception(f'Found ambiguous ISO 639-3 code in {dataset_name} dataset: {src} or {trg}')

            if not src in ISO_639_3_TO_BCP_47:
                assert bcp47_regex_pattern.match(src), f'{src} does not match the BCP 47 regex pattern.'
            else:
                if zho_ambiguity_flag and src == "zho":
                    src = ISO_639_3_TO_BCP_47.get(src)[0]
                elif knc_ambiguous_flag and src == "knc":
                    src = ISO_639_3_TO_BCP_47.get(src)[1]
                else:
                    src = ISO_639_3_TO_BCP_47.get(src)[0]
            if not trg in ISO_639_3_TO_BCP_47:
                assert bcp47_regex_pattern.match(trg), f'{trg} does not match the BCP 47 regex pattern.'
            else:
                if zho_ambiguity_flag and trg == "zho":
                    trg = ISO_639_3_TO_BCP_47.get(trg)[0]
                elif knc_ambiguous_flag and trg == "knc":
                    trg = ISO_639_3_TO_BCP_47.get(trg)[1]
                else:
                    trg = ISO_639_3_TO_BCP_47.get(trg)[0]

            new_lang_direction_name = f'{src}-{trg}'
            os.rename(os.path.join(dataset_path, lang_direction), os.path.join(dataset_path, new_lang_direction_name))
            for file in os.listdir(os.path.join(dataset_path, new_lang_direction_name)):
                suffix = file.split('.')[-1]
                if len(suffix) == 2:
                    suffix = ISO_CODE_MAPPER_1_TO_3[suffix]

                if not suffix in ISO_639_3_TO_BCP_47:
                    assert bcp47_regex_pattern.match(suffix), f'{suffix} does not match the BCP 47 regex pattern.'
                else:
                    if zho_ambiguity_flag and suffix == "zho":
                        suffix = ISO_639_3_TO_BCP_47.get(suffix)[0]
                    elif knc_ambiguous_flag and suffix == "knc":
                        suffix = ISO_639_3_TO_BCP_47.get(suffix)[1]
                    else:
                        suffix = ISO_639_3_TO_BCP_47.get(suffix)[0]

                prefix = file[:file.rfind('.')]
                os.rename(
                    os.path.join(dataset_path, new_lang_direction_name, file),
                    os.path.join(dataset_path, new_lang_direction_name, f'{prefix}.{suffix}'))


def fix_datasets_structure():
    for dataset_name in os.listdir(datasets_root):
        print(f'Processing {dataset_name}. dataset.')
        dataset_path = os.path.join(datasets_root, dataset_name)
        dataset_content = os.listdir(dataset_path)

        if dataset_name == 'indic_nlp':
            nested_path = os.path.join(dataset_path, 'finalrepo')
            non_train_datasets_path = os.path.join(datasets_root, os.pardir, 'non_train_datasets')
            os.makedirs(non_train_datasets_path, exist_ok=True)
            try:
                os.rename(os.path.join(nested_path, 'README'), os.path.join(non_train_datasets_path, 'README'))
            except:
                pass
            try:
                shutil.move(os.path.join(nested_path, 'dev'), non_train_datasets_path)
            except:
                pass
            try:
                shutil.move(os.path.join(nested_path, 'test'), non_train_datasets_path)
            except:
                pass
            train_path = os.path.join(nested_path, 'train')
            indic_datasets_dirnames = [el for el in os.listdir(train_path) if os.path.isdir(os.path.join(train_path, el))]
            for el in os.listdir(train_path):
                if os.path.isdir(os.path.join(train_path, el)):
                    shutil.move(os.path.join(train_path, el), os.path.join(datasets_root, el))
                else:
                    shutil.move(os.path.join(train_path, el), os.path.join(non_train_datasets_path, el))
            shutil.rmtree(dataset_path)
            for indic_dataset_dirname in indic_datasets_dirnames:
                indic_dataset_path = os.path.join(datasets_root, indic_dataset_dirname)
                for el in os.listdir(indic_dataset_path):
                    src, trg = el.split('-')
                    src = ISO_CODE_MAPPER_1_TO_3[src]
                    trg = ISO_CODE_MAPPER_1_TO_3[trg]
                    new_dirname = f'{src}-{trg}'
                    indic_dataset_lang_direction = os.path.join(indic_dataset_path, new_dirname)
                    os.rename(os.path.join(indic_dataset_path, el), indic_dataset_lang_direction)
                    for file in os.listdir(indic_dataset_lang_direction):
                        suffix = ISO_CODE_MAPPER_1_TO_3[file.split('.')[-1]]
                        prefix = file[:file.rfind('.')]
                        os.rename(
                            os.path.join(indic_dataset_lang_direction, file),
                            os.path.join(indic_dataset_lang_direction, f'{prefix}.{suffix}'))

        if dataset_name == 'NLLB-Seed':
            tmp_dict = set()
            # TODO(gordicaleksa): potentially remove the script name from the directory name
            for dirname in dataset_content:
                src, trg = dirname.split('-')
                tmp_dict.add(src)
                tmp_dict.add(trg)
                nllb_dataset_path = os.path.join(datasets_root, dataset_name, dirname)
                files = os.listdir(nllb_dataset_path)
                # Rename files to have the language code as the extension.
                for file in files:
                    if '.' in file:  # To prevent adding multiple suffixes...
                        continue
                    lang_code = file.split('_')[0]
                    new_filename = f'{file}.{lang_code}'
                    os.rename(os.path.join(nllb_dataset_path, file), os.path.join(nllb_dataset_path, new_filename))
            print(tmp_dict)

        has_dirs = all([os.path.isdir(os.path.join(dataset_path, content)) for content in dataset_content])
        for content in dataset_content:
            print(content, os.path.isdir(os.path.join(dataset_path, content)))

        if has_dirs:
            pass
        else:
            dataset_content = [file_lang_dir[0] for file_lang_dir in retrieve_supported_files_and_directions(dataset_content)]
            if len(dataset_content) == 0:
                continue
            assert len(dataset_content) == 2, f'Expected 2 files, got {len(dataset_content)}'
            lang1 = dataset_content[0].split('.')[-1]
            lang2 = dataset_content[1].split('.')[-1]

            is_iso_639_1_1 = False
            is_iso_639_1_2 = False

            if len(lang1) == 2:
                lang1 = ISO_CODE_MAPPER_1_TO_3[lang1]
                is_iso_639_1_1 = True

            if len(lang2) == 2:
                lang2 = ISO_CODE_MAPPER_1_TO_3[lang2]
                is_iso_639_1_2 = True

            dirname1 = f'{lang1}-{lang2}'
            dirname2 = f'{lang2}-{lang1}'
            os.makedirs(os.path.join(dataset_path, dirname1), exist_ok=True)
            os.makedirs(os.path.join(dataset_path, dirname2), exist_ok=True)

            filename1 = dataset_content[0]
            filename2 = dataset_content[1]

            new_filename1 = f'{filename1[:filename1.rfind(".")]}.{lang1}' if is_iso_639_1_1 else filename1
            new_filename2 = f'{filename2[:filename2.rfind(".")]}.{lang2}' if is_iso_639_1_2 else filename2

            def copy_del(filename, new_filename):
                shutil.copyfile(os.path.join(dataset_path, filename), os.path.join(dataset_path, dirname1, new_filename))
                shutil.copyfile(os.path.join(dataset_path, filename), os.path.join(dataset_path, dirname2, new_filename))
                os.remove(os.path.join(dataset_path, filename))

            copy_del(filename1, new_filename1)
            copy_del(filename2, new_filename2)


if __name__ == '__main__':
    # fix_datasets_structure()
    map_to_bcp47()