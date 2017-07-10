# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# IP Packets handling utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from libc.string cimport memcpy, memset


def get_checksum(bytes msg):
    cdef unsigned int cs, i, lm, l, ll
    cdef unsigned char* ptr

    cs = 0
    ptr = msg
    l = len(msg)
    ll = l // 2
    for i in range(ll):
        cs += (ptr[0] << 8) + ptr[1]
        ptr += 2
    if ll * 2 < l:
        cs += ptr[0]
    # Truncate to 32 bits
    cs &= 0xFFFFFFFF
    # Fold 32 bits to 16 bits
    cs = (cs >> 16) + (cs & 0xFFFF)  # Add high 16 bits to low 16 bits
    cs += (cs >> 16)
    return ~cs & 0xFFFF


def build_icmp_echo_request(int request_id, int seq, bytes payload):
    cdef unsigned char[65536] out
    cdef unsigned int cs, i, lm, l, ll, lp
    cdef unsigned char* ptr
    cdef unsigned char* pl
    # ICMP Type
    out[0] = 8
    out[1] = 0
    # Checksum
    out[2] = 0
    out[3] = 0
    # Request ID
    out[4] = (request_id >> 8) & 0xFF
    out[5] = request_id & 0xFF
    # Sequence
    out[6] = (seq >> 8) & 0xFF
    out[7] = seq & 0xFF
    # Payload
    pl = payload
    lp = len(payload)
    memcpy(out + 8, pl, lp)
    # Get checksum
    cs = 0
    ptr = out
    l = len(payload) + 8
    ll = l // 2
    for i in range(ll):
        cs += (ptr[0] << 8) + ptr[1]
        ptr += 2
    if ll * 2 < l:
        cs += ptr[0]
    # Truncate to 32 bits
    cs &= 0xFFFFFFFF
    # Fold 32 bits to 16 bits
    cs = (cs >> 16) + (cs & 0xFFFF)  # Add high 16 bits to low 16 bits
    cs += (cs >> 16)
    cs = ~cs & 0xFFFF
    # Write checksum
    out[2] = (cs >> 8) & 0xFF
    out[3] = cs & 0xFF
    return bytes(out[:8 + lp])
