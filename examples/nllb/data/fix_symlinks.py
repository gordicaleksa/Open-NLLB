import os
from pathlib import Path


def symlink(target: Path, actual: Path) -> None:
    """Symlink, but allows overidding previous symlink"""
    assert actual.exists(), f"actual path: {actual} doesn't exist"
    if target.is_symlink():
        target.unlink()
    target.symlink_to(actual)


max_num_shards = 11


dict_file = Path("/home/gordicaleksa/python_data_utils/spm_models/flores200_sacrebleu_tokenizer_spm.dict.txt")
data_root = "/home/gordicaleksa/python_data_utils/data_bin/"

def fix_dict_symlinks():
    # Fix symlink for dict files
    for i in range(max_num_shards):
        for shard_dir_name in os.listdir(data_root):
            shard_dir_path = os.path.join(data_root, shard_dir_name)
            dict_paths = [filepath for filepath in os.listdir(shard_dir_path) if filepath.startswith("dict")]
            for dict_path in dict_paths:
                target_path = Path(os.path.join(shard_dir_path, dict_path))
                symlink(target_path, dict_file)


def fix_valid_symlinks():
    # Get all valid files from shard000
    target_valid_files = []
    for shard_dir_name in os.listdir(data_root):
        if not shard_dir_name.startswith("shard000"):
            continue
        shard_dir_path = os.path.join(data_root, shard_dir_name)
        target_valid_files.extend([filepath for filepath in os.listdir(shard_dir_path) if filepath.startswith("valid")])

    for shard_dir_name in os.listdir(data_root):
        if shard_dir_name.startswith("shard000"):
            continue
        shard_dir_path = os.path.join(data_root, shard_dir_name)
        source_valid_files = [filepath for filepath in os.listdir(shard_dir_path) if filepath.startswith("valid")]
        for source_filename in source_valid_files:
            source_path = Path(os.path.join(shard_dir_path, source_filename))
            symlink(source_path, Path(os.path.join(data_root, f"shard{0:03d}", source_filename)))


fix_valid_symlinks()