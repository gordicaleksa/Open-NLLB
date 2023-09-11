# Explanation of the MT data pipeline in Open-NLLB

Dataset construction process looks like following, there are 10 steps in total (note: the number of steps is semi-arbitrarily chosen so that we end up with approximately self-contained logical units):

## Step 1
At the end of the data preparation stage (which happens in [Open-NLLB-stopes](https://github.com/gordicaleksa/Open-NLLB-stopes)) we end up with sharded, binarized language directions.

Example: let's take `eng_Latn-tur_Latn` language direction as an example (meaning English to Turkish direction, both have Latin script).
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

Both `bin` and `idx` files are binary files that have a proprietary format (`mmap` format).

`bin` files contain tokenized sentences (we used the `SPM-200` tokenizer) per line (in a raw/binary format). All of them are suffixed with an EOS token (`</s>`) that has index = 2 in SPM-200's dictionary.

`idx` files contain number of tokens per sentence from the `bin` file (including the `</s>` token) per line, aka a single number per line.

The language code just before the `.bin`/`.idx` suffix tells us about the processed language in that particular file (i.e. are these English or Turkish sentences).

## Step 2
Next up we load the data from the above `bin`/`idx` files into `mmap` or memory mapped dataset.

TL;DR: `mmap` helps us to deal with datasets whose size can't fit in system memory (RAM). It automagically handles loading from the disk so that you don't have to think about RAM utilization yourself.

It's the lowest level of abstraction and it deals with headers, pointers and bytes from `.bin` & `.idx` files.

You can find its implementation in the `MMapIndexedDataset` class.

## Step 3
We then wrap the `mmap` dataset for both the source and the target language into `PrependTokenDataset`.

As the name suggests it prepends the lang tokens to all src & trg tokenized sentences (token here means a number/index in the SPM dictionary not something like `_an`).

Language tokens look something like `__hin_Deva__` and have their own corresponding index in the SPM dictionary.

So at this point the source/target sentence might look something like: `260058 230 392 22050 2` (format = (`lang token` = 260058, `data tokens` = 230 392 22050, `</s>` = 2).

## Step 4
We then wrap the source/target `PrependTokenDataset` datasets into `LanguagePairDataset` abstraction.

## Step 5
We then wrap multiple `LanguagePairDataset`s (for every lang direction we are training on) into `SampledMultiDataset`.

This dataset additionally assigns a sampling ratio to each of its `LanguagePairDataset` subsets - based on the size of the subset.
For example if one subset has 75M sentences and the other one 25M the sampling coefficients  will be 0.75 and 0.25 respectively (unless we modify the temperature). That means  we'll be sampling 3x more data from the bigger subset (proportionally).

But if we change the temperature from 1 to something above/below it - it also computes the "virtual size" of the dataset now that we’ve potentially upsampled (or downsampled) some of the lang-direction subsets.

*Note on virtual size: as an example if we have 2 lang directions one with 1M and one with 0.5M sentences and temperature > 1 then the virtual size is basically 1M + 0.5M*c, where c is a coefficient larger than 1. Thus we end up with a virtual size that's bigger than 1.5M sentences (we will effectively duplicate certain sentences from that smaller subset).*

It finally pre-computes all of the indices for this particular epoch for the virtual dataset and creates a random permutation of those indices.

## Step 6
Next we wrap `SampledMultiDataset` into `EpochBatchIterator`.

At the end of the `get_train_iterator` function (which both loads `SampledMultiDataset` dataset and instantiates the `EpochBatchIterator`) we call `self.reset_dummy_batch(batch_iterator.first_batch)` which in return triggers `first_batch` function to be called which in return calls `frozen_batches` (`len` operator acting as the trigger) and finally that function subsequently calls the batch sampler which does the following 2 operations:

a) sorts the virtual dataset indices by target & source sample sizes in that particular order.

b) filters out the samples that are too long (> `512`) (either source/target).

Note: `batch_sampler = dataset.batch_by_size` (line 354, `construct_batch_sampler` func in `TranslationMultiSimpleEpochTas`) didn’t make complete sense how the final indices were batched doesn’t seem to be monotonic in size. If someone wants to do an analysis around this and write a short report that would be a valuable contribution.

## Step 6.1 - note on collation
`first_batch` function (mentioned above called as a part of `self.reset_dummy_batch`) triggers the collation procedure for the dummy batch - which is effectively the first time that our code calls into the data pipeline.

The process looks like the following:
* We iterate through the indices of the first batch (as determined by the output of `dataset.batch_by_size` function all).
* For each of those indices we index into `SampledMultiDataset` which internally delegates that index to the right `LanguagePairDataset` which then further delegates that call to the underlying source/target `mmap` datasets. From there we fetch the "raw" tokens which are then prepended with the language token (in `PrependTokenDataset`) and finally `SampledMultiDataset` propagates that information upward in a form of a dictionary with 3 keys: `id`, `source`, `target`.
* Next up `SampledMultiDataset`'s collate function is triggered and internally it delegates this call further to `LanguagePairDataset`'s collate function.
* The collate function extracts the `source` (`target`) tensors from each of those sample dictionaries. Finds the max sequence length and creates a tensor of dimension `num_samples` x `max_{src/trg}_len` initialized with `pad` tokens.
* That resulting tensor is then populated with source/target tokens applying left/right padding respectively.
* Finally we create another tensor (`prev_output_tokens`) that is the exact copy of the target tensor with the ony difference that the `</s>` "EOS" token is swapped so that it's now the first token in those sequences (effectively they are using "EOS" token as a BOS token as well - i.e. start/beginning of sequence token). This is the tensor that we feed into the decoder and we compare its outputs against the `target` tensor.
* The collate function finally returns a dictionary:
```
    batch = {
        "id": id,
        "nsentences": len(samples),
        "ntokens": ntokens,
        "net_input": {
            "src_tokens": src_tokens,
            "src_lengths": src_lengths,
            "prev_output_tokens": prev_output_tokens,
        },
        "target": target,
    }
```

And this is exactly what you end up seeing if you take a look at our data loading loops for either training or validation. Now you understand exactly how the whole process works in the background (almost - see the next couple of steps! :)).

## Step 7
Once we have retrieved `EpochBatchIterator` from step 6, we call the `next_epoch_itr` function on it and it does the following steps:
* It shuffles the `frozen_batches`'s (mentioned before as being a property of `EpochBatchIterator`) rows. Frozen batches (which is a list of lists of indices) is arranged in such a way that its first rows contain indices of the shortest samples in our dataset. Thus those first indices lead to a construction of batches that have a large amount of short sentences. As we progress through its rows the batches end up having less and less sentences and are longer in length. Basically going from left to right and top to bottom across its indices we get progressively longer sentence pairs.
* Shards the indices across different GPUs on our system (by wrapping the shuffled batch into `ShardedIterator`). If you have `n` GPUs on your system, the first GPU will take out 0th, (n-1)-first, 2*(n-1)-st ... rows from the shuffled batch.

Note from @gordicaleksa: I think it might be better to first shard and then shuffle because doing it like this, in the worst case scenario, we might end up having a much larger work load on one of the GPUs. Because for example all of the "wide" batches end up on that GPU (i.e. small batch size long sentences).

## Step 8
The sharded shuffled batches are then passed into `PyTorch’s dataloader` together with `SampledMultiDataset` and its collator function.

## Step 9
All of the above is then wrapped into a `CountingIterator` which just does what the name suggests: keeps track of the number of consumed batches during the training (or validation - similar pipeline there).

## Step 10
Finally `CountingIterator` object is wrapped into in a progress bar (e.g. `WandBProgressBarWrapper` + `JsonProgressBar`). Those just
do some additional logging (to the console and/or Weights & Biases dashboard) and then delegate the call to the `CountingIterator`.

Note: Only the main/master GPU (the one that has a global rank == 0) process will log to Weights & Biases.
The other GPU processes won't have that additional wandb progress bar wrapper instead they'll only have e.g. JSON bar wrapper.

---

Some additional context: all of this is a part of the `TranslationMultiSimpleEpochTask`.