# ----------------------------------------------------------------------
# ACL Address Checking implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import socket
import struct


def _iter_pairs(prefixes):
    """
    Yield tuples of first, last addresses as integer
    :param prefixes: Iterable of IPv4 prefixes
    :return: yield (first, last)
    """
    for prefix in prefixes:
        p, mask = prefix.split("/")
        p = struct.unpack("!L", socket.inet_aton(p))[0]
        mask = int(mask)
        p_mask = ((1 << mask) - 1) << (32 - mask)
        b_mask = 0xFFFFFFFF ^ p_mask
        yield p & p_mask, p | b_mask


def match(prefixes, ip):
    """
    Check if ip is match against ACL
    :param prefixes: Iterable of IPv4 prefixes
    :param ip: IPv4 address
    :return: True if ip is in prefixes
    """
    a = struct.unpack("!L", socket.inet_aton(ip))[0]
    return any(f <= a <= l for f, l in _iter_pairs(prefixes))
