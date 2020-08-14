# ----------------------------------------------------------------------
# GZip compressor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import io
import gzip

# NOC modules
from .base import BaseCompressor


class GZipCompressor(BaseCompressor):
    name = "gzip"
    ext = ".gz"

    def open(self) -> io.TextIOBase:
        return io.TextIOWrapper(gzip.GzipFile(self.path, self.mode))

    def close(self) -> None:
        self.f.close()
