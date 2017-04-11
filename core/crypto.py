# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Crypto-related snippets
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
import hashlib

## Symbols used in salt
ITOA64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
SALT_DICT = list(ITOA64)


def gen_salt(len):
    """
    Generate random salt of given length
    >>> len(gen_salt(10))==10
    True
    """
    return "".join([random.choice(SALT_DICT) for _ in range(len)])


def md5crypt(password, salt=None, magic="$1$"):
    """
    MD5 password hash
    (Used for RIPE authentication)
    >>> md5crypt("test",salt="1234")
    '$1$1234$InX9CGnHSFgHD3OZHTyt3.'
    >>> md5crypt("test",salt="1234")
    '$1$1234$InX9CGnHSFgHD3OZHTyt3.'
    >>> md5crypt("test",salt="1234",magic="$5$")
    '$5$1234$x29w4cwzSDnesjss/m2O1.'
    """
    salt = salt if salt else gen_salt(8)
    # /* The password first, since that is what is most unknown */ /* Then our magic string */ /* Then the raw salt */
    m = hashlib.md5(password + magic + salt)
    # /* Then just as many characters of the MD5(pw,salt,pw) */
    mixin = hashlib.md5(password + salt + password).digest()
    for i in range(len(password)):
        m.update(mixin[i % 16])
    # /* Then something really weird... */
    # Also really broken, as far as I can tell.  -m
    i = len(password)
    while i:
        if i & 1:
            m.update("\x00")
        else:
            m.update(password[0])
        i >>= 1
    final = m.digest()
    # /* and now, just to make sure things don"t run too fast */
    for i in range(1000):
        m2 = hashlib.md5()
        if i & 1:
            m2.update(password)
        else:
            m2.update(final)
        if i % 3:
            m2.update(salt)
        if i % 7:
            m2.update(password)
        if i & 1:
            m2.update(final)
        else:
            m2.update(password)
        final = m2.digest()
    # This is the bit that uses to64() in the original code.
    rearranged = ""
    for a, b, c in (
    (0, 6, 12), (1, 7, 13), (2, 8, 14), (3, 9, 15), (4, 10, 5)):
        v = ord(final[a]) << 16 | ord(final[b]) << 8 | ord(final[c])
        for i in range(4):
            rearranged += ITOA64[v & 0x3f]
            v >>= 6
    v = ord(final[11])
    for i in range(2):
        rearranged += ITOA64[v & 0x3f]
        v >>= 6
    return magic + salt + "$" + rearranged
