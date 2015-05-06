# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Common SSH utilities
## Based upon twisted.conch.ssh code
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import struct
import os
from hashlib import sha1
import logging
## Third-party modules
from Crypto.Util.number import bytes_to_long, long_to_bytes


def secure_random(bytes):
    return os.urandom(bytes)


def NS(s):
    """
    Generate string representation
    """
    s = str(s)
    return struct.pack("!L", len(s)) + s


def get_NS(s, count=1):
    """
    Extract *count* strings from stream
    and return s1, ..., sN, rest
    """
    c = 0
    while s and c < count:
        l, = struct.unpack("!L", s[:4])
        yield s[4:4 + l]
        s = s[4 + l:]
        c += 1
    yield s


def _MP(number):
    """
    Generate arbitrary precision representation
    """
    if number == 0:
        return "\x00\x00\x00\x00"
    assert number > 0
    bn = long_to_bytes(number)
    if ord(bn[0]) & 128:
        bn = "\x00" + bn
    return struct.pack(">L", len(bn)) + bn


def _MPpow(x, y, z):
    return MP(pow(x, y, z))


def _get_MP(s, count=1):
    c = 0
    while s and c < count:
        l, = struct.unpack(">L", s[:4])
        yield bytes_to_long(s[4:4 + l])
        s = s[4 + l:]
        c += 1
    yield s


def pkcs1_digest(data, message_len):
    d = ID_SHA1 + sha1(data).digest()
    pad_len = message_len - 2 - len(d)
    return "\x01" + ("\xff" * pad_len) + "\x00" + d


def _gmpy_get_MP(data, count=1):
    """
    gmpy version of get_MP
    """
    mp = []
    c = 0
    for i in range(count):
        length = struct.unpack('!L', data[c:c + 4])[0]
        mp.append(long(
            gmpy.mpz(data[c + 4:c + 4 + length][::-1] + '\x00', 256)))
        c += length + 4
    return tuple(mp) + (data[c:],)


def _gmpy_MP(i):
    """
    gmpy version of MP
    """
    i2 = gmpy.mpz(i).binary()[::-1]
    return struct.pack("!L", len(i2)) + i2


def _gmpy_MPpow(x, y, z=None):
    """
    gmpy version of MPpow
    """
    r = py_pow(gmpy.mpz(x), y, z).binary()[::-1]
    return struct.pack('!L', len(r)) + r


def _gmpy_pow(x, y, z=None):
    """
    gmpy version of pow
    """
    return py_pow(gmpy.mpz(x), y, z)

##
ID_SHA1 = "\x30\x21\x30\x09\x06\x05\x2b\x0e\x03\x02\x1a\x05\x00\x04\x14"

## Save system pow
py_pow = pow

# Will be set by install functions
get_MP = None
MP = None
MPpow = None

## Install gmp-less implementations
def install():
    global get_MP, MP, MPpow
    logging.info("SSH: gmpy not found. Using python implementation")
    get_MP = _get_MP
    MP = _MP
    MPpow = _MPpow


## Install gmpy-accelerated functions
def install_gmpy():
    global get_MP, MP, MPpow
    logging.info("SSH: Using gmpy")
    get_MP = _gmpy_get_MP
    MP = _gmpy_MP
    MPpow = _gmpy_MPpow
    __builtins__["pow"] = _gmpy_pow

## Install functions
try:
    import gmpy
    install_gmpy()
except ImportError:
    install()
