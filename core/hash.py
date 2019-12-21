# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fast hash function
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import struct

# Third-party modules
from csiphash import siphash24
from typing import Dict, Any
import six

# NOC modules
from noc.core.comp import smart_text, smart_bytes

SIPHASH_SEED = b"\x00" * 16
hash_fmt = struct.Struct("!q")


def hash_str(value):
    """
    Calculate integer hash of value

    :param value: String
    :return: Hashed string
    """
    return siphash24(SIPHASH_SEED, smart_bytes(smart_text(value)))


def hash_int(value):
    return hash_fmt.unpack(hash_str(value))


def dict_hash_int(d):
    # type: (Dict[six.text_type, Any]) -> int
    r = ["%s=%s" % (k, d[k]) for k in sorted(d)]
    return hash_int(",".join(r))
