import typing
import os
from sys import exit
import logging

from .resources.type_file import File
from .resources.helpers import Analysis, human_size, hash_chunk
from .resources.errors import DuplicateFinderError, PermissionsError

log = logging.getLogger(__name__)

class DuplicateFinder:
    """
    A simple utility for finding duplicated files within a a specified path.
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
        if os.path.exists(path):  # make sure path exists
            self.root = path
        else:
            raise FileNotFoundError("Path does not exist.")

        self.recurse = recurse
        self.by_hash = by_hash
        self.hash_table = {}
        self.size_table = {}
        self.files = None
        self.junk_files = None


    def __fetch_files(self):
        """ Sets `self.files` to a tuple of File objects fetched from `self.root` recursively or non-recursively. """
        all_files = []  # to keep files
        log.info('  |_ [*] Fetching files...')
        if self.recurse:
            # use os.walk
            for root, _, files in os.walk(self.root):
                for file in files:
                    full_path = os.path.join(root, file)  # get full path
                    size = os.path.getsize(full_path)  # get size using full path
                    # creating a file object
                    file = File(name=file, size=size, root=root, secure_hash="")
                    all_files.append(file)
        else:
            # use os.listdir and filter files only.
            items = [i for i in os.listdir(self.root) if os.path.isfile(os.path.join(self.root, i))]
            for file in items:
                full_path = os.path.join(self.root, file)  # get full path
                size = os.path.getsize(full_path)  # get size
                # create file object
                file = File(name=file, size=size, root=self.root, secure_hash="")
                all_files.append(file)
        # return a tuple of all_files sorted
        self.files = tuple(sorted(all_files, key=lambda x: x.name))


    def __generate_size_table(self):
        """ Builds an index with files grouped by common sizes. """
        index = {}  # init index
        log.info("  |_ [*] Generating size table...")
        for file in self.files:
            # setdefault file size and file
            index.setdefault(file.size, []).append(file)
        # filter only sizes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        self.size_table = index
        log.info("     |_ [+] Generated size table successfully.")


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
        log.info("  |_ [*] Generating hash table...")
        for file in files:
            # set secure_hash of file objects
            try:
                file.secure_hash = hash_chunk(file, file.size)
            except PermissionError:
                raise PermissionsError(f"Access denied, cannot scan {file}")
            except TypeError:
                raise DuplicateFinderError(f"Cannot generate a secure hash for {file}")
            # setdefault file.secure_hash and file
            index.setdefault(file.secure_hash, []).append(file)
        # filter only hashes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        self.hash_table = index
        log.info("     |_ [+] Generated hash table successfully.")


    def get_junk_files(self):
        """ Returns the junk or files to delete leaving an original copy for each file """
        return self.junk_files


    def search_duplicate(self):
        """
        Main API of the DuplicateFinder class, calls all necessary methods does to find duplicates
        and sets junk files or files to delete.
        Finds duplicates using sizes if `self.by_hash` is set to False, otherwise by hash.
        Access it's result through `self.junk_files`.
        """
        log.info("\n[*] Searching for duplicates...")
        self.__fetch_files()  # fetch files
        if self.files:
            log.info(f"     |_ [+] Fetched successfully {len(self.files):,} files.")
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
            exit('     |_ [-] No files found. You might wanna check your path!')


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