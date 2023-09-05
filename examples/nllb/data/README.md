# No Language Left Behind : Data

### Steps to download, format, & analyze the data (TL;DR)

1. Make sure you have a Python (e.g. conda) environment with the packages from `requirements.txt`.
2. Run the `download_parallel_corpora.py` script (find the instructions below). It will download all primary data + NLLB Seed (but will not download the 3 datasets mentioned below which require logging in, etc.) and prepare them so that they satisfy a common directory/file structure (see the header of the `download_parallel_corpora.py` script for more info).
3. (Optional - advanced) If you wish to analyze the data for each of the languages in the primary dataset check out the `analyse_data.py` script.
4. (Optional - advanced) Check out some notes we compiled by manually analyzing the datasets available for download from our `download_parallel_corpora.py` script [here](examples/nllb/data/NOTES_ON_LANGS.md).

You can find more information down below.

### Primary Datasets

#### Public data

The script [`download_parallel_corpora.py`](download_parallel_corpora.py) is provided for convenience to automate download of many publicly available sources of MT data
which were used to train NLLB models. You should provide a parent directory into which to save the data. Usage is as follows:

```bash
python download_parallel_corpora.py --directory $DOWNLOAD_DIRECTORY
```

Note that there are a number of other adhoc datasets for which we are
not able to automate this process because they require an account or login
of some kind:

1. Chichewa News (https://zenodo.org/record/4315018#.YaTuk_HMJDY)
2. GELR (Ewe-Eng) (https://www.kaggle.com/yvicherita/ewe-language-corpus)
3. Lorelei (https://catalog.ldc.upenn.edu/LDC2021T02)

Important note on JW300 (described in https://aclanthology.org/P19-1310/):
at the time of final publication, the JW300 corpus was no longer publicly
available for MT training because of licensing isses with the Jehovah's
Witnesses organization, though it had already been used for the NLLB project.
We hope that it may soon be made available again.

#### NLLB-Seed Data

NLLB-Seed datasets are included along with above Public datasets to create our Primary dataset. NLLB-Seed data can be downloaded from [here](https://github.com/facebookresearch/flores/tree/main/nllb_seed).


### Mined Datasets

LASER3 encoders and mined bitext metadata are open sourced in [LASER](https://github.com/facebookresearch/LASER) repository. Global mining pipeline and monolingual data filtering pipelines are released and available in our [stopes](https://github.com/facebookresearch/stopes) repository.

### Backtranslated Datasets

A helper script to perform backtranslation can be found in [`examples/nllb/modeling/scripts/backtranslation/generate_backtranslations.sh`](../modeling/scripts/backtranslation/generate_backtranslations.sh). It will take a corpus that’s been binarized using `stopes` [`prepare_data` pipeline](https://github.com/facebookresearch/stopes/tree/main/stopes/pipelines/prepare_data) and backtranslate all its shards. Please check the [backtranslation README](../modeling/scripts/backtranslation/README.md) file for further guidance on how to run this helper script.

Data that has been backtranslated will then need to be extracted into a parallel corpus. The script [`examples/nllb/modeling/scripts/backtranslation/extract_fairseq_bt.py`](../modeling/scripts/backtranslation/extract_fairseq_bt.py) automates this task. Further information can be found in the README above.

Once backtranslated data has been extracted, it can be treated as any other bitext corpus. Please follow the instructions for data filtering and preparation below.


## Preparing the data

Data preparation is fully managed by the [`stopes`](https://github.com/facebookresearch/stopes) pipelines. Specifically:

1. Data filtering is performed using `stopes` [`filtering`](https://github.com/facebookresearch/stopes/tree/main/stopes/pipelines/filtering) pipeline. Please check the corresponding README file and example configuration for more details.
2. Once filtered, data can then be preprocessed/binarized with `stopes` [`prepare_data`](https://github.com/facebookresearch/stopes/tree/main/stopes/pipelines/prepare_data) pipeline.

Encoding the datasets are done using the new `SPM-200` model which was trained on 200+ languages used in the NLLB project. For more details see [link](../modeling/README.md).

| SPM-200 Artifacts | download links |
| - | - |
| Model | [link](https://tinyurl.com/flores200sacrebleuspm) |
| Dictionary| [link](https://tinyurl.com/nllb200dictionary) |
