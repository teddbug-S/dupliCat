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
def main() -> bool:
    pass


@main.command(name="search-duplicates")
@click.option("--no-recurse", is_flag=True, help="Do not recurse into subdirectories")
@click.option("--path", default=os.getcwd(), help="Path to the directory to be scanned")
@click.option("--dont-use-hash", is_flag=True, help="Do not use hash to compare files")
@click.option("--dont-use-size", is_flag=True, help="Do not use size to compare files")
@click.option("--delete", is_flag=True, help="Delete duplicate files.")
def search_duplicates(
    path: str, no_recurse: bool, dont_use_hash: bool, dont_use_size: bool, delete: bool
) -> None:
    click.echo(click.style(f"Scanning {path!r}...\n", fg="green", bold=True))

    duplicat = dupliCat.dupliCat(path=path, recurse=not no_recurse)
    try:
        duplicates = duplicat.search_duplicate(
            use_hash=not dont_use_hash, from_size=not dont_use_size
        )
    except dupliCat.NoDuplicatesFound:
        click.echo(click.style("No duplicates found.", fg="green", bold=True))
        return None
    except dupliCat.NoFilesFoundError:
        click.echo(click.style(f"{path!r} directory is empty.", bold=True))
        return None

    grouped_duplicates = defaultdict(list)  # {SECURE_HASH: [DUPLIFILE, DUPLIFILE, ...]}
    for duplicate in duplicates:
        grouped_duplicates[duplicate.secure_hash].append(duplicate)

    length = len(grouped_duplicates)
    click.echo(
        click.style(
            f"Found {length} {'duplicate' if length == 1 else 'duplicates'}", bold=True
        )
    )

    # Print duplicated files
    for i, files in enumerate(grouped_duplicates.values(), start=1):
        q = click.style(
            f"{i}. Size: {files[0].human_size}:\t{', '.join([repr(f.path) for f in files])}",
            fg="yellow",
            bold=True,
        )
        click.echo(q)

    if delete and length > 0:
        # asking for confirmation on whether to delete files
        confirmation = click.confirm(
            click.style(
                "\nDo you want to delete duplicates? (This action is irreversible)",
                bold=True,
            )
        )
        if not confirmation:
            return None

        # ask if we should keep a copy of a duplicate file or not
        keep_copy = click.confirm(
            click.style("Do you want to keep a copy of the original file?", bold=True)
        )

        if keep_copy:  # remove first file and keep the rest to be deleted
            files = [fs[1:] for fs in grouped_duplicates.values()]
        else:
            files = list(grouped_duplicates.values())

        # flattening the list
        files = [f for fs in files for f in fs]

        # deleting files
        counter = 0
        for f in files:
            try:
                f.delete()
            except Exception:
                continue
            else:
                counter += 1

        color = "green" if counter == len(files) else "yellow" if counter > 0 else "red"
        click.echo(
            click.style(
                f"\nDeleted {counter} {'file' if counter == 1 else 'files'} out of {len(files)}",
                bold=True, fg=color
            )
        )


if __name__ == "__main__":
    main()
