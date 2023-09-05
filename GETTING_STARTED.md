# Getting started with Open-NLLB

WORK-IN-PROGRESS

TODO(gordicaleksa): wrap this up, still broken don't rely on it yet.

There are 5 different components to Open-NLLB system, and thus 5 different areas where you could contribute! Each of these contributions is equally important to us!

They are:
1. Data collection / sourcing / verification
2. Dataset processing
3. Filtering
4. Data preparation
5. Model training

For some of these you don't even need to setup the environment for fairseq and stopes.

Let's break them down and see the steps necessary to get started with each one of them.

## 1. Data collection, sourcing, verification

Setup: no setup needed.
Soft requirement: [join our Discord server]() for easier communication.

What?

Data collection: if you wish to help with collecting a brand new parallel corpus we're happy to support you! Please flag them to us either by creating a [GitHub issue]() or by flagging it in our [Discord server]() in the [open-nllb]() channel.

Data sourcing: if you find an interesting dataset for some of the languages [that we support]() please flag them to us either by creating a [GitHub issue]() or by flagging it in our [Discord server]() in the [open-nllb]() channel.

Data verification: you can manually read through some of the public/mined data that we have and as a native speaker flag any potential issues you encounter.

We're keeping track of a list of our ["language champions" here] - meaning people who are natives across various languages that we support and that we can reach out to if we have any doubts about the correctness of the data (either content or the label).

## 2. Dataset processing

Setup: you'll need a Python environment with a couple of Python packages specified [here]().

Primary bi-text:

You can by adding new download functions to our [`download_parallel_corpora.py`](examples/nllb/data/download_parallel_corpora.py) file.

Mined bi-text:

Our main script for downloading the mined data is [`download_mined_bitext.py`](examples/nllb/data/download_mined_bitext.py). It's still super rudimentary and could use some polishing.

Back translation data:

WIP - we still didn't play with this.

## 3. Filtering

Setup: Install the [Open-NLLB-stopes](https://github.com/gordicaleksa/Open-NLLB-stopes) project.
[Follow these INSTALL]() instructions to build the environment that you can also use for Open-NLLB-stopes.

Check out [this README](https://github.com/gordicaleksa/Open-NLLB-stopes/tree/nllb_replication/stopes/pipelines/filtering) for more information.

TL;DR: the workflow is the following:
you run the `download_parallel_corpora.py` script it downloads the primary bi-text and then
you point the filtering pipeline to it, the pipeline then uses various heuristics like line length
filtering of the bi-text and deduplication to filter out higher quality bi-text.

You can then proceed to the next stage which is data preparation.

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



