from os import devnull, path
from .TypeFile import File
from contextlib import redirect_stdout
from collections import namedtuple
from hashlib import blake2b


def silent(callback):
    def wrapper(*args, **kwargs):
        with open(devnull, 'w') as f:
            with redirect_stdout(f):
                callback(*args, **kwargs)

    return wrapper


def human_size(nbytes_) -> str:
    """
    Converts bytes to a human readable size

        print(_human_size(2024)) # -> 1.98 KB
    """
    suffixes = ["B", "KB", "MB", "GB", "TB", "PT"]
    index = 0
    while nbytes_ >= 1024 and index < len(suffixes) - 1:
        nbytes_ /= 1024
        index += 1
    size = round(nbytes_, 2)
    return f"{size:,} {suffixes[index]}"


def read_chunk(file: File, size) -> bytes:
    """ Reads first [size] chunks from file, size defaults to 400 """
    file = path.join(file.root, file.name)  # get full path of file
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
