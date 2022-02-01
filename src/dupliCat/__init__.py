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

import os
import typing
from collections import namedtuple
from hashlib import blake2b
from itertools import filterfalse


class DupliCatException(Exception):
    """base exception class"""


class SizeIndexEmpty(DupliCatException): ...


class HashIndexEmpty(DupliCatException): ...


class NoFilesFoundError(DupliCatException): ...


# The type file

class dupliFile:
    """ A class of keeping all needed info about a file """

    def __init__(self, name: str, root: os.PathLike, size: int, secure_hash: str) -> None:
        self.name = name  # basename of the file
        self.root = root  # the root dir of the file
        self.size = size  # size of the file
        self.secure_hash = secure_hash  # secure hash generated from first 1024 bytes read

    def delete(self) -> None:
        """Deletes this file from the system"""
        os.remove(os.path.join(self.root, self.name))

    def __repr__(self) -> str:
        """represents `repr(dupliFile)`"""
        return f"dupliFile(name={self.name!r}, root={self.root!r}, size={self.size}, secure_hash={self.secure_hash!r})"

    def __str__(self) -> str:
        """represents `str(dupliFile)`"""
        return f"dupliFile(name={self.name!r}, root={self.root!r}, size={self.size}, secure_hash={self.secure_hash!r})"

    def __gt__(self, other):
        return self.size > other.size or self.name > other.name

    def __lt__(self, other):
        return self.size < other.size or self.name > other.name

    def __eq__(self, other):
        return self.size == other.size or self.secure_hash == other.secure_hash

    def __ne__(self, other):
        return self.size != other.size or self.secure_hash != other.secure_hash


# analyses of duplicate search
Analysis = namedtuple("Analysis", ["total_count", "total_size", "most_occurrence"])


class dupliCat:
    """Manages duplicate files"""

    def __init__(self, path, recurse=False) -> None:
        # primary properties
        self.path = path
        self.recurse = recurse
        # created
        self.fetched_files: typing.List[dupliFile] = list()  # keeps all files fetched from `path`
        self.size_index = None  # keeps size index of files
        self.hash_index = None  # keeps hash index of files
        self.duplicates: typing.List[dupliFile] = list()  # keeps all duplicate files

    # Some helper functions

    @staticmethod
    def human_size(nbytes_: int) -> str:
        """
        Converts bytes to a human-readable size

            print(human_size(2024)) # -> 1.98 KB
        """
        suffixes = ["B", "KB", "MB", "GB", "TB", "PT"]
        index = 0
        while nbytes_ >= 1024 and index < len(suffixes) - 1:
            nbytes_ /= 1024
            index += 1
        size = round(nbytes_, 2)
        return f"{size:,} {suffixes[index]}"

    @staticmethod
    def read_chunk(file_: dupliFile, size: int = 400) -> bytes:
        """Reads first `size` chunks from file, `size` defaults to 400."""
        with open(os.path.join(file_.root, file_.name), 'rb') as f:
            chunk = f.read(size)
        return chunk

    @staticmethod
    def hash_chunk(text: str, key: int) -> str:
        """returns hashed version of text using `blake2b` hashing algorithm"""
        hash_ = blake2b(key=bytes(str(key), 'utf-8'))  # a hash object key set to file size
        # update hash with chunk
        hash_.update(text)
        # return a secure hash
        return hash_.hexdigest()

    def analyse(self) -> typing.Optional[Analysis]:
        """returns analysis on search"""
        # do we have duplicates?
        if self.duplicates:
            total_file_num = len(self.duplicates)  # total number duplicate files
            # total size of duplicate files
            total_size = self.human_size(sum(file_.size for file_ in self.duplicates))
            # do we have a hash index or was the search by a hash index?
            if self.hash_index:
                most_occurrence = len(max((i for i in self.hash_index.values()), key=lambda x: len(x)))
            else:
                most_occurrence = len(max((i for i in self.size_index.values()), key=lambda x: len(x)))
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
        file_.secure_hash = self.hash_chunk(chunk, key=file_.size)
        return file_

    def fetch_files(self) -> typing.Iterable[dupliFile]:
        """fetches all files from `self.path`"""
        # use os.walk to recursively fetch files
        if self.recurse:
            for root, _, files in os.walk(self.path, topdown=True):
                # create a file object
                for file_ in files:
                    size = os.path.getsize(os.path.join(root, file_))  # get size of file
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
                    os.listdir(self.path)
            ):
                size = os.path.getsize(os.path.join(self.path, file_))
                self.fetched_files.append(
                    dupliFile(name=file_, root=self.path, size=size, secure_hash="")
                )
        # return `self.fetched_files`
        if not self.fetched_files:
            raise NoFilesFoundError(f"no files found in the directory {self.path!r}, you might wanna check it out.")
        return self.fetched_files

    def generate_size_index(self, files: typing.Iterable = None) -> None:
        """generates index of files grouped together by sizes"""
        index = dict()
        files = files if files else self.fetched_files
        for file_ in files:
            # insert files into index grouped by size
            index.setdefault(file_.size, []).append(file_)
        # filter only sizes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        # set to `self.size_index`
        self.size_index = index

    def generate_hash_index(self, files: typing.Iterable = None, from_size: bool = False) -> None:
        """generates index of files grouped together by secure_hashes of the files
        Args:
            files: files to use in generating the index
            from_size: if set to True, hash index will be generated from `self.size_index`"""
        # use files else use self.fetched_files
        files_ = files if files else self.fetched_files
        if from_size:
            if not self.size_index:
                raise SizeIndexEmpty(
                    "can't generate hash index from empty size index, did you generate size index?")
            elif self.size_index:
                # get files from size index
                files_ = [f for items in self.size_index.values() for f in items]
        if not files_:
            raise NoFilesFoundError("no files found, did you forget to fetch files?")
        # initialize index
        index = dict()
        # insert data in index
        for file_ in files_:
            try:
                # generate secure hash for each file
                self.generate_secure_hash(file_)
            except (PermissionError, TypeError):
                ...  # do nothing...
            index.setdefault(file_.secure_hash, []).append(file_)
        # filter only sizes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        # set to `self.size_index`
        self.hash_index = index

    def search_duplicate(self, use_hash=True, from_size=True) -> typing.Iterator[dupliFile]:
        """search for duplicate files either `by_hash` or `by_size` or both."""
        # get files
        files_ = self.fetched_files if self.fetched_files else self.fetch_files()
        # generate size index
        self.generate_size_index(files=files_)
        # find duplicates by both methods
        if use_hash:
            # enable hash generation from size index
            self.generate_hash_index(files=files_, from_size=from_size)
            # set all duplicated files from hash index
            duplicate_files = [file_ for items in self.hash_index.values() for file_ in items]
        else:
            duplicate_files = [file_ for items in self.size_index.values() for file_ in items]
        # set and return
        self.duplicates = duplicate_files
        return duplicate_files


__all__ = [
    "dupliFile", "NoFilesFoundError", "SizeIndexEmpty", "DupliCatException", "HashIndexEmpty", "dupliCat", "Analysis"]
