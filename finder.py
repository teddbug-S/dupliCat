import argparse
import typing
from sys import exit
from textwrap import dedent
from colored import fg, attr
from dataclasses import dataclass
from os import walk, PathLike, system, listdir
from os import path as _path
from contextlib import redirect_stdout
from collections import namedtuple
from hashlib import blake2b
from io import StringIO
from functools import wraps

from pathlib import Path


@dataclass
class File:
    """ A dataclass of keeping all needed info about a file """
    name: str
    size: int
    root: PathLike
    secure_hash: str

    def delete(self):
        ...

    def __gt__(self, other):
        return self.size > other.size or self.name > other.name

    def __lt__(self, other):
        return self.size < other.size or self.name > other.name

    def __eq__(self, other):
        return self.size == other.size or self.secure_hash == other.secure_hash

    def __ne__(self, other):
        return self.size != other.size or self.secure_hash != other.secure_hash


def silent(callback: typing.Callable):
    @wraps(callback)
    def wrapper(*args, **kwargs):
        stream = StringIO()
        with redirect_stdout(stream):
            result = callback(*args, **kwargs)
        return result
    return wrapper


def human_size(nbytes_: int) -> str:
    """
    Converts bytes to a human readable size

        print(human_size(2024)) # -> 1.98 KB
    """
    suffixes = ["B", "KB", "MB", "GB", "TB", "PT"]
    index = 0
    while nbytes_ >= 1024 and index < len(suffixes) - 1:
        nbytes_ /= 1024
        index += 1
    size = round(nbytes_, 2)
    return f"{size:,} {suffixes[index]}"


def read_chunk(file: File, size: int=400) -> bytes:
    """ Reads first [size] chunks from file, size defaults to 400 """
    file = _path.join(file.root, file.name)  # get full path of file
    with open(file, 'rb') as file:
        # read chunk size
        chunk = file.read(size)
    return chunk


def hash_chunk(file: File, key: int):
    """ Returns a secure hash of first 1024 bytes from specified file. """
    chunk = read_chunk(file, size=1024)  # read chunk
    hash_ = blake2b(key=bytes(str(key), 'utf-8'))  # a hash object key set to file size
    # update hash with chunk
    hash_.update(chunk)
    # return a secure hash
    return hash_.hexdigest()


Analysis = namedtuple("Analysis", ["total_count", "total_size", "most_occurrence"])


class DupliCat:
    """
    A simple utility for finding duplicated files within a a specified _path.
    :param path
        Path which search will be done
    :param recurse
       When set to True, searches all sub-directories in the path given,
       defaults to False.
       Duplicates can exist with different names in different directories.
    :param by_hash
       Find duplicates using hash table if set to True otherwise uses size_table.
       Using the hash_table is more accurate in conditions where different files
       have same sizes and quite fast since it generates it from the size table,
       using the size table is more faster and quite better since
       those conditions are rare!
       Oops, they are not rare!!!
       NOTE: We recommend you use the hash table to avoid lose of data or important files.
    :property:
        files:
            A tuple of all file listings of the `path` parameter.
        size_table:
            A key-value pair of files grouped together by sizes, can be accessed through `self.size_table`.
        hash_table:
            A key-value pair of files and grouped by a secure hash of the
            first 1024 bytes of data read from each file, can be accessed through `self.hash_table`.
        junk_files:
            A tuple of files reserved as junk and can all be deleted.
        analysis:
            returns analysis on search made
    """

    def __init__(self, /, path, recurse=False, by_hash=True):
        path_ = Path(path)
        if path_.exists():  # make sure path exists
            self.root = path
        else:
            exit("%s[-]❗Path does not exist.%s" %(fg('red'), attr('reset')))
        self.recurse = recurse
        self.by_hash = by_hash
        self.hash_table = {}
        self.size_table = {}
        self.files = None
        self.junk_files = None

    def __fetch_files(self):
        """ Sets `self.files` to a tuple of File objects fetched from `self.root` recursively or non-recursively. """
        all_files = []  # to keep files
        print('  %s↳[*]📂 Fetching files...%s' %(fg('blue'), attr('reset')))
        if self.recurse:
            # use walk
            for root, _, files in walk(self.root):
                for file in files:
                    full_path = _path.join(root, file)  # get full path
                    size = _path.getsize(full_path)  # get size using full path
                    # creating a file object
                    file = File(name=file, size=size, root=root, secure_hash="")
                    all_files.append(file)
        else:
            # use listdir and filter files only.
            items = [i for i in listdir(self.root) if _path.isfile(_path.join(self.root, i))]
            for file in items:
                full_path = _path.join(self.root, file)  # get full path
                size = _path.getsize(full_path)  # get size
                # create file object
                file = File(name=file, size=size, root=self.root, secure_hash="")
                all_files.append(file)
        # return a tuple of all_files sorted
        self.files = tuple(sorted(all_files, key=lambda x: x.name))

    def __generate_size_table(self):
        """ Builds an index with files grouped by common sizes. """
        index = {}  # init index
        print("  %s↳[*]🚀 Generating size table...%s" %(fg('blue'), attr('reset')))
        for file in self.files:
            # setdefault file size and file
            index.setdefault(file.size, []).append(file)
        # filter only sizes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        self.size_table = index
        print("     %s↳[+]✅ Generated size table successfully.%s" %(fg('green'), attr('reset')))

    def __generate_hash_table(self, from_size: bool = True):
        """ Builds an index of files grouped by secure hashes of read 1024 bytes.
        :arg
            `from_size`:
            If from `from_size` is set to False, hash table will be generated using `self.files`.
            Otherwise, it generates the hash table using `self.size_table` therefore it will internally call
            `self.__generate_size_table` if `self.size_table` is empty.
        """
        # get files from __size_index in order to save time and speed also enhances accuracy
        if self.files:
            if from_size:
                if not self.size_table:
                    self.__generate_size_table()
                files = [file for i in self.size_table.values() for file in i]
            else:
                files = self.files
        else:
            return 0

        index = {}  # init index
        print("  %s↳[*]🚀 Generating hash table...%s" %(fg('blue'), attr('reset')))
        for file in files:
            # set secure_hash of file objects
            try:
                file.secure_hash = hash_chunk(file, file.size)
            except PermissionError:
                print(f"     %s↳[-]❌ Access Denied! Can't scan {file}%s" %(fg('red'), attr('reset')))
            except TypeError:
                print(f"     %s↳[-]😕 Could generate a secure hash for {file}%s" %(fg('blue'), attr('reset')))
            # setdefault file.secure_hash and file
            index.setdefault(file.secure_hash, []).append(file)
        # filter only hashes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        self.hash_table = index
        print("     %s↳[+]✅ Generated hash table successfully.%s" %(fg('green'), attr('reset')))

    def get_junk_files(self) -> typing.List[File]:
        """ Returns the junk or files to delete leaving an original copy for each file """
        return self.junk_files

    def search_duplicate(self):
        """
        Main API of the DupliCat class, calls all necessary methods does to find duplicates
        and sets junk files or files to delete.
        Finds duplicates using sizes if `self.by_hash` is set to False, otherwise by hash.
        Access it's result through `self.junk_files`.
        """
        print("\n%s[*]🔍 Searching for duplicates...%s" %(fg('blue'), attr('reset')))
        self.__fetch_files()  # fetch files
        if self.files:
            print(f"     %s↳[+]✅ Fetched successfully {len(self.files):,} files.%s" %
            (fg('green'), attr('reset')))
            if self.by_hash:
                # use hash table
                self.__generate_hash_table()
                self.junk_files = [file for i in self.hash_table.values() for file in i[1:]]  # get junk files by
                # leaving an original copy of each duplicate
            else:
                # use size_table
                self.__generate_size_table()
                self.junk_files = [file for i in self.size_table.values() for file in i[1:]]  # get junk files by
                # leaving an original copy of each duplicate
        else:
            exit('  %s⛔ [-] No files found. You might wanna check your path!%s' %(fg('yellow'), attr('reset')))

    @silent
    def search_silent(self):
        """
        A wrapper for the `search_duplicate` method.
        Use if you don't want anything to be printed out during search.
        :return:
        """
        self.search_duplicate()

    @property
    def analysis(self) -> typing.Optional[Analysis]:
        """
        Generates an analysis on the search for duplicates
        Returns an ``Analysis`` namedtuple.
        """
        if self.junk_files:
            total_file_num = len(self.junk_files)  # total number junk files found
            total_file_size_b = sum(file.size for file in self.junk_files)  # total size of junk files
            total_size = human_size(total_file_size_b)

            if self.hash_table:
                most_occurrence = len(max((i for i in self.hash_table.values()), key=lambda x: len(x)))
            else:
                most_occurrence = len(max((i for i in self.size_table.values()), key=lambda x: len(x)))
            # set each analysis
            result = Analysis(total_file_num, total_size, most_occurrence)
            return result
        # If we've reached this point, return ``None``
        return None


if __name__ == '__main__':

    def main():
        parser = argparse.ArgumentParser(description="Searches for duplicate files in a specified _path.")
        parser.add_argument("--path", '-p', default=curdir,
                            help="specify path to look for duplicates, defaults to current directory")
        parser.add_argument("--recurse", '-r', action='store_const', const=True,
                            help="set this flag if you want search to be recursive which includes files in sub-dirs")
        parser.add_argument("--by_hash", '-s', action='store_const', const=False, default=True,
                            help="set this flag if you want to use size table otherwise, hash table.")
        args = parser.parse_args()
        finder = DupliCat(path=args.path, recurse=args.recurse, by_hash=args.by_hash)
        finder.search_duplicate()
        analysis = finder.analysis
        if analysis is not None:
            temp = f"""
            Total duplicates found: {analysis.total_count:,}
            Total size on disk: {analysis.total_size:}
            Most occurrence: {analysis.most_occurrence:,}
            ---------------------------------
            """
            print(dedent(temp))
        else:
            print("[!] No duplicates found.")


    main()