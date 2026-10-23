# ----------------------------------------------------------------------
# Fast hash function
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import struct
from typing import Any

# Third-party modules
from siphash24 import siphash24
from bson import ObjectId


# NOC modules
from noc.core.comp import smart_text

SIPHASH_SEED = b"\x00" * 16
hash_fmt = struct.Struct("!q")


def hash_str(value: str | ObjectId | int) -> bytes:
    """Calculate SipHash digest for a value.

    The value is converted to a string representation before hashing.
    The function returns the raw 64-bit hash digest.

    Args:
        value: Value to calculate the hash for.

    Returns:
        Raw hash digest as bytes.
    """
    return siphash24(smart_text(value).encode(), key=SIPHASH_SEED).digest()


def hash_int(value: str | ObjectId | int) -> int:
    """Calculate integer hash for a value.

    The SipHash digest is converted into a signed 64-bit integer.

    Args:
        value: Value to calculate the hash for.

    Returns:
        Hash value as an integer.
    """
    return hash_fmt.unpack(hash_str(value))[0]


def dict_hash_int(d: dict[str, Any]) -> int:
    """Calculate deterministic integer hash for a dictionary.

    Dictionary keys are sorted before hashing to ensure that dictionaries
    with the same content produce the same hash regardless of key order.

    Args:
        d: Dictionary to calculate the hash for.

    Returns:
        Hash value as an integer.
    """
    r = [f"{k}={d[k]}" for k in sorted(d)]
    return hash_int(",".join(r))


def dict_hash_int_args(**kwargs: Any) -> int:
    """Calculate deterministic integer hash for keyword arguments.

    This is a convenience wrapper around :func:`dict_hash_int`.

    Args:
        **kwargs: Values to include in the hash calculation.

    Returns:
        Hash value as an integer.
    """
    return dict_hash_int(kwargs)
