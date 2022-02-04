# MIT License

# Copyright (c) 2022 Divine Darkey

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import dupliCat
import click
import os
from collections import defaultdict


@click.group()
@click.option("--path", default=os.getcwd(), help="Path to the directory to be scanned")
@click.option("--no-recurse", is_flag=True, help="Do not recurse into subdirectories")
def main(path, no_recurse):
    main.duplicat = dupliCat.dupliCat(path=path, recurse=not no_recurse)
    click.echo(f"Scanning {path!r}...\n")


@main.command(name="search-duplicates")
@click.option("--dont-use-hash", is_flag=True, help="Do not use hash to compare files")
@click.option("--dont-use-size", is_flag=True, help="Do not use size to compare files")
def search_duplicates(dont_use_hash, dont_use_size):
    duplicates = main.duplicat.search_duplicate(
        use_hash=not dont_use_hash, from_size=not dont_use_size
    )
    grouped_duplicates = defaultdict(list)
    for duplicate in duplicates:
        grouped_duplicates[duplicate.secure_hash].append(duplicate)

    for i, files in enumerate(grouped_duplicates.values(), start=1):
        click.echo(f"{i}. {', '.join([f'{f.path!r}' for f in files])}")


if __name__ == "__main__":
    main()
