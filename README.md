# DupliCat

A simple utility for finding duplicated files within a specified path.
It is intended to be a library but can also be used as a commandline tool,
it doesn't delete the duplicate files found but returns a list of junk files
you can choose to delete yourself.

# Usage As A Library:
   - Import the [DuplicateFinder](https://github.com/teddbug-S/DupliCat/blob/main/main/DuplicateFinder.py) class and create an object by passing the following arguments,
       - `path`
           where the search will be made, defaults to current directory.
       - `recurse`
           boolean, set to true if you want it to recurse down to all files in the path including sub-dirs
           defaults to `False`
       - `by_hash`
           find duplicates using hash table if set to True otherwise uses size_table, using the 
           hash_table is more accurate in conditions where different files have same sizes
           and quite fast since table is generated using the size table, parameter defaults to `True`.
           Using the size table is more faster but does not guarrantee accuracy.
           
    NOTE: We recommend you use the hash table to avoid lose of data or important files.
  
   - call the `search_duplicate` method to begin the 🔍 search, search results will be stored in 
       the `junk_files` property of the class. This method is somewhat the main api of the class, it 
       does everything for you, calling other methods instead of this when you want to conduct a search will
       definitely break something.
   
   - call the `silent_search` method if you want a silent search and nothing printed out.
       This calls `search_duplicate` behind the scenes and suppresses it's output.
    
    NOTE: Junk files set by this method contains all duplicates which can safely be deleted without 
    worrying about an original copy for each.
 
   - use the `analysis` property for analysis on the search made, this returns a named tuple containing 
       the total number of duplicate files accessed through `analysis.total_count`, their total size on the disk
       accessed through `analysis.total_size` and the most occurred file, accessed through `analysis.most_occurrence`.

   - You can also access the size table using the `size_table` property of the class and hash table by `hash_table` 
     property.
     

# Usage From Commandline
   - run the class on 💻 commandline and pass it `-h` flag, this will definitely see you through!

# Contact
   - twitter  : teddbug
   - facebook: Tedd Bug

😄 Happy Coding!
