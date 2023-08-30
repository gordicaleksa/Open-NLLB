#!/bin/bash

# Set the root directory of the toxicity lists dataset
# You can download it from here: https://github.com/facebookresearch/flores/blob/main/toxicity/README.md
ROOT_DIR=/home/aleksa/Projects/nllb/fairseq/NLLB-200_TWL

# Iterate through all the zip files in the root directory
for zip_file in $ROOT_DIR/*.zip; do
    # Get the file name without the extension
    file_prefix=$(basename $zip_file .zip)
    # Unzip the file with the password (you'll find it in the above README)
    unzip -P tL4nLLb $zip_file
    # Move the unzipped file to the root directory
    mv $file_prefix.txt $ROOT_DIR
    # Remove the original zip file
    rm $zip_file
done
