#!/bin/bash

# Set the root directory of the toxicity lists dataset
ROOT_DIR=/home/aleksa/Projects/nllb/fairseq/NLLB-200_TWL

# Iterate through all the zip files in the root directory
for zip_file in $ROOT_DIR/*.zip; do
    # Get the BCP47 code from the zip file name
    BCP47_code=$(basename $zip_file .zip)
    # Unzip the file with the password
    unzip -P tL4nLLb $zip_file
    # Move the unzipped file to the root directory
    mv $BCP47_code.txt $ROOT_DIR
    rm $zip_file
done
