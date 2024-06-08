# ----------------------------------------------------------------------
# BI decorators
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import struct

# Third-party modules
from siphash24 import siphash24
import bson

# NOC modules
from noc.config import config
from noc.models import is_document
from noc.core.comp import smart_bytes

_ZEROx16 = b"\x00" * 16


def _get_siphash_seed():
    if not config.installation_id:
        # Plain bi_id space
        return _ZEROx16
    # Try to reach globally-unique space
    # Installation name is UUID, giving exact 16 bytes of seed
    import uuid

    return uuid.UUID(config.installation_id).bytes


SIPHASH_SEED = _get_siphash_seed()
BI_ID_FIELD = "bi_id"


def bi_hash(v):
    """
    Calculate BI hash from given value
    :param v:
    :return:
    """
    if not isinstance(v, str):
        v = str(v)
    bh = siphash24(smart_bytes(v), key=SIPHASH_SEED).digest()
    return int(struct.unpack("!Q", bh)[0] & 0x7FFFFFFFFFFFFFFF)


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
