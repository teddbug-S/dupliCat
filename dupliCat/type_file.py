# MIT License

# Copyright (c) 2022 Divine Darkey

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os


class File:
    """ A class of keeping all needed info about a file """

    def __init__(self, name, root, size, secure_hash) -> None:
        self.name = name # basename of the file
        self.root = root # the root dir of the file
        self.size = size # size of the file
        self.secure_hash = secure_hash # secure hash generated from first 1024 bytes read 
    
    def delete(self) -> None:
        """Deletes this file from the system"""
        os.remove(os.path.join(self.root, self.name))
    
    def __repr__(self) -> str:
        """represents `repr(File)`"""
        return f"File(name={self.name!r}, root={self.root!r}, size={self.size}, secure_hash={self.secure_hash!r})"
    
    def __str__(self) -> str:
        """represents `str(File)`"""
        return f"File(name={self.name!r}, root={self.root!r}, size={self.size}, secure_hash={self.secure_hash!r})"

    def __gt__(self, other):
        return self.size > other.size or self.name > other.name

    def __lt__(self, other):
        return self.size < other.size or self.name > other.name

    def __eq__(self, other):
        return self.size == other.size or self.secure_hash == other.secure_hash

    def __ne__(self, other):
        return self.size != other.size or self.secure_hash != other.secure_hash