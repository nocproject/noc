# ----------------------------------------------------------------------
# BI decorators
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
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
from noc.core.typing import SupportsStr

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
BI_HASH_MASK = 0x7FFFFFFFFFFFFFFF


def bi_hash(v: str | SupportsStr) -> int:
    """
    Calculate a stable BI hash value for the given object.

    The object is converted to its string representation and mapped to a
    fixed-size integer hash value. Objects with the same string
    representation produce the same hash value.

    Args:
        v: Object to hash. Must be a string or provide a string representation
            via `__str__`.

    Returns:
        Stable integer hash value limited to the BI hash range.
    """
    if not isinstance(v, str):
        v = str(v)
    bh = siphash24(v.encode(), key=SIPHASH_SEED).digest()
    return int(struct.unpack("!Q", bh)[0] & BI_HASH_MASK)


def new_bi_id() -> int:
    """
    Generate a new BI identifier.

    A unique ObjectId is converted into a stable BI hash value to produce
    a compact integer identifier.

    Returns:
        New BI identifier.
    """
    return bi_hash(bson.ObjectId())


def bi_sync(cls):
    """
    Denote class to add bi_id defaults
    :return:
    """
    if is_document(cls):
        f = cls._fields.get(BI_ID_FIELD)
        assert f, f"{BI_ID_FIELD} field must be defined"
    else:
        f = [f for f in cls._meta.fields if f.name == BI_ID_FIELD]
        assert f, f"{BI_ID_FIELD} field must be defined"
        f = f[0]
    f.default = new_bi_id
    return cls
