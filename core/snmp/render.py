# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# display_hint render functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
from typing import Optional, Callable

# NOC modules
from noc.core.comp import smart_text, bord


def render_bin(oid, value):
    # type: (six.text_type, six.binary_type) -> six.binary_type
    """
    Render raw binary
    :param oid:
    :param value:
    :return:
    """
    return value


def render_utf8(oid, value):
    # type: (six.text_type, six.binary_type) -> six.text_type
    """
    Render as UTF-8 text. Ignore errors
    :param oid:
    :param value:
    :return:
    """
    return smart_text(value, errors="ignore")


def get_text_renderer(encoding="utf-8"):
    # type: (Optional[six.text_type]) -> Callable[[six.text_type, six.binary_type], six.text_type]
    """
    Return text renderer for arbitrary encoding
    :param encoding:
    :return:
    """

    def renderer(oid, value):
        return smart_text(value, errors="ignore", encoding=encoding)

    return renderer


def render_empty(oid, value):
    # type: (six.text_type, six.binary_type) -> six.text_type
    """
    Always render empty string
    :param oid:
    :param value:
    :return:
    """
    return ""


def render_mac(oid, value):
    # type: (six.text_type, six.binary_type) -> six.text_type
    """
    Render 6 octets as MAC address. Render empty string on length mismatch
    :param oid:
    :param value:
    :return:
    """
    if len(value) != 6:
        return ""
    return "%02X:%02X:%02X:%02X:%02X:%02X" % tuple(bord(x) for x in value)


def get_string_renderer(v):
    # type: (six.text_type) -> Callable[[six.text_type, six.binary_type], six.text_type]
    """
    Always renders arbitrary string
    :param v:
    :return:
    """

    def renderer(oid, value):
        return v

    return renderer
