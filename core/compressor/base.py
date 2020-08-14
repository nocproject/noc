# ----------------------------------------------------------------------
# BaseCompressor class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import io
from typing import Optional


class BaseCompressor(object):
    name = None
    # Default file extension
    ext = None

    def __init__(self, path: str, mode: str = "r"):
        self.path = path
        self.mode = mode
        self.f: Optional[io.TextIOBase] = None

    def __enter__(self):
        self.f = self.open()
        return self.f

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.f:
            self.close()
            self.f = None

    def open(self) -> io.TextIOBase:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError
