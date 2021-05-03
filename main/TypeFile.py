from dataclasses import dataclass
from os import PathLike


@dataclass
class File:
    """ A dataclass of keeping all needed info about a file """
    name: str
    size: int
    root: PathLike
    secure_hash: str

    def __gt__(self, other):
        return self.size > other.size or self.name > other.name

    def __lt__(self, other):
        return self.size < other.size or self.name > other.name

    def __eq__(self, other):
        return self.size == other.size or self.secure_hash == other.secure_hash

    def __ne__(self, other):
        return self.size != other.size or self.secure_hash != other.secure_hash