# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fast hash function
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from csiphash import siphash24

SIPHASH_SEED = b"\x00" * 16


def hash_str(value):
    """
    Calculate integer hash of value

    :param value: String
    :return: Hashed string
    """
    return siphash24(SIPHASH_SEED, str(value))
