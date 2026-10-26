# ----------------------------------------------------------------------
# Compression utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections.abc import Callable

TCompressor = Callable[[bytes], bytes]
TDecompressor = Callable[[bytes], bytes]


def _dummy(x: bytes) -> bytes:
    return x


def get_compressor(name: str) -> TCompressor:
    if name == "zlib":
        # Python modules
        from zlib import compress

        return compress
    if name == "lzma":
        # Python modules
        from lzma import compress

        return compress
    return _dummy


def get_decompressor(name: str) -> TDecompressor:
    if name == "zlib":
        # Python modules
        from zlib import decompress

        return decompress
    if name == "lzma":
        # Python modules
        from lzma import decompress

        return decompress
    return _dummy
