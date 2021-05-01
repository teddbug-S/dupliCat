import argparse
import hashlib
import os
from sys import exit
from textwrap import dedent
from TypeFile import File


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
            exit("[-] Path does not exist.")
        self.recurse = recurse
        self.by_hash = by_hash
        self.hash_table = {}
        self.size_table = {}
        self.files = None
        self.junk_files = None

    @staticmethod
    def read_chunk(file: File, size) -> bytes:
        """ Reads first [size] chunks from file, size defaults to 400 """
        file = os.path.join(file.root, file.name)  # get full path of file
        with open(file, 'rb') as file:
            # read chunk size
            chunk = file.read(size)
        return chunk

    def __hash_chunk(self, file: File, key: int):
        """ Returns a secure hash of first 1024 bytes from specified file. """
        chunk = self.read_chunk(file, size=1024)  # read chunk
        hash_ = hashlib.blake2b(key=bytes(str(key), 'utf-8'))  # a hash object key set to file size
        # update hash with chunk
        hash_.update(chunk)
        # return a secure hash
        return hash_.hexdigest()

    def __fetch_files(self):
        """ Sets `self.files` to a tuple of File objects fetched from `self.root` recursively or non-recursively. """
        all_files = []  # to keep files
        print('  |_ [*] Fetching files...')
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
        print("  |_ [*] Generating size table...")
        for file in self.files:
            # setdefault file size and file
            index.setdefault(file.size, []).append(file)
        # filter only sizes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        self.size_table = index
        print("     |_ [+] Generated size table successfully.")

    def __generate_hash_table(self, from_size: bool = True):
        """ Builds an index of files grouped by secure hashes of read 1024 bytes.
        :arg
            `from_size`:

            If from `from_size` is set to False, hash table will be generated using `self.files`.
            Otherwise, it generates the hash table using `self.size_table` therefore it will internally call
            `self.__generate_size_table` if `self.size_table` is empty.
        """
        # get files from __size_index in order to save time and speed also enhances accuracy
        print("  |_ [*] Generating hash table...")
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
        for file in files:
            # set secure_hash of file objects
            try:
                file.secure_hash = self.__hash_chunk(file, file.size)
            except PermissionError:
                print(f"     |_ [-] Access Denied! Can't scan {file}")
            except TypeError:
                print(f"     |_ [-] Could generate a secure hash for {file}")
            # setdefault file.secure_hash and file
            index.setdefault(file.secure_hash, []).append(file)
        # filter only hashes containing two or more files
        index = {key: value for key, value in index.items() if len(value) > 1}
        self.hash_table = index
        print("     |_ [+] Generated hash table successfully.")

    def get_junk_files(self):
        """ Returns the junk or files to delete leaving an original copy for each file """
        return self.junk_files

    def find_junk_files(self):
        """
        Main API of the DuplicateFinder class, calls all necessary methods does to find duplicates
        and sets junk files or files to delete.

        Finds duplicates using sizes if `self.by_hash` is set to False, otherwise by hash.
        Access it's result through `self.junk_files`.
        """
        print("\n[*] Searching for duplicates...")
        self.__fetch_files()  # fetch files
        if self.files:
            print(f"     |_ [+] Fetched successfully {len(self.files):,} files.")
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

    @property
    def analysis(self) -> dict:
        """
        Generates an analysis on the search for duplicates

        Returns a dictionary containing values for each analysis.

        keys:
            'total_count' :  total number of all duplicates found
            'total_size' : total size of all junk files on disk.
            'most_occurred_file' : as name suggests
        """
        if self.junk_files:
            total_file_num = len(self.junk_files)  # total number junk files found
            total_file_size_b = sum(file.size for file in self.junk_files)  # total size of junk files
            # found in bytes
            total_file_size_kb = total_file_size_b / 1000  # total size in kilobytes
            total_file_size_mb = total_file_size_kb / 1000  # total size in megabytes
            total_file_size_gb = total_file_size_mb / 1000  # total size in gigabytes
            # create the ultimate total size choosing a suitable value and formatting with unit
            if total_file_size_gb < 1:
                total_size = f"{total_file_size_mb:.2f} MB"
            elif total_file_size_mb < 1:
                total_size = f"{total_file_size_kb:.2f} KB"
            elif total_file_size_kb < 1:
                total_size = f"{total_file_size_b:.2f} B"
            else:
                total_size = f"{total_file_size_gb:.2f} GB"
            if self.hash_table:
                most_occurrence = len(max((i for i in self.hash_table.values()), key=lambda x: len(x)))
            else:
                most_occurrence = len(max((i for i in self.size_table.values()), key=lambda x: len(x)))
            # set each analysis
            result = {
                'total_size': total_size,
                'total_count': total_file_num,
                'most_occurrence': most_occurrence
            }
            return result
        else:
            return {}


if __name__ == '__main__':

    def main():
        parser = argparse.ArgumentParser(description="Searches for duplicate files in a specified path.")
        parser.add_argument("--path",
                            '-p', default=os.curdir,
                            help="specify path to look for duplicates, defaults to current directory")
        parser.add_argument("--recurse", '-r', action='store_const', const=True,
                            help="set this flag if you want search to be recursive which includes files in sub-dirs")
        parser.add_argument("--by_hash", '-s', action='store_const', const=False, default=True,
                            help="set this flag if you want to use size table otherwise, hash table.")
        args = parser.parse_args()
        finder = DuplicateFinder(path=args.path, recurse=args.recurse, by_hash=args.by_hash)
        finder.find_junk_files()
        analysis = finder.analysis
        if analysis:
            temp = f"""
            Total duplicates found: {analysis['total_count']:,}
            Total size on disk: {analysis['total_size']}
            Most occurrence: {analysis['most_occurrence']:,}
            ---------------------------------
            """
            print(dedent(temp))
        else:
            print("[-] No duplicates found.")


    main()
