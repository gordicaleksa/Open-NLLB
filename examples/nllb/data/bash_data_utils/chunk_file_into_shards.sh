#!/bin/bash

# We used this script to chunk big language files into shards so that we can subsequently manually
# go through the data in e.g. vscode (otherwise loading would fail)


input_file1="${1}"
input_file2="${2}"
output_dir="${3}"

echo "Input file 1: ${input_file1}"
echo "Input file 2: ${input_file2}"
echo "Output directory: ${output_dir}"
# Create the output directory if it doesn't exist
mkdir -p "${output_dir}"
# Set the desired number of lines per chunk (you can adjust this)
lines_per_chunk=10000000

# Export the variables, including lines_per_chunk, so they are available to the functions
export input_file1 input_file2 output_dir lines_per_chunk
# Function to process a chunk of lines
process_chunk() {
  chunk_start="$1"
  chunk_end="$2"
  chunk_number="$3"

  chunk_file1="${output_dir}/${input_file1}_${chunk_number}.txt"
  chunk_file2="${output_dir}/${input_file2}_${chunk_number}.txt"

  # create the chunk file
  touch "${chunk_file1}" "${chunk_file2}"
  sed -n "${chunk_start},${chunk_end}p" "${input_file1}" > "${chunk_file1}"
  sed -n "${chunk_start},${chunk_end}p" "${input_file2}" > "${chunk_file2}"
}

# Calculate the number of lines in the input files
total_lines=$(wc -l < "${input_file1}")

# Calculate the number of chunks needed
num_chunks=$(( (total_lines + lines_per_chunk - 1) / lines_per_chunk ))

echo "Total lines: ${total_lines}"
echo "Lines per chunk: ${lines_per_chunk}"

export -f process_chunk

# Use xargs and parallel to process the chunks in parallel with tqdm
seq 1 $num_chunks | xargs -I{} -P 32 -n 1 bash -c 'process_chunk "$((( {} - 1 ) * lines_per_chunk + 1))" "$(( {} * lines_per_chunk ))" {} "${output_dir}"' | \
  tqdm --unit "chunks" --total "$num_chunks" --bar-format="{l_bar}{bar}| {n}/{total} Chunks [{elapsed}, ETA: {remaining}]"

echo "Chunks created in $output_dir."