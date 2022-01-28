from finder import DupliCat

path = "/home/teddbug/Pictures"


finder_ = DupliCat(path, recurse=True)
finder_.search_duplicate()


for file_ in finder_.junk_files:
    print(file_.name)
