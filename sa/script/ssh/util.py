# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Common SSH utilities
## Based upon twisted.conch.ssh code
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import struct
import os
from hashlib import sha1
## Third-party modules
from Crypto.Util.number import bytes_to_long, long_to_bytes

##
##
##
def secure_random(bytes):
    return os.urandom(bytes)

##
##
##
def NS(s):
    s=str(s)
    return struct.pack("!L",len(s))+s

##
##
##
def get_NS(s, count=1):
    c=0
    while s and c<count:
        l,=struct.unpack("!L", s[:4])
        yield s[4:4+l]
        s=s[4+l:]
        c+=1
    yield s

##
##
##
def MP(number):
    if number==0:
        return "\x00\x00\x00\x00"
    assert number>0
    bn = long_to_bytes(number)
    if ord(bn[0])&128:
        bn = "\x00" + bn
    return struct.pack('>L',len(bn)) + bn

##
##
##
def MPpow(x, y, z):
    return MP(pow(x,y,z))

##
##
##
def get_MP(s, count=1):
    c=0
    while s and c<count:
        l,=struct.unpack(">L", s[:4])
        yield bytes_to_long(s[4:4+l])
        s=s[4+l:]
        c+=1
    yield s

##
##
##
def pkcs1_digest(data, message_len):
    d = ID_SHA1+sha1(data).digest()
    pad_len=message_len-2-len(d)
    return "\x01" + ("\xff" * pad_len) + "\x00" + d

##
ID_SHA1 = "\x30\x21\x30\x09\x06\x05\x2b\x0e\x03\x02\x1a\x05\x00\x04\x14"
