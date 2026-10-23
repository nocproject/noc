# ----------------------------------------------------------------------
# LZMA compressor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import io
import lzma

# NOC modules
from .base import BaseCompressor


class LZMACompressor(BaseCompressor):
    name = "lzma"
    ext = ".xz"

    def open(self) -> io.TextIOBase:
        return io.TextIOWrapper(lzma.LZMAFile(self.path, self.mode))

    def close(self) -> None:
        self.f.close()
