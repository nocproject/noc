# ----------------------------------------------------------------------
# Fast hash function
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import struct

# Third-party modules
from siphash24 import siphash24
from typing import Dict, Any

# NOC modules
from noc.core.comp import smart_text, smart_bytes

SIPHASH_SEED = b"\x00" * 16
hash_fmt = struct.Struct("!q")


def hash_str(value: Any) -> str:
    """
    Calculate integer hash of value

    :param value: String
    :return: Hashed string
    """
    return siphash24(smart_bytes(smart_text(value)), key=SIPHASH_SEED).digest()


def hash_int(value: Any) -> int:
    return hash_fmt.unpack(hash_str(value))[0]


def dict_hash_int(d: Dict[str, Any]) -> int:
    r = ["%s=%s" % (k, d[k]) for k in sorted(d)]
    return hash_int(",".join(r))


def dict_hash_int_args(**kwargs):
    return dict_hash_int(kwargs)
