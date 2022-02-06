# DupliCat

A simple utility for finding duplicated files within a specified path.
It is intended to be a library but can also be used as a commandline tool,
it doesn't delete the duplicate files found but returns a list of junk files so that you can choose the ones to delete.

## Usage As A Library

- Import the [dupliCat](https://github.com/teddbug-S/dupliCat/blob/main/src/dupliCat/__init__.py) class and create an object by passing the following arguments,
  - `path`
           where the search will be made, defaults to current directory.
  - `recurse`
           boolean, set to true if you want it to recurse down to all files in the path including sub-dirs
           defaults to `False`

### Methods

- the `generate_secure_hash` method takes a file as first argument and generates a secure-hash for it.
     Hashing algorithm is blake2b, key is the size of the file, it returns the file with secure_hash attribute
     set. File must be of type `dupliFile`.

- `read_chunk` this method reads a default 400 bytes of data from file. It takes the file as first positional
      argument and size as second argument which defaults to 400. File must be of type `dupliFile`

- `human_size` this is a static method that converts bytes into human-readable format.

   ```doctest
     >>> human_size(nbytes=123456)
     >>> 120.56 KB
   ```

- `hash_chunk` static method, takes two positional arguments, `text: str` and `key: int`
      hashes text with key using blake2b.
  
- call the `search_duplicate` method to begin the 🔍 search, search results will be stored in
       the `duplicates` property of the class. This method is somewhat the main api of the class, it
       does everything for you, calling other methods instead of this might remove the functionality of
       using files from `size_index` as input for generating a hash index.

   the `search_duplicate` method has the following optional arguments

  - `use_hash`
           find duplicates using hash table if set to True otherwise uses size_table, using the
           hash_table is more accurate in conditions where different files have same sizes
           and quite fast since table is generated using the size table, parameter defaults to `True`.
           Using the size table is faster but does not guarantee accuracy.
  - `from_size`
          it defaults to True, this enables the `search_duplicate` method to generate a hash index
          using files from the size index. Defaults to `True`.

    Note:
        Both parameters are set to True for more accurate search since search will be done using the
       `size_index` and also the `hash_index`.
        Junk files set by this method contains all duplicates with one file left over for each.

- use the `analyse` method to analyse search result, this returns a named tuple of type `Analysis`.
   It contains
       the total number of duplicate files accessed through `analysis.total_file_num`, their total size on the disk
       accessed through `analysis.total_size` and the most occurred file, accessed through `analysis.most_occurrence`.

- the `generate_size_index` method is used to generate the size index from files.
  It sets the result or the generated size_index to `self.size_index`
  takes the paramter
  - `files`: files from which size index should be generated.

- the `generate_hash_index` method is used to generate the hash index from files.
  It sets the result or the generated_hash_index to `self.hash_index`
  takes the paramter
  - `files`: files from which hash index should be generated.

### Properties

- `size_index`
      You can also access the size index using the property. it is a dictionary containing files
      grouped by their sizes.
- `hash_index`
      You can also access the hash index using this property. It is a dictionary containing files
      grouped by their secure hashes.
- `fetched_files`
      access all fetched files from the search path
- `path`
           where the search will be made, defaults to current directory.
- `recurse`
      boolean, set to true if you want it to recurse down to all files in the path including sub-dirs
      defaults to `False`

## Usage From Commandline

You can now use dupliCat from the command line.

   ```cli
   bash$ dupliCat --help
   ```

   the above code will help you to use it.

## Contact

### teddbug-S

- twitter: [teddbug](https://www.twitter.com/teddbug)
- facebook: [Tedd Bug](https://www.facebook.com/tedd.bug.79/)
- mail: etornam47@protonmail.com

### Kwieeciol

- mail: lukkwie456@gmail.com
- facebook: [Kwieeciol](https://www.facebook.com/profile.php?id=100043452014581)


😄 Happy Coding!
