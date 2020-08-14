# ----------------------------------------------------------------------
# Plain compressor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import io

# NOC modules
from .base import BaseCompressor


class PlainCompressor(BaseCompressor):
    name = "plain"
    ext = ""

    def open(self) -> io.TextIOBase:
        return open(self.path, self.mode)

    def close(self) -> None:
        self.f.close()
