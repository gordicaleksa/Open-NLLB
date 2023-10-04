from collections import Counter
from dataclasses import dataclass
import logging
from pathlib import Path
import re
import subprocess
import shlex
import string
import typing as tp
from typing import Dict, List, Optional, Set
import unicodedata

import xxhash


def open_file_cmd(filename: tp.Union[Path, str]) -> str:
    if isinstance(filename, Path):
        filename = str(filename)
    filename = shlex.quote(filename)
    cat = "cat"
    if filename.endswith(".xz"):
        cat = "xzcat"
    if filename.endswith(".gz"):
        cat = "zcat"

    return shlex.join((cat, filename))

def bash_pipefail(*pipe_parts: str) -> str:
    """Run a bash pipelines with "-o pipefail".
    This allows to catch zcat failures.
    Note that it will also generate error if you use "head" in your pipeline.
    The arguments are supposed to be valid bash commands.
    """
    pipe = " | "
    return shlex.join(["/bin/bash", "-o", "pipefail", "-c", pipe.join(pipe_parts)])

def count_lines(filename: str) -> int:
    """
    Count the number of lines in a file.
    """
    result = subprocess.run(
        bash_pipefail(
            open_file_cmd(filename),
            shlex.join(["wc", "-l"]),
        ),
        capture_output=True,
        shell=True,
    )
    out = result.stdout.decode("utf-8")
    lines_numbers = [int(line) for line in out.split() if line]
    assert len(lines_numbers) == 1
    return lines_numbers[0]

#
# BELOW CODE IS COPY PASTED FROM THE FILTERING PIPELINE OF STOPES REPO.
#
UNICODE_PUNCT = {
    "，": ",",
    "。": ".",
    "、": ",",
    "„": '"',
    "”": '"',
    "“": '"',
    "«": '"',
    "»": '"',
    "１": '"',
    "」": '"',
    "「": '"',
    "《": '"',
    "》": '"',
    "´": "'",
    "∶": ":",
    "：": ":",
    "？": "?",
    "！": "!",
    "（": "(",
    "）": ")",
    "；": ";",
    "–": "-",
    "—": " - ",
    "．": ". ",
    "～": "~",
    "’": "'",
    "…": "...",
    "━": "-",
    "〈": "<",
    "〉": ">",
    "【": "[",
    "】": "]",
    "％": "%",
    "►": "-",
}

UNICODE_PUNCT_RE = re.compile(f"[{''.join(UNICODE_PUNCT.keys())}]")

NON_PRINTING_CHARS_RE = re.compile(
    f"[{''.join(map(chr, list(range(0,32)) + list(range(127,160))))}]"
)

DIGIT_RE = re.compile(r"\d")

PUNCT_OR_NON_PRINTING_CHARS_RE = re.compile(
    (UNICODE_PUNCT_RE.pattern + NON_PRINTING_CHARS_RE.pattern).replace("][", "")
)

def remove_non_printing_char(text: str) -> str:
    return NON_PRINTING_CHARS_RE.sub("", text)


def replace_unicode_punct(text: str) -> str:
    return "".join((UNICODE_PUNCT.get(c, c) for c in text))


def normalize_whitespace(s):
    # Replace sequences of whitespace characters with a single space
    s = re.sub(r'\s+', ' ', s)
    # Remove leading and trailing whitespace
    return s.strip()


def strip_accents(line: str) -> str:
    """Strips accents from a piece of text."""
    nfd = unicodedata.normalize("NFD", line)
    output = [c for c in nfd if unicodedata.category(c) != "Mn"]
    if len(output) == line:
        return line
    return "".join(output)


def normalize_for_lid(line: str) -> str:
    line = normalize_whitespace(line)
    line = line.lower()
    line = DIGIT_RE.sub("", line)  # remove digits
    line = remove_non_printing_char(line)
    line = replace_unicode_punct(line)
    line = line.translate(str.maketrans('', '', string.punctuation))  # Remove all punctuation.
    # line = strip_accents(line)
    line = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '', line)  # remove ip addresses
    line = re.sub(r'http\S+', '', line)  # remove urls
    line = normalize_whitespace(line)
    return line


def normalize_for_dedup(line: str) -> str:
    line = normalize_whitespace(line)
    if not line:
        return line
    line = line.lower()
    line = DIGIT_RE.sub("0", line)
    line = PUNCT_OR_NON_PRINTING_CHARS_RE.sub("", line)
    line = strip_accents(line)
    return line


@dataclass
class DatasetLine:
    src: str
    tgt: Optional[str]
    corpus: str = None  # we keep track of the corpus name as certain filters might need it
    score: Optional[float] = None  # optional score for mined corpora and similar

    # Store LID probabilities for each sentence. Needed only for debug purposes.
    src_lid_prob: Optional[float] = None
    tgt_lid_prob: Optional[float] = None


class FilteringCounts:
    def __init__(
        self,
        total_before: int = 0,  # total examples before filtering
        total_after: int = 0,  # total examples after filtering
        empty: int = 0,  # num of examples filtered due to being empty
        min_len: int = 0,
        max_len: int = 0,
        max_len_ratio: int = 0,
        min_src_unique_ratio: int = 0,
        max_toxicity: int = 0,
        max_toxicity_difference: int = 0,
        lid_threshold: int = 0,
        laser_threshold: int = 0,  # num of examples filtered due to LASER score
        source_dedup: int = 0,
        target_dedup: int = 0,
        pair_dedup: int = 0,
    ):
        self.total_before = total_before
        self.total_after = total_after

        # LengthFilter
        self.empty = empty
        self.min_len = min_len
        self.max_len = max_len
        self.max_len_ratio = max_len_ratio
        self.min_src_unique_ratio = min_src_unique_ratio

        # ToxicityFilter
        self.max_toxicity = max_toxicity
        self.max_toxicity_difference = max_toxicity_difference

        # LidFilter
        self.lid_threshold = lid_threshold

        # LaserFilter
        self.laser_threshold = laser_threshold

        # DedupFilter
        self.pair_dedup = pair_dedup
        self.target_dedup = target_dedup
        self.source_dedup = source_dedup

    def __add__(self, other):
        return FilteringCounts(
            **{key: val + getattr(other, key) for key, val in self.__dict__.items()}
        )

    def __radd__(self, other):
        if other == 0:
            return self
        return other.__add__(self)


class Filter:
    def filter_line(
        self, line: DatasetLine, counts: FilteringCounts
    ) -> Optional[DatasetLine]:
        raise NotImplementedError


# Copied from stopes
class DedupFilter(Filter):
    def __init__(
        self,
        dedup_pairs: bool,
        max_source_dedup: Optional[int],
        max_target_dedup: Optional[int],
    ):
        # pair deduplication
        self.dedup_pairs = dedup_pairs
        self.seen_pair_hashes: Set[int] = set()

        # source-side deduplication
        self.source_dedup = max_source_dedup
        self.source_dup_counts: Dict[int, int] = Counter()

        # target-side deduplication
        self.target_dedup = max_target_dedup
        self.target_dup_counts: Dict[int, int] = Counter()

    def filter_line(
        self, line: DatasetLine, counts: FilteringCounts
    ) -> Optional[DatasetLine]:

        if line.tgt is not None and (self.dedup_pairs or self.target_dedup):
            normalized_tgt = normalize_for_dedup(line.tgt)

        if self.dedup_pairs or self.source_dedup:
            normalized_src = normalize_for_dedup(line.src)

        if self.dedup_pairs:
            normalized = str(normalized_src)
            if line.tgt is not None:
                normalized += f"\t{normalized_tgt}"
            line_hash = xxhash.xxh3_64_intdigest(normalized)
            if line_hash in self.seen_pair_hashes:
                counts.pair_dedup += 1
                return None
            self.seen_pair_hashes.add(line_hash)

        if self.target_dedup and line.tgt is not None:
            line_hash = xxhash.xxh3_64_intdigest(normalized_tgt)
            if self.target_dup_counts[line_hash] >= self.target_dedup:
                counts.target_dedup += 1
                return None
            self.target_dup_counts[line_hash] += 1

        if self.source_dedup:
            line_hash = xxhash.xxh3_64_intdigest(normalized_src)
            if self.source_dup_counts[line_hash] >= self.source_dedup:
                counts.source_dedup += 1
                return None
            self.source_dup_counts[line_hash] += 1

        return line


class LengthFilter(Filter):
    def __init__(
        self,
        min_len: Optional[int],
        max_len: Optional[int],
        max_len_ratio: Optional[float],
        length_factors: Dict[str, float],
        src_lang: str,
        tgt_lang: str,
    ):
        self.min_len = min_len
        self.max_len = max_len
        self.max_len_ratio = max_len_ratio

        try:
            self.src_factor = length_factors[src_lang]
        except KeyError:
            logging.warning(f"Missing length factor for {src_lang}")
            self.src_factor = 1.0

        try:
            self.tgt_factor = length_factors[tgt_lang]
        except KeyError:
            logging.warning(f"Missing length factor for {tgt_lang}")
            self.tgt_factor = 1.0

    def filter_line(
        self, line: DatasetLine, counts: FilteringCounts
    ) -> Optional[DatasetLine]:
        # filter empty lines
        if not line.src or (line.tgt is not None and not line.tgt):
            counts.empty += 1
            return None

        if line.tgt is not None:
            if not line.tgt:
                counts.empty += 1
                return None

        if (
            self.min_len
            or self.max_len
            or self.max_len_ratio
        ):
            # min len, max len
            src_len = max(1, len(line.src) * self.src_factor)
            if self.min_len is not None and src_len < self.min_len:
                counts.min_len += 1
                return None
            if self.max_len is not None and src_len > self.max_len:
                counts.max_len += 1
                return None
            # same as above, but for tgt if set
            if line.tgt is not None:
                tgt_len = max(1, len(line.tgt) * self.tgt_factor)
                if self.min_len is not None and tgt_len < self.min_len:
                    counts.min_len += 1
                    return None
                if self.max_len is not None and tgt_len > self.max_len:
                    counts.max_len += 1
                    return None
                # len ratio
                if self.max_len_ratio is not None:
                    ratio = (
                        src_len / tgt_len if src_len > tgt_len else tgt_len / src_len
                    )
                    if ratio > self.max_len_ratio:
                        counts.max_len_ratio += 1
                        return None

        return line


if __name__ == '__main__':
    pass
    # file_path = 'examples/nllb/data/tmp.py'

    # # Method 1:
    # num_lines = int(subprocess.check_output(['wc', '-l', file_path]).decode('utf-8').split()[0])
    # print(num_lines)

    # # Method 2:
    # num_lines2 = count_lines(file_path)
    # print(num_lines2)