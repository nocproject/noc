# ----------------------------------------------------------------------
# Compression utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Callable

TCompressor = Callable[[bytes], bytes]
TDecompressor = Callable[[bytes], bytes]


def _dummy(x: bytes) -> bytes:
    return x


def get_compressor(name: str) -> TCompressor:
    if name == "zlib":
        from zlib import compress

        return compress
    if name == "lzma":
        from lzma import compress

        return compress
    return _dummy


def get_decompressor(name: str) -> TDecompressor:
    if name == "zlib":
        from zlib import decompress

        return decompress
    if name == "lzma":
        from lzma import decompress

        return decompress
    return _dummy
