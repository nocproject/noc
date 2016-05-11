# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ASN.1 BER utitities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from libc.stdio cimport snprintf

def parse_p_oid(bytes msg):
    """
    >>> BERDecoder().parse_p_oid("+\\x06\\x01\\x02\\x01\\x01\\x05\\x00")
    "1.3.6.1.2.1.1.5.0"
    """
    cdef unsigned int b, i
    cdef char v
    cdef char[1024] out
    cdef char* ptr, o_ptr

    ptr = msg
    optr = out
    if ptr[0] == "+":
        optr += snprintf(optr, 1024 - (optr - out), "1.3")
    else:
        optr += snprintf(
            optr,
            1024 - (optr - out),
            "%d.%d",
            ptr[0] // 40,
            ptr[0] % 40
        )
    ptr += 1
    b = 0
    for i in range(1, len(msg)):
        v = ptr[0]
        ptr += 1
        b = (b << 7) + (v & 0x7f)
        if not (v & 0x80):
            optr += snprintf(optr, 1024 - (optr - out), ".%d", b)
            b = 0
    return out
