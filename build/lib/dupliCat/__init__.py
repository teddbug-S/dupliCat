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

from __future__ import annotations

import os
from typing import List, Dict, Union, Optional, Iterable, Callable, Any
from collections import namedtuple
from hashlib import blake2b
from itertools import filterfalse
from functools import wraps, cached_property


class DupliCatException(Exception):
    """base exception class"""


class NoFilesFoundError(DupliCatException):
    ...


class NoDuplicatesFound(DupliCatException):
    ...


def _check_instance(fn: Callable[[Any, Any], bool]) -> Callable[[Any, Any], bool]:
    # Simple decorator for the comparison operators,
    # checks if ``self`` and ``other`` are the same object.
    @wraps(fn)
    def wrapper(self: Any, other: Any) -> bool:
        if isinstance(other, type(self)):
            return fn(self, other)
        raise TypeError(
            f"Can't compare {type(self).__name__!r} with {type(other).__name__!r}"
        )

    return wrapper


# The type file


class dupliFile:
    """A class of keeping all needed info about a file"""

    def __init__(
        self, name: str, root: os.PathLike, size: int, secure_hash: str
    ) -> None:
        self.name: str = name  # basename of the file
        self.root: os.PathLike = root  # the root dir of the file
        self.path: str = os.path.join(root, name)  # the full path of the file
        self.size: int = size  # size of the file
        self.secure_hash: str = (
            secure_hash  # secure hash generated from first 1024 bytes read
        )

    def delete(self) -> None:
        """Deletes this file from the system"""
        os.remove(self.path)

    def __repr__(self) -> str:
        """represents `repr(dupliFile)`"""
        return f"dupliFile(name={self.name!r}, root={self.root!r}, size={self.size}, secure_hash={self.secure_hash!r})"

    __str__ = __repr__

    @_check_instance
    def __gt__(self, other: dupliFile) -> bool:
        return self.size > other.size or self.name > other.name

    @_check_instance
    def __ge__(self, other: dupliFile) -> bool:
        return self.size >= other.size or self.name >= other.name

    @_check_instance
    def __lt__(self, other: dupliFile) -> bool:
        return self.size < other.size or self.name < other.name

    @_check_instance
    def __le__(self, other: dupliFile) -> bool:
        return self.size <= other.size or self.name <= other.name

    @_check_instance
    def __eq__(self, other: dupliFile) -> bool:
        return self.size == other.size or self.secure_hash == other.secure_hash

    @_check_instance
    def __ne__(self, other: dupliFile) -> bool:
        return self.size != other.size or self.secure_hash != other.secure_hash

    @cached_property
    def human_size(self) -> str:
        return dupliCat.human_size(self.size)


# analyses of duplicate search
Analysis = namedtuple("Analysis", ["total_count", "total_size", "most_occurrence"])


class dupliCat:
    """Manages duplicate files"""

    def __init__(self, path, recurse=False) -> None:
        # primary properties
        self.path = path
        self.recurse = recurse
        # created
        self.fetched_files: List[
            dupliFile
        ] = list()  # keeps all files fetched from `path`
        self.size_index: Dict[int, List[dupliFile]] = {}  # keeps size index of files
        self.hash_index: Dict[str, List[dupliFile]] = {}  # keeps hash index of files
        self.duplicates: List[dupliFile] = list()  # keeps all duplicate files

    # Some helper functions

    @staticmethod
    def human_size(nbytes: Union[int, float]) -> str:
        """
        Converts bytes to a human-readable size

            print(human_size(2024)) # -> 1.98 KB
        """
        suffixes = ["B", "KB", "MB", "GB", "TB", "PT"]
        index = 0
        while nbytes >= 1024 and index < len(suffixes) - 1:
            nbytes /= 1024
            index += 1
        size = round(nbytes, 2)
        return f"{size:,} {suffixes[index]}"

    @staticmethod
    def read_chunk(file_: dupliFile, size: int = 400) -> bytes:
        """Reads first `size` chunks from file, `size` defaults to 400."""
        with open(os.path.join(file_.root, file_.name), "rb") as f:
            chunk = f.read(size)
        return chunk

    @staticmethod
    def hash_chunk(text: str, key: int) -> str:
        """returns hashed version of text using `blake2b` hashing algorithm"""
        hash_ = blake2b(
            key=bytes(str(key), "utf-8")
        )  # a hash object key set to file size
        # update hash with chunk
        hash_.update(text)  # type: ignore
        # return a secure hash
        return hash_.hexdigest()

    def analyse(self) -> Optional[Analysis]:
        """returns analysis on search"""
        # do we have duplicates?
        if self.duplicates:
            total_file_num = len(self.duplicates)  # total number duplicate files
            # total size of duplicate files
            total_size = self.human_size(sum(file_.size for file_ in self.duplicates))
            # do we have a hash index or was the search by a hash index?
            if self.hash_index:
                most_occurrence = len(
                    max((i for i in self.hash_index.values()), key=lambda x: len(x))
                )
            else:
                most_occurrence = len(
                    max((i for i in self.size_index.values()), key=lambda x: len(x))
                )
            # set analysis parameters and return
            return Analysis(total_file_num, total_size, most_occurrence)

        # If we've reached this point, return ``None``
        return None

    def generate_secure_hash(self, file_: dupliFile) -> dupliFile:
        """
        generates and sets secure_hash attribute of file with encryption key as the size of `file_`.
        Returns the file
        """
        # first read 1024 data chunk from file_
        chunk = self.read_chunk(file_, size=1024)
        # generate and set secure hash
        # hash index doesn't get generated when chunk is turned into str
        file_.secure_hash = self.hash_chunk(chunk, key=file_.size)  # type: ignore
        return file_

    def fetch_files(self) -> Iterable[dupliFile]:
        """fetches all files from `self.path`"""
        # use os.walk to recursively fetch files
        if self.recurse:
            for root, _, files in os.walk(self.path, topdown=True):
                # create a file object
                for file_ in files:
                    try:
                        size = os.path.getsize(
                            os.path.join(root, file_)
                        )  # get size of file
                    except FileNotFoundError:
                        ...
                    else:
                        # append file to `self.fetched_files`
                        self.fetched_files.append(
                            dupliFile(name=file_, root=root, size=size, secure_hash="")
                        )
        else:
            # fetch all files in `self.path` with `os.listdir`
            for file_ in filterfalse(
                # filter out dirs with `fiterfalse`
                lambda x: not os.path.isfile(os.path.join(self.path, x)),
                # directory listing with os.listdir
                os.listdir(self.path),
            ):
                # sometimes somehow some files are returned from fetch but raises FileNotFoundError whenever they are been used.
                try:
                    size = os.path.getsize(os.path.join(self.path, file_))
                except FileNotFoundError:
                    ...
                else:
                    self.fetched_files.append(
                        dupliFile(name=file_, root=self.path, size=size, secure_hash="")
                    )
        # return `self.fetched_files`
        if not self.fetched_files:
            raise NoFilesFoundError(
                f"no files found in the directory {self.path!r}, you might wanna check it out."
            )
        return self.fetched_files.copy()

    def generate_size_index(self, files: Iterable = None) -> None:
        """generates index of files grouped together by sizes"""
        index: Dict[int, List[dupliFile]] = dict()
        files = files if files else self.fetched_files
        for file_ in files:
            # insert files into index grouped by size
            index.setdefault(file_.size, []).append(file_)
        # filter only sizes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        # set to `self.size_index`
        self.size_index = index

    def generate_hash_index(self, files: Iterable = None) -> None:
        """generates index of files grouped together by secure_hashes of the files
        Args:
            files: files to use in generating the index"""
        # use files else use self.fetched_files
        files_ = files if files else self.fetched_files
        if not files_:
            raise NoFilesFoundError("no files found, did you forget to fetch files?")
        # initialize index
        index: Dict[str, List[dupliFile]] = dict()
        # insert data in index
        for file_ in files_:
            try:
                # generate secure hash for each file
                self.generate_secure_hash(file_)
            except (PermissionError, TypeError):
                pass  # do nothing...
            index.setdefault(file_.secure_hash, []).append(file_)
        # filter only sizes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        # set to `self.size_index`
        self.hash_index = index

    def search_duplicate(self, use_hash=True, from_size=True) -> List[dupliFile]:
        """search for duplicate files either `by_hash` or `by_size` or both."""
        # get files
        files_ = self.fetched_files if self.fetched_files else self.fetch_files()
        # generate size index
        self.generate_size_index(files=files_)
        # find duplicates by both methods
        if use_hash:
            if (
                from_size and not self.size_index
            ):  # from_size should be controlles by `search_duplicate`
                # not `generate_hash_index`
                raise NoDuplicatesFound("No duplicates found!")
            # else use files from size index
            files_ = [file_ for items in self.size_index.values() for file_ in items]
            # enable hash generation from size index
            self.generate_hash_index(files=files_)
            # set all duplicated files from hash index
            duplicate_files = [
                file_ for items in self.hash_index.values() for file_ in items
            ]
        else:
            duplicate_files = [
                file_ for items in self.size_index.values() for file_ in items
            ]
        # set and return a copy
        self.duplicates = duplicate_files
        return duplicate_files.copy()


__all__ = (
    "dupliFile",
    "NoFilesFoundError",
    "DupliCatException",
    "NoDuplicatesFound",
    "dupliCat",
    "Analysis",
)
