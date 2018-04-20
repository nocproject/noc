# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STOMP PDU encoder/decoder
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.serialize import json_encode

VERSION = "1.1"


def stomp_escape_value(s):
    """
    Escape arbitrary string to STOMP header value

    >>> stomp_escape_value("the string")
    'the string'
    >>> stomp_escape_value("the string:\\test")
    'the string\\\\c\\test'

    :param s:
    :return:
    :rtype: str
    """
    return str(s).replace("\\", "\\\\").replace(":", "\\c")\
        .replace("\n", "\\n")


def stomp_unescape_value(s):
    """
    Unescape arbitrary string from STOMP
    :param s:
    :return:
    """
    return s.replace("\\n", "\n").replace("\\c", ":")\
        .replace("\\\\", "\\")


def stomp_parse_frame(s):
    """
    Parse STOMP frame

    COMMAND
    header1:value1
    header2:value2

    BODY

    :param s:
    :return:
    """
    f = s.split("\n")
    if len(f) < 2:
        raise ValueError("STOMP Frame too short")
    cmd = f[0]
    headers = {}
    try:
        idx = f.index("")
    except ValueError:
        raise ValueError("Invalid STOMP frame")
    # Parse headers
    for h in f[1: idx]:
        l, r = h.split(":", 1)
        if l not in headers:
            headers[l] = stomp_unescape_value(r)
    # Parse body
    body = "\n".join(f[idx + 1:])
    return cmd, headers, body


def stomp_build_frame(cmd, headers=None, body=""):
    headers = headers or {}
    # Set content-type
    if "content-type" not in headers:
        if isinstance(body, basestring):
            headers["content-type"] = "text/plain"
        else:
            headers["content-type"] = "text/json"
    # Serialize body
    if not isinstance(body, basestring):
        body = json_encode(body)
    # Set content-length
    if "content-length" not in headers:
        headers["content-length"] = len(body)
    # Escape headers
    h = "\n".join("%s:%s" % (k, stomp_escape_value(headers[k]))
        for k in headers)
    return "%s\n%s\n\n%s\x00" % (cmd, h, body)
