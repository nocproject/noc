# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ASN.1 BER utitities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from libc.stdio cimport snprintf


def parse_tlv_header(bytes msg):
    """
    Parse TLV header
    :returns decoder_id, tag_class, tag_id, is_primitive, is implicit, offset, length
    """
    cdef unsigned char* ptr
    cdef unsigned char v, c
    cdef int tag_class, tag_id, i, skip, l, tl, decoder_id
    cdef bint is_constructed, is_implicit

    ptr = msg
    v = ptr[0]
    # 0xc0 == 11000000
    tag_class = v & 0xc0
    # 0x20 == 00100000
    is_constructed = bool(v & 0x20)
    #
    is_implicit = False
    # 0x1f == 00011111
    tag_id = v & 0x1f
    # e0 == 11100000
    # (tag_class | is_constructed) >> 5
    decoder_id = (v & 0xe0) >> 5
    #
    skip = 1
    if tag_id == 0x1f:
        # high-tag number form
        tag_id = 0
        while True:
            c = ptr[skip]
            skip += 1
            tag_id = (tag_id << 7) + (c & 0x7f)
            if not (c & 0x80):
                break
    elif v & 0x80:
        # Implicit types
        tag_class = 0
        if not is_constructed and ptr[1] == 0:
            tag_id = 5
        else:
            is_implicit = True
        # Recalculate decoder_id
        if is_constructed:
            decoder_id = 1
        else:
            decoder_id = 0
    # Parse length
    l = ptr[skip]
    skip += 1
    if l & 0x80:
        # Long form
        tl = l & 0x7f
        l = 0
        while tl:
            l = (l << 8) + ptr[skip]
            skip += 1
            tl -= 1
    # Apply tag_id to decoder id
    decoder_id = decoder_id | (tag_id << 3)
    #
    return decoder_id, tag_class, tag_id, is_constructed, is_implicit, skip, l


def parse_p_oid(bytes msg):
    """
    >>> BERDecoder().parse_p_oid("+\\x06\\x01\\x02\\x01\\x01\\x05\\x00")
    "1.3.6.1.2.1.1.5.0"
    """
    cdef unsigned int b, i
    cdef unsigned char v
    cdef char[1024] out
    cdef char* ptr
    cdef char* o_ptr
    cdef int l_msg = len(msg)

    ptr = msg
    o_ptr = out
    if ptr[0] == "+":
        o_ptr += snprintf(o_ptr, 1024 - (o_ptr - out), "1.3")
    else:
        o_ptr += snprintf(
            o_ptr,
            1024 - (o_ptr - out),
            "%u.%u",
            <unsigned int>(ptr[0] // 40),
            <unsigned int>(ptr[0] % 40)
        )
    ptr += 1
    b = 0
    for i in range(1, l_msg):
        v = ptr[0]
        ptr += 1
        b = (b << 7) + (v & 0x7f)
        if not (v & 0x80):
            o_ptr += snprintf(o_ptr, 1024 - (o_ptr - out), ".%u", b)
            b = 0
    return out


def encode_oid(bytes msg):
    """
    >>> BEREncoder().encode_oid("1.3.6.1.2.1.1.5.0")
    '\\x06\\x08+\\x06\\x01\\x02\\x01\\x01\\x05\\x00'

    :param msg:
    :return:
    """
    cdef int v = 0
    cdef int nv = 0
    cdef int sn = 0
    cdef char x
    cdef char *ptr = msg
    cdef char[1024] out
    cdef char* o_ptr = out + 2
    cdef l_msg = len(msg)

    out[0] = 0x6  # OID primitive
    # out[1] should be length
    for _ in range(l_msg):
        x = ptr[0]
        if x < 0x30 or x > 0x39:
            if sn == 0:
                nv = v
                sn = 1
            elif sn == 1:
                o_ptr[0] = nv * 40 + v
                o_ptr += 1
                sn = 2
            else:
                while v > 0x7f:
                    o_ptr[0] = (v & 0x7f) | 0x80
                    o_ptr += 1
                    v >>= 7
                o_ptr[0] = v
                o_ptr += 1
            v = 0
        else:
            v = (v << 8) + (x - 0x30)
        ptr += 1
    if sn == 2:
        o_ptr[0] = v
    # Write length
    out[1] = o_ptr - out - 1
    return bytes(out[:o_ptr - out + 1])
