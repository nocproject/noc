# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# IDNA utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.comp import smart_text, smart_bytes

IDNA_PREFIX = str("xn--")


def to_idna(zone: str) -> str:
    """
    Convert literal zone name to IDNA encoding
    :param zone:
    :return:
    """
    return smart_text(smart_text(zone).lower().encode("idna"))


def from_idna(zone: str) -> str:
    """
    Convert IDNA zone name representation to literal name
    :param self:
    :param s:
    :return:
    """
    if not is_idna(zone):
        return zone
    return smart_text(smart_bytes(zone).decode("idna"))


def is_idna(zone: str) -> bool:
    """
    Check if zone name is in IDNA representation
    :param zone:
    :return:
    """
    return IDNA_PREFIX in zone
