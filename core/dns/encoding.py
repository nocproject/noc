# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# IDNA utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six

# NOC modules
from noc.core.comp import smart_text, smart_bytes

IDNA_PREFIX = six.text_type("xn--")


def to_idna(zone):
    # type: (six.text_type) -> six.text_type
    """
    Convert literal zone name to IDNA encoding
    :param zone:
    :return:
    """
    return smart_text(smart_text(zone).lower().encode("idna"))


def from_idna(zone):
    # type: (six.text_type) -> six.text_type
    """
    Convert IDNA zone name representation to literal name
    :param self:
    :param s:
    :return:
    """
    if not is_idna(zone):
        return zone
    return smart_text(smart_bytes(zone).decode("idna"))


def is_idna(zone):
    # type: (six.text_type) -> bool
    """
    Check if zone name is in IDNA representation
    :param zone:
    :return:
    """
    return IDNA_PREFIX in zone
