# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BI decorators
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import struct
# Third-party modules
from csiphash import siphash24

SIPHASH_SEED = b"\x00" * 16


def get_bi_id(self):
    """
    Returns BI id
    :param self: 
    :return: 
    """
    if not self.bi_id:
        h = getattr(self, "_bi_id", None)
        if not h:
            bh = siphash24(SIPHASH_SEED, str(self.id))
            h = struct.unpack("!Q", bh)[0]
            self._bi_id = h
        return h
    else:
        return self.bi_id


def bi_sync(cls):
    """
    Denote class 
    :param cls: 
    :return: 
    """
    setattr(cls, "get_bi_id", get_bi_id)
    return cls
