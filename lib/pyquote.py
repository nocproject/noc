# -*- coding: utf-8 -*-
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
def bin_quote(s):
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
        return "".join([qc(c) for c in s])
    
##
## Decode ASCII-encoded string back to binary
##
def bin_unquote(s):
    """
    >>> [i for i in range(256) if bin_unquote(bin_quote(chr(i)))!=chr(i)]
    []
    """
    return rx_unqoute.sub(lambda x:hex_map[x.group(1)], str(s).replace(r"\\","\\x5c"))
##
## Unit Test
##
if __name__ == "__main__":
    import doctest
    doctest.testmod()
