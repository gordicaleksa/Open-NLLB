from pathlib import Path
import subprocess
import shlex
import typing as tp


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


if __name__ == '__main__':
    pass
    # file_path = 'examples/nllb/data/tmp.py'

    # # Method 1:
    # num_lines = int(subprocess.check_output(['wc', '-l', file_path]).decode('utf-8').split()[0])
    # print(num_lines)

    # # Method 2:
    # num_lines2 = count_lines(file_path)
    # print(num_lines2)