import argparse
import logging
import os
from textwrap import dedent
from .duplicate_finder import DuplicateFinder

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="Searches for duplicate files in a specified path.")
    parser.add_argument("--path", '-p', default=os.curdir,
                        help="specify path to look for duplicates, defaults to current directory")
    parser.add_argument("--recurse", '-r', action='store_const', const=True,
                        help="set this flag if you want search to be recursive which includes files in sub-dirs")
    parser.add_argument("--by_hash", '-s', action='store_const', const=False, default=True,
                        help="set this flag if you want to use size table otherwise, hash table.")
    args = parser.parse_args()
    finder = DuplicateFinder(path=args.path, recurse=args.recurse, by_hash=args.by_hash)
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
        print("[-] No duplicates found.")


if __name__ == "__main__":
    main()