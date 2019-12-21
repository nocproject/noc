# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# SNMP utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# Third-party modules
import six
from typing import Any, Optional

# NOC modules
from noc.core.comp import smart_text


rx_os_format = re.compile(
    r"(?P<repeat>[*]?)"
    r"(?P<size>\d+)"
    r"(?P<format>[xdoat])"
    r"(?P<dsep>[^*0-9]?)"
    r"(?P<rt>[^*0-9]?)"
)


def render_tc(value, base_type, format=None):
    # type: (Any, six.text_type, Optional[six.text_type]) -> six.text_type
    """
    Render SNMP TC using DISPLAY-HINT according to RFC 2579

    :param value: Binary string
    :param base_type: Basic SNMP TC Type
    :param format: Optional format string (DISPLAY-HINT)
    """
    if format is None:
        # if base_type == "OctetString":
        #    # Apply default formatting for octet strings
        #    if len(value) == 4:
        #        # Format as IPv4 address
        #        return ".".join([str(ord(c)) for c in value])
        return str(value)
    if base_type == "Integer32":
        if format == "x":
            # Hexadecimal
            return "%x" % value
        elif format == "o":
            # Octal
            return "%o" % value
        elif format == "b":
            # Binart
            pass
        elif format == "d":
            return str(value)
        elif format and format.startswith("d"):
            if format[1] == "-":
                p = int(format[2:])
                v = str(value)
                if len(v) <= p:
                    v = "0" * (p - len(v) + 1) + v
                return "%s.%s" % (v[:-p], v[-p:])
    elif base_type == "OctetString":
        value = [ord(c) for c in value]
        r = ""
        while value:
            for match in rx_os_format.finditer(format):
                if not value:
                    break
                repeat, size, fmt, dsep, rt = match.groups()
                if repeat and rt:
                    dsep = ""
                size = int(size)
                if repeat:
                    repeat = value.pop(0)
                else:
                    repeat = 1
                rr = []
                for i in range(repeat):
                    if not value:
                        break
                    if fmt == "a":
                        rr += [chr(v) for v in value[:size]]
                        value = value[size:]
                    elif fmt == "t":
                        s = "".join([chr(v) for v in value[:size]])
                        value = value[size:]
                        rr += [smart_text(s, errors="ignore")]
                    else:
                        v = 0
                        for j in range(size):
                            v = (v << 8) + value.pop(0)
                        if fmt == "x":
                            rr += ["%02x" % v]
                        elif fmt == "d":
                            rr += ["%d" % v]
                        elif fmt == "o":
                            rr += ["%03o" % v]
                        else:
                            raise ValueError("Unknown format: %s" % fmt)
                # Join with repeat separator
                r += rt.join(rr)
                #
                if value and dsep:
                    r += dsep
        return r
    return smart_text(value, errors="ignore")
