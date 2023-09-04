# ----------------------------------------------------------------------
# display_hint render functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import Optional, Callable

# NOC modules
from noc.core.comp import smart_text


def render_bin(oid: str, value: bytes) -> bytes:
    """
    Render raw binary
    :param oid:
    :param value:
    :return:
    """
    return value


def render_utf8(oid: str, value: bytes) -> str:
    """
    Render as UTF-8 text. Ignore errors
    :param oid:
    :param value:
    :return:
    """
    return smart_text(value, errors="ignore")


def get_text_renderer(encoding: Optional[str] = "utf-8") -> Callable[[str, bytes], str]:
    """
    Return text renderer for arbitrary encoding
    :param encoding:
    :return:
    """

    def renderer(oid, value):
        return smart_text(value, errors="ignore", encoding=encoding)

    return renderer


def render_empty(oid: str, value: bytes) -> str:
    """
    Always render empty string
    :param oid:
    :param value:
    :return:
    """
    return ""


def render_mac(oid: str, value: bytes) -> str:
    """
    Render 6 octets as MAC address. Render empty string on length mismatch
    :param oid:
    :param value:
    :return:
    """
    if len(value) != 6:
        return ""
    return "%02X:%02X:%02X:%02X:%02X:%02X" % tuple(value)


def render_IPV6(oid: str, value: bytes) -> str:
    """
    Render 16 octets as ip address V6. Render empty string on length mismatch
    :param oid:
    :param value:
    :return:
    """
    if len(value) != 16:
        return ""
    return "%02X%02X:%02X%02X:%02X%02X:%02X%02X:%02X%02X:%02X%02X:%02X%02X:%02X%02X" % tuple(value)


def get_string_renderer(v: str) -> Callable[[str, bytes], str]:
    """
    Always renders arbitrary string
    :param v:
    :return:
    """

    def renderer(oid, value):
        return v

    return renderer
