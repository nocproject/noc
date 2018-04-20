# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Binary data to string encoder/decoder
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re
#
# Patterns
#
rx_unqoute=re.compile(r"\\x([0-9a-f][0-9a-f])",re.MULTILINE|re.DOTALL)
# Map to convert two-char hex to integer
hex_map=dict([("%02x"%i,chr(i)) for i in range(256)])
#
# Quote binary data to ASCII-string
#
=======
##----------------------------------------------------------------------
## Binary data to string encoder/decoder
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
##
## Patterns
##
rx_unqoute=re.compile(r"\\x([0-9a-f][0-9a-f])",re.MULTILINE|re.DOTALL)
## Map to convert two-char hex to integer
hex_map=dict([("%02x"%i,chr(i)) for i in range(256)])
##
## Quote binary data to ASCII-string
##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
def bin_quote(s):
    """
    >>> bin_quote(None)
    ''
    >>> bin_quote("A")
    'A'
    """
    def qc(c):
        if c=="\\":
            return "\\\\"
        oc=ord(c)
        if oc<32 or oc>126:
            return "\\x%02x"%oc
        return c

    if s is None:
        return ""
    else:
        if isinstance(s, unicode):
           s = s.encode("utf-8")
        return "".join([qc(c) for c in s])
<<<<<<< HEAD

#
# Decode ASCII-encoded string back to binary
#
=======
    
##
## Decode ASCII-encoded string back to binary
##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
def bin_unquote(s):
    """
    >>> [i for i in range(256) if bin_unquote(bin_quote(chr(i)))!=chr(i)]
    []
    """
    if isinstance(s, unicode):
        s = s.encode("utf-8")
    return rx_unqoute.sub(lambda x:hex_map[x.group(1)], str(s).replace(r"\\","\\x5c"))
