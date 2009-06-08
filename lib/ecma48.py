# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ECMA-48 control sequences processing
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import re
## Convert ECMA Notation to byte form
def c(x,y):
    """
    Convert ECMA-48 character notation to 8-bit form
    >>> c(0,0)
    0
    >>> c(1,11)
    27
    >>> c(15,15)
    255
    """
    return (x<<4)+y

ESC=chr(c(1,11))
##
## Definitions of Control Character Sequences from ECMA-48
##
C0  = "[00/00-01/15]"
C1  = "01/11,[04/00-05/15]"
CSI = "01/11,05/11,[03/00-03/15]*,[02/00-02/15]*,[04/00-07/14]"
##
## Compile single definition to regular expression
##
rx_char=re.compile(r"^(\d\d)/(\d\d)$")
rx_range=re.compile(r"^\[(\d\d)/(\d\d)-(\d\d)/(\d\d)\](\*?)$")
def compile_ecma_def(s):
    r=[]
    for token in s.split(","):
        match=rx_range.match(token)
        if match:
            c1=c(int(match.group(1)),int(match.group(2)))
            c2=c(int(match.group(3)),int(match.group(4)))
            if c1==c2:
                x=[r"\x%02x"%c1]
            elif c1<c2:
                rr=[r"\x%02x"%x for x in range(c1,c2+1)]
                x=["[%s]"%"".join(rr)]
            else:
                rr=[r"\x%02x"%x for x in range(c2,c1+1)]
                x=["[%s]"%"".join(rr)]
            if match.group(5):
                x+="*"
            r+=x
            continue
        match=rx_char.match(token)
        if match:
            r+=[r"\x%02x"%c(int(match.group(1)),int(match.group(2)))]
            continue
        raise Exception("Invalid token: <%s>"%token)
    return "".join(r)
##
## Compile ECMA-48 definitions to regular expression
##
def get_ecma_re():
    re_csi=compile_ecma_def(CSI)
    re_c1=compile_ecma_def(C1).replace("\\x5b","")
    re_c0=compile_ecma_def(C0)
    for xc in ["\\x08","\\x09","\\x0a","\\x0d","\\x1b"]:
        re_c0=re_c0.replace(xc,"")
    #re_c0=compile_ecma_def(C0).replace("\\x08","").replace("\\x0d","").replace("\\x0a","").replace("\\x1b","").replace("\\x09","") # \n,\r, ESC, \t, BS
    re_vt100="\\x1b[c()78]" # VT100
    re_other="\\x1b[^[]"       # Last resort. Skip all ESC+char
    return "|".join(["(%s)"%r for r in (re_csi,re_c1,re_c0,re_vt100,re_other)])
##
## Backspace pattern
##
rx_bs=re.compile("[^\x08]\x08")
##
## \r<spaces>\r should be cut
##
rx_lf_spaces=re.compile(r"\r\s+\r")
##
## ESC sequence to go to the bottom-left corner of the screen
##
rx_esc_pager=re.compile("(^.*?\x1b\\[24;1H)|((?<=\n).*?\x1b\\[24;1H)",re.MULTILINE)
##
## Remove ECMA-48 Control Sequences from a string
##
rx_ecma=re.compile(get_ecma_re())
def strip_control_sequences(s):
    """
    Normal text leaved untouched
    >>> strip_control_sequences("Lorem Ipsum")
    'Lorem Ipsum'
    
    CR,LF and ESC survive from C0 set
    >>> repr(strip_control_sequences("".join([chr(i) for i in range(32)])))
    "'\\\\x08\\\\t\\\\n\\\\r\\\\x1b'"
    
    C1 set stripped (ESC+[ survive)
    >>> strip_control_sequences("".join(["\x1b"+chr(i) for i in range(64,96)]))
    '\\x1b['
    
    CSI without P and I stripped
    >>> strip_control_sequences("\x1b[@\x1b[a\x1b[~")
    ''
    
    CSI with I stripped
    >>> strip_control_sequences("\x1b[ @\x1b[/~")
    ''
    
    CSI with P and I stripped
    >>> strip_control_sequences("\x1b[0 @\x1b[0;7/~")
    ''
    
    Cleaned stream
    >>> strip_control_sequences("L\x1b[@or\x1b[/~em\x1b[0 @ Ips\x1b[0;7/~um\x07")
    'Lorem Ipsum'
    
    Incomplete CSI passed
    >>> strip_control_sequences("\x1b[")
    '\\x1b['
    
    Incomplete C1 passed
    >>> strip_control_sequences('\x1b')
    '\\x1b'
    
    Single backspace
    >>> strip_control_sequences('123\x084')
    '124'
    
    Triple backspace
    >>> strip_control_sequences('123\x08\x08\x084')
    '4'
    """
    def strip_while(s,rx):
        while True:
            ss=rx.sub("",s)
            if ss==s:
                return s
            s=ss
    
    # Remove pager trash
    s=strip_while(s,rx_esc_pager)
    # Process backspaces
    s=strip_while(s,rx_bs)
    # Process LFs
    s=rx_lf_spaces.sub("",s)
    # Remove escape sequences
    return rx_ecma.sub("",s)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
