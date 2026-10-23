# ----------------------------------------------------------------------
# Crypto-related snippets
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import random
import hashlib


# Symbols used in salt
ITOA64 = b"./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
SALT_SYMBOLS = list(ITOA64)
REARRANGED_BITS = ((0, 6, 12), (1, 7, 13), (2, 8, 14), (3, 9, 15), (4, 10, 5))


def gen_salt(salt_len: int) -> bytes:
    """
    Generate random salt of given length
    >>> len(gen_salt(10)) == 10
    True
    """
    return bytes([random.choice(SALT_SYMBOLS) for _ in range(salt_len)])


def md5crypt(password: bytes, salt: bytes | None = None, magic: bytes = b"$1$") -> bytes:
    """
    MD5 password hash
    (Used for RIPE authentication)
    >>> md5crypt(b"test", salt=b"1234")
    b'$1$1234$InX9CGnHSFgHD3OZHTyt3.'
    >>> md5crypt(b"test", salt=b"1234")
    b'$1$1234$InX9CGnHSFgHD3OZHTyt3.'
    >>> md5crypt(b"test", salt=b"1234", magic=b"$5$")
    b'$5$1234$x29w4cwzSDnesjss/m2O1.'
    """
    salt = salt if salt else gen_salt(8)
    # /* The password first, since that is what is most unknown */ /* Then our magic string */ /* Then the raw salt */
    m = hashlib.md5(password + magic + salt)
    # /* Then just as many characters of the MD5(pw,salt,pw) */
    mixin = hashlib.md5(password + salt + password).digest()
    for i in range(len(password)):
        m.update(bytes([mixin[i % 16]]))
    # /* Then something really weird... */
    # Also really broken, as far as I can tell.  -m
    i = len(password)
    while i:
        if i & 1:
            m.update(b"\x00")
        else:
            m.update(bytes([password[0]]))
        i >>= 1
    final = m.digest()
    # /* and now, just to make sure things don't run too fast */
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
    rearranged = []
    for a, b, c in REARRANGED_BITS:
        v = final[a] << 16 | final[b] << 8 | final[c]
        for i in range(4):
            rearranged.append(ITOA64[v & 0x3F])
            v >>= 6
    v = final[11]
    for i in range(2):
        rearranged.append(ITOA64[v & 0x3F])
        v >>= 6
    return magic + salt + b"$" + bytes(rearranged)
