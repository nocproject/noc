# ----------------------------------------------------------------------
# Compatibility routines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# NOC modules
from noc.core.typing import SupportsStr

DEFAULT_ENCODING = "utf-8"


def smart_bytes(s: bytes | str | SupportsStr, encoding: str = DEFAULT_ENCODING) -> bytes:
    """
    Convert strings to bytes when necessary
    """
    if isinstance(s, bytes):
        return s
    if isinstance(s, str):
        return s.encode(encoding)
    return str(s).encode(encoding)


def smart_text(
    s: str | bytes | SupportsStr, errors: str = "strict", encoding: str = DEFAULT_ENCODING
) -> str:
    """
    Convert bytes to string when necessary
    """
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        return s.decode(encoding, errors=errors)
    return str(s)
