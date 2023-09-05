# Getting started with Open-NLLB 🚀

There are 5 different components to Open-NLLB system, and thus 5 different areas where you could potentially contribute! Each of these contributions is equally important to us! ⭐

They are:
1. [Data collection, sourcing, verification](#data-collection-sourcing-verification)
2. [Dataset formatting](#dataset-formatting)
3. [Filtering](#filtering)
4. [Data preparation](#data-preparation)
5. [Model training](#model-training)

For some of these you don't even need to setup the Python environment.

Let's break them down and see the steps necessary to get started with each one of them!

Note: also see the main project document [here](https://docs.google.com/document/d/1Wt6Ze8mDnh_Dd-u3ahVndj0weTg5Gxo1rZG5aqWxIY0/edit#heading=h.2e9s1rv1npn0).

## 1. Data collection, sourcing, verification

**Setup:** no special setup needed.

Soft requirement: [join our Discord server](https://discord.gg/peBrCpheKE) for easier communication.

There are 3 sub-tasks here, those being:

🪣 `Data collection`: if you wish to help with collecting a **brand new parallel corpus** we're happy to support you! Please flag them to us either by creating a [GitHub issue](https://github.com/gordicaleksa/Open-NLLB/issues/new/choose) or by flagging it in our [Discord server](https://discord.gg/peBrCpheKE) in the [open-nllb](https://discord.gg/59DZDWgR5a) channel. We currently don't have any such effort going on but we might kick off new ones in the future.

🔎 `Data sourcing`: if you find an interesting dataset for some of the languages [that we support](https://github.com/gordicaleksa/Open-NLLB/blob/nllb_replication/examples/nllb/modeling/scripts/flores200/langs.txt) (see [Flores200](https://github.com/facebookresearch/flores/blob/main/flores200/README.md) for the actual names of those languages) please flag them to us either by creating a [GitHub issue]() or by flagging it in our [Discord server](https://discord.gg/peBrCpheKE) in the [open-nllb](https://discord.gg/59DZDWgR5a) channel.

🚩 `Data verification`: you can manually read through some of the public and/or mined (automatically scraped and refined) data that we have collected and as a native speaker flag any potential issues you encounter!

We're keeping track of a list of our "language champions" [here](https://docs.google.com/document/d/1myp6qZImAdAKBQS0-V6DgcLb7wGMnSMvV92cLvDOJbw) - meaning people who are native speakers of various languages that we support and that we can reach out to if we have any doubts about the correctness of the data (either the content or the label, e.g. a Central Kurdish file might have been mislabeled as Northern Kurdish).

If you're willing to become the owner for your native language - please sign up! 🙏

Tasks:
* You can find the list of prepared language-specific data tasks in [that same language champions document](https://docs.google.com/document/d/1myp6qZImAdAKBQS0-V6DgcLb7wGMnSMvV92cLvDOJbw).
* If you want to take this one step further and directly go through the public/mined data that we have, please check out the next section [data formatting](#data-formatting).

⭐ People who contribute across any of these sub-areas will be clearly **credited** in our main README file!

## 2. Dataset formatting

**Setup:** you'll need a Python environment with a couple of Python packages specified in the requirements file [here](examples/nllb/data/requirements.txt). If you don't play with the stages 3, 4, 5 (see below) these are all of the Python packages you'll need.

Check out this [README](examples/nllb/data/README.md) for a quick start.

There is a couple of sub-tasks where you could help:
* `Primary bi-text` - You can help by adding new download functions to our [`download_parallel_corpora.py`](examples/nllb/data/download_parallel_corpora.py) file.

* `Mined bi-text` - Our main script for downloading the mined data is [`download_mined_bitext.py`](examples/nllb/data/download_mined_bitext.py). It's still super rudimentary and could use some polishing. We're just using HuggingFace interface at the moment.

* `Back-translation data` - WIP - we still didn't play with this at all so any contribution (even a beginner-friendly tutorial on how to get started) would be super appreciated!

## 3. Filtering

**Setup:** Install the [Open-NLLB-stopes](https://github.com/gordicaleksa/Open-NLLB-stopes) project. Just [follow these INSTALL instructions](INSTALL.md) to build the Python environment that you can also then re-use for Open-NLLB.

Check out [this README](https://github.com/gordicaleksa/Open-NLLB-stopes/tree/nllb_replication/stopes/pipelines/filtering) for more information on how to run the filtering stage.

TL;DR: the workflow is the following:
* Run the `download_parallel_corpora.py` script which downloads our primary bi-text and formats it.
* After you have this data run the filtering pipeline that uses various heuristics like line length based filtering and pairwise deduplication to filter out lower quality bi-text.
* With the filtered data ready you can then proceed to the next stage (data preparation).

## 4. Data preparation

Setup: Install the [Open-NLLB-stopes](https://github.com/gordicaleksa/Open-NLLB-stopes) project.
[Follow these INSTALL]() instructions to build the environment that you can also use for Open-NLLB-stopes.

Check out [this README](https://github.com/gordicaleksa/Open-NLLB-stopes/tree/nllb_replication/stopes/pipelines/prepare_data) for more information.

TL;DR: the workflow is the following:
* You run the `prepare_extra_configs.py` to create the `train_corpora.yaml` config file that contains the paths to the filtered data from the previous stage.
* Modify `prepare_data.yaml` config to setup the stage.
* The stage itself will first do some validation checks (make sure all bi-text source/target files have the same number of lines), next up it will concatenate all the data from all the corpora for a particular language direction (e.g. `eng_Latn-rus_Cyrl` meaning English with a Latin script to Russian with a Cyrillic script). After that
it will do additional deduplication across the language directions + shard the files into smaller pieces.
At the very end it will binarize those textual files (applying the SPM-200 tokenizer).

## 5. Model training

Setup: Setup: Install the [Open-NLLB](https://github.com/gordicaleksa/Open-NLLB) project.
[Follow these INSTALL]() instructions to build the environment that you can also use for Open-NLLB-stopes.

For local runs (non-slurm runs) you need to run the [`train.py`](fairseq_cli/train.py) use this [config]() as the starting point.

I got that config by running the `train_script.py` following this README and extracting the necessary settings,
then tracing the code path and ending at `train.py` which ultimately gets called (whether you run this locally or on a slurm cluster).

Also check out [this README](/home/aleksa/Projects/nllb/fairseq/fairseq_cli/README.md) for more information.



