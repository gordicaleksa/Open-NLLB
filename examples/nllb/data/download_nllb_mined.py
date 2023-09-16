from datasets import load_dataset

# TODO(gordicaleksa): use this script to download the mined bitexts.
dataset = load_dataset("allenai/nllb", "eng_Latn-srp_Cyrl")

print(len(dataset["train"]))
print('ok')