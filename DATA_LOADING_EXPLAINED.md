# Explanation of the MT data loading pipeline in fairseq

Dataset construction process looks like following:

1. At the end of the data preparation stage in stopes we end up with sharded binarized language directions.

Example: let's take `eng_Latn-tur_Latn` language direction as an example.
The train dataset has 28 shards that are organized in the following structure:
```
/data_bin
    /shard000
        /train.eng_Latn-tur_Latn.eng_Latn.bin
        /train.eng_Latn-tur_Latn.eng_Latn.idx
        /train.eng_Latn-tur_Latn.tur_Latn.bin
        /train.eng_Latn-tur_Latn.tur_Latn.idx
    /shard001
        ...
    ...
    /shard027
```

`bin` files contain tokenized sentences (we used `SPM-200` tokenizer) per line.
All of them are suffixed with an EOS token `</s>` that has index = 2 in SPM-200's dictionary.

`idx` files contain number of tokens per sentence from the `bin` file (including the `</s>` token) per line, aka a single number per line.

The language code just before the `.bin`/`.idx`suffix tells us the processed language in that file.

2. Next up we load the data from the above `bin`/`idx` files into `mmap` or memory mapped dataset.
TL;DR: `mmap` helps us to deal with datasets whose size can't fit in system memory (RAM). It handles loading from the disk.

It's the lowest level of abstraction is and it deals with headers, pointers and bytes from `.bin` & `.idx`.

You can find its implementation in the `MMapIndexedDataset` class.

3. We then wrap the mmap dataset for both the source and the target language into `PrependTokenDataset`.
As the name suggests it prepends the lang tokens to all src & trg tokenized sentences (token here means a number not something like `_an`).

Language tokens look something like `__hin_Deva__` and have their own corresponding index in the SPM dictionary.

So at this point the source/target sentence might look something like: `260058 230 392 22050 2` (format: `lang token` - `data tokens` - `</s>`).

4. We then wrap the source/target `PrependTokenDataset` datasets into `LanguagePairDataset` abstraction.

5. We then wrap multiple of `LanguagePairDataset` (for every lang direction we are training on) into `SampledMultiDataset`.

This dataset additionally assigns a sampling ratio to each of its `LanguagePairDataset` subsets - based on the size of the subset.
For example if one subset has 75M sentences and the other one 25M the sampling coefficients  will be 0.75 and 0.25 respectively (unless we modify the temperature). That means  we'll be sampling 3x more data from the bigger subset (proportionally).

But if we change the temperature from 1 to something above/below it - it also computes the "virtual size" of the dataset now that we’ve potentially upsampled (or downsampled) some of the lang-direction subsets.

It finally pre-computes all of the indices for this particular epoch for the virtual dataset and randomely permutes them based on some deterministic way of configuring the random seed.

6. Next we wrap `SampledMultiDataset` into `EpochBatchIterator`.

# WIP - will wrap it up tomorrow :)

Add the end of the construction process we call frozen_batch we additionally **sort indices by target & source sample sizes** and then we **filter out the ones that are too long** (> `512`).

Note: `batch_sampler = dataset.batch_by_size(` (line 354, construct_batch_sampler func in TranslationMultiSimpleEpochTask didn’t make complete sense how the final indices were batched doesn’t seem to be monotonic in size

Later `next_epoch_itr` calls a shuffle on the `frozen_batches` from `EpochBatchIterator` + does the sharding across GPUs (by wrapping the shuffled batch into `ShardedIterator`) 

Finally it passes the sharded batches into `PyTorch’s dataloader`

That’s then wrapped into a `CountingIterator`

And finally that’s wrapped up in a progress bar (e.g. wandb + json)

Task: `TranslationMultiSimpleEpochTask`