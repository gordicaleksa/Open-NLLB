import argparse
import os
import re
import shutil

from lang_code_mappings import UNSUPPORTED_LANG_CODES, AMBIGUOUS_ISO_639_3_CODES, ISO_639_1_TO_ISO_639_3, ISO_639_3_TO_BCP_47, SUPPORTED_BCP_47_CODES, retrieve_supported_files_and_iso_639_3_codes

BCP47_REGEX = re.compile(r'[a-z]{3}_[a-zA-Z]{4}')

# TODO(gordicaleksa): Should we add both directions for each language pair? I do that for "flat" datasets. I.e. datasets whose structure is "datasetname/lang_files" with no intermediate directory.

# Notes:
# I've modified ISO_639_3_TO_BCP_47 and added new language mappings from macro-language to specific language (making assumptions for the given datasets we currently have)
# Some datasets are ambiguous like e.g. "bianet" because it uses "kur" which stands for Kurdish which has 3 specific langs in it.
# NLLB supports central & northern Kurdish, and you can recognize the difference based on the script (Arab vs Latn).
# I manually mapped "kur" -> "kmr_Latn" (Northern Kurdish) - as I saw a Latn script.

def shoehorn_datasets_into_regular_structure(args):
    datasets_root = args.datasets_root
    non_train_datasets_path = args.non_train_datasets_path

    for dataset_name in os.listdir(datasets_root):
        dataset_path = os.path.join(datasets_root, dataset_name)
        dataset_content = os.listdir(dataset_path)

        if dataset_name == 'indic_nlp':
            print(f'Processing {dataset_name}. dataset.')
            nested_path = os.path.join(dataset_path, 'finalrepo')
            target_directory = os.path.join(non_train_datasets_path, dataset_name)
            os.makedirs(target_directory, exist_ok=True)
            try:
                os.rename(os.path.join(nested_path, 'README'), os.path.join(target_directory, 'README'))
            except:
                pass
            try:
                shutil.move(os.path.join(nested_path, 'dev'), target_directory)
            except:
                pass
            try:
                shutil.move(os.path.join(nested_path, 'test'), target_directory)
            except:
                pass
            train_path = os.path.join(nested_path, 'train')
            target_directory = os.path.join(target_directory, 'train')
            os.makedirs(target_directory, exist_ok=True)

            for el in os.listdir(train_path):
                if os.path.isdir(os.path.join(train_path, el)):
                    shutil.move(os.path.join(train_path, el), os.path.join(datasets_root, el))
                else:
                    shutil.move(os.path.join(train_path, el), os.path.join(target_directory, el))

            shutil.rmtree(dataset_path)

        if dataset_name == 'NLLB-Seed':
            nllb_seed_processing_flag = False
            for dirname in dataset_content:
                nllb_dataset_path = os.path.join(datasets_root, dataset_name, dirname)
                files = os.listdir(nllb_dataset_path)
                # Rename files to have the BCP 47 language code as the extension.
                for file in files:
                    if '.' in file:  # To prevent adding multiple suffixes...
                        continue
                    if not nllb_seed_processing_flag:
                        print(f'Processing {dataset_name}. dataset.')
                    nllb_seed_processing_flag = True
                    new_filename = f'{file}.{file}'
                    os.rename(os.path.join(nllb_dataset_path, file), os.path.join(nllb_dataset_path, new_filename))

        has_dirs = all([os.path.isdir(os.path.join(dataset_path, content)) for content in dataset_content])

        if not has_dirs:
            dataset_content = [file_lang_dir[0] for file_lang_dir in retrieve_supported_files_and_iso_639_3_codes(dataset_content)]

            if len(dataset_content) == 0:
                print(f'Found no supported files in {dataset_name} dataset.')
                continue

            assert len(dataset_content) == 2, f'Expected 2 files, got {len(dataset_content)}'
            print(f'Processing {dataset_name}. dataset.')

            lang_code_1 = dataset_content[0].split('.')[-1]
            lang_code_2 = dataset_content[1].split('.')[-1]

            is_iso_639_1_1 = False
            is_iso_639_1_2 = False

            if len(lang_code_1) == 2:
                lang_code_1 = ISO_639_1_TO_ISO_639_3[lang_code_1]
                is_iso_639_1_1 = True

            if len(lang_code_2) == 2:
                lang_code_2 = ISO_639_1_TO_ISO_639_3[lang_code_2]
                is_iso_639_1_2 = True

            dirname1 = f'{lang_code_1}-{lang_code_2}'
            dirname2 = f'{lang_code_2}-{lang_code_1}'
            os.makedirs(os.path.join(dataset_path, dirname1), exist_ok=True)
            os.makedirs(os.path.join(dataset_path, dirname2), exist_ok=True)

            filename1 = dataset_content[0]
            filename2 = dataset_content[1]

            new_filename1 = f'{filename1[:filename1.rfind(".")]}.{lang_code_1}' if is_iso_639_1_1 else filename1
            new_filename2 = f'{filename2[:filename2.rfind(".")]}.{lang_code_2}' if is_iso_639_1_2 else filename2

            def copy_del(filename, new_filename):
                shutil.copyfile(os.path.join(dataset_path, filename), os.path.join(dataset_path, dirname1, new_filename))
                shutil.copyfile(os.path.join(dataset_path, filename), os.path.join(dataset_path, dirname2, new_filename))
                os.remove(os.path.join(dataset_path, filename))

            copy_del(filename1, new_filename1)
            copy_del(filename2, new_filename2)


def map_all_lang_codes_to_bcp47(args):
    datasets_root = args.datasets_root

    for dataset_name in os.listdir(datasets_root):
        print(f'Mapping {dataset_name} dataset to BCP 47.')
        dataset_path = os.path.join(datasets_root, dataset_name)
        for lang_direction in os.listdir(dataset_path):
            el_path = os.path.join(dataset_path, lang_direction)
            if not os.path.isdir(el_path):
                print(f'Skipping file {lang_direction} in {dataset_name} dataset.')
                continue
            src, trg = lang_direction.split('-')

            if len(src) == 2:
                src = ISO_639_1_TO_ISO_639_3[src]
            if len(trg) == 2:
                trg = ISO_639_1_TO_ISO_639_3[trg]

            if src in UNSUPPORTED_LANG_CODES or trg in UNSUPPORTED_LANG_CODES:
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
                assert BCP47_REGEX.match(src), f'{src} does not match the BCP 47 regex pattern.'
            else:
                if zho_ambiguity_flag and src == "zho":
                    src = ISO_639_3_TO_BCP_47.get(src)[0]
                elif knc_ambiguous_flag and src == "knc":
                    src = ISO_639_3_TO_BCP_47.get(src)[1]
                else:
                    src = ISO_639_3_TO_BCP_47.get(src)[0]
            if not trg in ISO_639_3_TO_BCP_47:
                assert BCP47_REGEX.match(trg), f'{trg} does not match the BCP 47 regex pattern.'
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
                if suffix in SUPPORTED_BCP_47_CODES:  # Already in BCP 47 format.
                    continue

                if len(suffix) == 2:
                    suffix = ISO_639_1_TO_ISO_639_3[suffix]

                if not suffix in ISO_639_3_TO_BCP_47:
                    assert BCP47_REGEX.match(suffix), f'{suffix} does not match the BCP 47 regex pattern.'
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Script to prepare the datasets even before running stopes library."
    )
    parser.add_argument(
        "--datasets_root",
        "-d",
        type=str,
        required=True,
        help="Root directory where download_parallel_corpora.py downloaded the data.",
    )
    args = parser.parse_args()
    non_train_datasets_path = os.path.join(args.datasets_root, os.pardir, 'non_train_datasets')
    args.non_train_datasets_path = non_train_datasets_path

    os.makedirs(args.datasets_root, exist_ok=True)
    os.makedirs(non_train_datasets_path, exist_ok=True)

    shoehorn_datasets_into_regular_structure(args)
    map_all_lang_codes_to_bcp47(args)