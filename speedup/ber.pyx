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


cdef inline char* _write_int(char* ptr, int v):
    if v < 0x80:  # 1 block
        ptr[0] = v
        return ptr + 1
    if v < (1 << 14):  # 2 blocks of 7 bits
        ptr[0] = ((v >> 7) & 0x7f) | 0x80
        ptr[1] = v & 0x7f
        return ptr + 2
    if v < (1 << 21):  # 3 blocks of 7 bits
        ptr[0] = ((v >> 14) & 0x7f) | 0x80
        ptr[1] = ((v >> 7) & 0x7f) | 0x80
        ptr[2] = v & 0x7f
        return ptr + 3
    if v < (1 << 28):  # 4 blocks
        ptr[0] = ((v >> 21) & 0x7f) | 0x80
        ptr[1] = ((v >> 14) & 0x7f) | 0x80
        ptr[2] = ((v >> 7) & 0x7f) | 0x80
        ptr[3] = v & 0x7f
        return ptr + 4
    # 5 blocks
    ptr[0] = ((v >> 28) & 0x7f) | 0x80
    ptr[1] = ((v >> 21) & 0x7f) | 0x80
    ptr[2] = ((v >> 14) & 0x7f) | 0x80
    ptr[3] = ((v >> 7) & 0x7f) | 0x80
    ptr[4] = v & 0x7f
    return ptr + 5


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
    cdef unsigned char *ptr = msg
    cdef unsigned char x
    cdef char[1024] out
    cdef char* o_ptr = out + 2
    cdef int l_msg = len(msg)

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
                o_ptr = _write_int(o_ptr, v)
            v = 0
        else:
            v = (v * 10) + (x - 0x30)
        ptr += 1
    if sn == 2:
        o_ptr = _write_int(o_ptr, v)
    # Write length
    out[1] = o_ptr - out - 2
    return out[:o_ptr - out]


cdef inline int _write_raw_int(char* ptr, int value):
    cdef int n = 0
    if value <= 0xFF:
        if value & 0x80:
            ptr[0] = 0
            ptr += 1
            n += 1
        ptr[0] = value
        return n + 1
    if value <= 0xFFFF:
        if value & 0x8000:
            ptr[0] = 0
            ptr += 1
            n += 1
        ptr[0] = (value >> 8) & 0xFF
        ptr[1] = value  & 0xFF
        return n + 2
    if value <= 0xFFFFFF:
        if value & 0x800000:
            ptr[0] = 0
            ptr += 1
            n += 1
        ptr[0] = (value >> 16) & 0xFF
        ptr[1] = (value >> 8) & 0xFF
        ptr[2] = value  & 0xFF
        return n + 3
    ptr[0] = (value >> 24) & 0xFF
    ptr[1] = (value >> 16) & 0xFF
    ptr[2] = (value >> 8) & 0xFF
    ptr[3] = value  & 0xFF
    return n + 4


def encode_int(int value):
    if value == 0:
        return bytes("\x02\x01\x00")
    cdef char[32] out
    cdef int n
    out[0] = 0x2  # Type
    if value > 0:
        if value <= 0x7f:
            out[1] = 1  # size
            out[2] = value
            return bytes(out[:3])
        n = _write_raw_int(out + 2, value)
        out[1] = n
        return bytes(out[:n + 2])
