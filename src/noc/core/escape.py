# ---------------------------------------------------------------------
# Escape/unescape to various encodings
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import binascii

# NOC modules
from noc.core.comp import smart_bytes, smart_text


def json_escape(s: str | bool | None) -> str:
    """
    Escape a value for safe inclusion into a JSON string.

    Args:
        s: String value to escape. ``bool`` values are converted to JSON
            literals (``"true"`` or ``"false"``), while ``None`` is
            converted to an empty string.

    Returns:
        Escaped string representation of the value.
    """
    if isinstance(s, bool):
        return "true" if s else "false"
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def fm_escape(s) -> str:
    """
    Escape binary FM data to string
    """
    return smart_text(binascii.b2a_qp(smart_bytes(s)).replace(b"=\n", b""))


def fm_unescape(s) -> bytes:
    """
    Decode escaped FM data to a raw string
    'ab\\xffcd'
    """
    return binascii.a2b_qp(smart_bytes(s))
