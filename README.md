# DupliCat

A simple utility for finding duplicated files within a specified path.
It is intended to be a library but can also be used as a commandline tool,
it doesn't delete the duplicate files found but returns a list of junk files so that you can choose the ones to delete.

# Usage As A Library:
   - Import the [dupliCat](https://github.com/teddbug-S/dupliCat/blob/main/dupliCat/duplicat.py) class and create an object by passing the following arguments,
       - `path`
           where the search will be made, defaults to current directory.
       - `recurse`
           boolean, set to true if you want it to recurse down to all files in the path including sub-dirs
           defaults to `False`
       <!-- - `by_hash`
           find duplicates using hash table if set to True otherwise uses size_table, using the 
           hash_table is more accurate in conditions where different files have same sizes
           and quite fast since table is generated using the size table, parameter defaults to `True`.
           Using the size table is more faster but does not guarrantee accuracy.
            -->
    <!-- NOTE: We recommend you use the hash table to avoid lose of data or important files. -->
  
   - call the `search_duplicate` method to begin the 🔍 search, search results will be stored in 
       the `duplicates` property of the class. This method is somewhat the main api of the class, it 
       does everything for you, calling other methods instead of this might remove the functionality of
       using files from `size_index` as input for generating a hash index.
   
   <!-- - call the `silent_search` method if you want a silent search and nothing printed out.
       This calls `search_duplicate` behind the scenes and suppresses it's output. -->
    
    NOTE: Junk files set by this method contains all duplicates with one file left over for each.
 
   - use the `analyse` method to analyse search result, this returns a named tuple of type `Analysis`.
   It contains 
       the total number of duplicate files accessed through `analysis.total_file_num`, their total size on the disk
       accessed through `analysis.total_size` and the most occurred file, accessed through `analysis.most_occurrence`.

   - You can also access the size index using the `size_index` property of the class and hash index by `hash_index` property.
     

# Usage From Commandline
   Functionality removed for now.

# Contact
   - twitter  : [teddbug](!https://www.twitter.com/teddbug)
   - facebook: [Tedd Bug](!https://www.facebook.com/tedd.bug.79/)

😄 Happy Coding!
