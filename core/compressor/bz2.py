# ----------------------------------------------------------------------
# BZipCompressor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import io
import bz2

# NOC modules
from .base import BaseCompressor


class GZipCompressor(BaseCompressor):
    name = "bz2"
    ext = ".bz2"

    def open(self) -> io.TextIOBase:
        return io.TextIOWrapper(bz2.BZ2File(self.path, self.mode))

    def close(self) -> None:
        self.f.close()
