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
import bson
# NOC modules
from noc.models import is_document

SIPHASH_SEED = b"\x00" * 16
BI_ID_FIELD = "bi_id"


def bi_hash(v):
    """
    Calculate BI hash from given value
    :param v:
    :return:
    """
    bh = siphash24(SIPHASH_SEED, str(v))
    return int(struct.unpack("!Q", bh)[0] & 0x7fffffffffffffff)


def new_bi_id():
    """
    Generate new bi_id
    :return:
    """
    return bi_hash(bson.ObjectId())


def bi_sync(cls):
    """
    Denote class to add bi_id defaults
    :param cls:
    :return:
    """
    if is_document(cls):
        f = cls._fields.get(BI_ID_FIELD)
        assert f, "%s field must be defined" % BI_ID_FIELD
    else:
        f = [f for f in cls._meta.fields if f.name == BI_ID_FIELD]
        assert f, "%s field must be defined" % BI_ID_FIELD
        f = f[0]
    f.default = new_bi_id
    return cls
