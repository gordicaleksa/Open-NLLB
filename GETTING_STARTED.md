# Getting started with Open-NLLB 🚀

There are 5 different components to Open-NLLB system, and thus 5 different areas where you could potentially contribute! Each of these contributions is equally important to us! ⭐

They are:
1. [Data collection, sourcing, verification](#1-data-collection-sourcing-verification)
2. [Dataset formatting](#2-dataset-formatting)
3. [Filtering](#3-filtering)
4. [Data preparation](#4-data-preparation)
5. [Model training](#5-model-training)

For some of these you don't even need to setup the Python environment.

Let's break them down and see the steps necessary to get started with each one of them!

Note: also see the main project document [here](https://docs.google.com/document/d/1Wt6Ze8mDnh_Dd-u3ahVndj0weTg5Gxo1rZG5aqWxIY0/edit#heading=h.2e9s1rv1npn0).

## 1. Data collection, sourcing, verification

**Setup:** no special setup needed.

Soft requirement: [join our Discord server](https://discord.gg/peBrCpheKE) for easier communication.

There are 3 sub-tasks here, those being:

🪣 `Data collection`: if you wish to help with collecting a **brand new parallel corpus** we're happy to support you! Please flag them to us either by creating a [GitHub issue](https://github.com/gordicaleksa/Open-NLLB/issues/new/choose) or by flagging it in our [Discord server](https://discord.gg/peBrCpheKE) in the [open-nllb](https://discord.gg/59DZDWgR5a) channel. We currently don't have any such effort going on but we might kick off new ones in the future.

🔎 `Data sourcing`: if you find an interesting dataset for some of the languages [that we support](https://github.com/gordicaleksa/Open-NLLB/blob/nllb_replication/examples/nllb/modeling/scripts/flores200/langs.txt) (see [Flores200](https://github.com/facebookresearch/flores/blob/main/flores200/README.md) for the actual names of those languages) please flag them to us either by creating a [GitHub issue](https://github.com/gordicaleksa/Open-NLLB/issues/new/choose) or by flagging it in our [Discord server](https://discord.gg/peBrCpheKE) in the [open-nllb](https://discord.gg/59DZDWgR5a) channel.

🚩 `Data verification`: you can manually read through some of the public and/or mined (automatically scraped and refined) data that we have collected and as a native speaker flag any potential issues you encounter!

We're keeping track of a list of our "language champions" [here](https://docs.google.com/document/d/1myp6qZImAdAKBQS0-V6DgcLb7wGMnSMvV92cLvDOJbw) - meaning people who are native speakers of various languages that we support and that we can reach out to if we have any doubts about the correctness of the data (either the content or the label, e.g. a Central Kurdish file might have been mislabeled as Northern Kurdish).

If you're willing to become the owner for your native language - please sign up! 🙏

Tasks:
* You can find the list of prepared language-specific data tasks in [that same language champions document](https://docs.google.com/document/d/1myp6qZImAdAKBQS0-V6DgcLb7wGMnSMvV92cLvDOJbw).
* If you want to take this one step further and directly go through the public/mined data that we have, please check out the next section [data formatting](#2-data-formatting).

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

TL;DR: the high-level workflow is the following:
* Run the `download_parallel_corpora.py` script which downloads our primary bi-text and formats it.
* Run 3 different Python scripts (see the README above for more details) to create all of the necessary filtering config files.
* After you have this data and configs run the filtering pipeline that uses various heuristics like line length based filtering and pairwise deduplication to filter out lower quality bi-text.
* With the filtered data ready you can then proceed to the next stage (data preparation).

## 4. Data preparation

**Setup:** Install the [Open-NLLB-stopes](https://github.com/gordicaleksa/Open-NLLB-stopes) project. Just [follow these INSTALL instructions](INSTALL.md) to build the Python environment that you can also then re-use for Open-NLLB.

Check out [this README](https://github.com/gordicaleksa/Open-NLLB-stopes/tree/nllb_replication/stopes/pipelines/prepare_data) for more information on how to run the data preparation stage.

TL;DR: the high-level workflow is the following:
1. (Optional) Run the filtering stage - data preparation can also work directly on "raw" bi-text (i.e. w/o filtering)
2. Run the `prepare_extra_configs.py` to create data preparation config file.
3. Modify `prepare_data.yaml` config to setup the data preparation stage linking to the config from the previous step.
4. The data preparation stage will then do the following:
    - Validation checks - makes sure that all bi-text source/target files have the same number of lines.
    - Concatenates the data from all the datasets for a particular language direction (e.g. `eng_Latn-rus_Cyrl` might exist in datasets `A`, `B`, and `C` and so we concat all 3 of those files into a final one).
    - Deduplicates across all language directions and then shards the language direction files into smaller pieces.
    - Binarizes the shards using the pre-trained `SPM-200` tokenizer.

## 5. Model training

**Setup:** Install the [Open-NLLB](https://github.com/gordicaleksa/Open-NLLB) project. Just [follow these INSTALL instructions](INSTALL.md) to build the Python environment that you can also then re-use for Open-NLLB-stopes.

*Note: if you've already run the setup for any of the previous two stages you don't need to do this.*

To run the training you have 2 options:
1. (Better for local runs) For local runs (non-slurm runs) you can run the [`train.py`](fairseq_cli/train.py) directly just use the config provided below as the starting point / reference.

Context: I got that config by running the [`train_script.py`](examples/nllb/modeling/train/train_script.py) following [its README](examples/nllb/modeling/README.md) and then extracting the settings that that script passes on to `train.py` (I just traced out the code path that led to it).

2. (Better when running on slurm) Run [`train_script.py`](examples/nllb/modeling/train/train_script.py) and follow [its README](examples/nllb/modeling/README.md) to get started.

Also check out [this README](/home/aleksa/Projects/nllb/fairseq/fairseq_cli/README.md) for more information (on how to setup Weights & Biases, etc.).

The reference train config:
```
    "--distributed-world-size", "2", "/home/aleksa/Projects/nllb/stopes/stopes/pipelines/prepare_data/processed_data/data_bin/shard000:/home/aleksa/Projects/nllb/stopes/stopes/pipelines/prepare_data/processed_data/data_bin/shard001",
    "--save-dir", "/home/aleksa/Projects/nllb/fairseq/model_checkpoints/save_dir",
    // "--tensorboard-logdir", "/home/aleksa/Projects/nllb/fairseq/model_checkpoints/tb/tb_log",
    "--skip-invalid-size-inputs-valid-test", "--memory-efficient-fp16", "--max-update", "100000",
    "--update-freq", "1", "--task", "translation_multi_simple_epoch", "--lang-pairs", "eng_Latn-spa_Latn,eng_Latn-rus_Cyrl,tur_Latn-rus_Cyrl",
    "--use-local-shard-size", "--sampling-method", "temperature", "--sampling-temperature", "1",
    "--adam-eps", "1e-06", "--adam-betas", "(0.9, 0.98)", "--lr-scheduler", "inverse_sqrt",
    "--warmup-init-lr", "1e-07", "--warmup-updates", "500", "--lr", "5e-05", "--stop-min-lr", "1e-09",
    "--clip-norm", "0.0", "--dropout", "0", "--weight-decay", "0.0",
    "--criterion", "label_smoothed_cross_entropy", "--label-smoothing", "0.1",
    "--best-checkpoint-metric", "nll_loss", "--max-tokens", "2048", "--seed", "2", "--log-format", "json",
    "--log-interval", "100", "--validate-interval-updates", "500", // "--valid-subset", "valid",
    "--keep-interval-updates", "1", "--keep-last-epochs", "1", "--validate-interval", "1000",
    "--max-source-positions", "512", "--max-target-positions", "512", "--enable-m2m-validation",
    "--add-data-source-prefix-tags", "--share-all-embeddings", "--decoder-normalize-before",
    "--encoder-normalize-before", "--optimizer", "adam", "--fp16-adam-stats", "--min-params-to-wrap",
    "100000000", "--ddp-backend", "fully_sharded", "--replication-count", "1", "--encoder-langtok", "src",
    "--decoder-langtok", "--langs", "/home/aleksa/Projects/nllb/fairseq/examples/nllb/modeling/scripts/flores200/langs.txt",
    "--save-interval-updates", "1000", "--save-interval", "1000", "--arch", "transformer", "--encoder-layers", "12",
    "--decoder-layers", "12", "--encoder-ffn-embed-dim", "4096", "--decoder-ffn-embed-dim", "4096", "--encoder-embed-dim",
    "1024", "--decoder-embed-dim", "1024", "--encoder-attention-heads", "16", "--decoder-attention-heads", "16",
    "--attention-dropout", "0.1", "--relu-dropout", "0.0", "--train-subset", "train",
    "--wandb-project", "open-nllb", "--disable-validation"
```

Notes:
* Modify `--distributed-world-size` depending on the number of GPUs you have on your system (I have 2, set to 1 if only single GPU)
* I removed some of the sharded paths (I have 28 of them and so will you if you download all of the primary data) just to make it more readable
* Modify `"--lang-pairs"` depending on which directions you want to train for
* Modify `"--max-tokens", "2048"` depending on the amount of VRAM you have. This is the max number of tokens in a batch (NLLB paper used 1.000.000!)
* Remove `--disable-validation` and uncomment `"--valid-subset", "valid",` if you have validation data (e.g. Flores 200)
* Remove `"--fp16-adam-stats"` if you didn't install Apex otherwise your run will fail
* Uncomment `--tensorboard-logdir` and remove `--wandb-project` if you wish to use Tensorboard instead of Weights & Biases
* Needless to say adapt the paths for your local system and check out the README and the code for more information about what each of these arguments does.


