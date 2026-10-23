# ----------------------------------------------------------------------
# IDNA utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.comp import smart_text, smart_bytes

IDNA_PREFIX = "xn--"


def to_idna(zone: str) -> str:
    """
    Convert literal zone name to IDNA encoding
    :return:
    """
    return smart_text(smart_text(zone).lower().encode("idna"))


def from_idna(zone: str) -> str:
    """
    Convert IDNA zone name representation to literal name
    :return:
    """
    if not is_idna(zone):
        return zone
    return smart_text(smart_bytes(zone).decode("idna"))


def is_idna(zone: str) -> bool:
    """
    Check if zone name is in IDNA representation
    :return:
    """
    return IDNA_PREFIX in zone
