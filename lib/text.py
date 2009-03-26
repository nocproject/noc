# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various text-processing utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import re

##
## Parse string containing table an return a list of table rows.
## Each row is a list of cells.
## Columns are determined by a sequences of ---- or ==== which are
## determines rows bounds.
## Examples:
## First Second Third
## ----- ------ -----
## a     b       c
## ddd   eee     fff
## Will be parsed down to the [["a","b","c"],["ddd","eee","fff"]]
##
rx_header_start=re.compile(r"^\s*[-=]+\s+[-=]+")
rx_col=re.compile(r"^(\s*)([\-]+|[=]+)")
def parse_table(s):
    columns=None
    r=[]
    columns=[]
    for l in s.splitlines():
        if not l.strip():
            columns=[]
            continue
        if rx_header_start.match(l): # Column delimiters found. try to determine column's width
            columns=[]
            x=0
            while l:
                match=rx_col.match(l)
                if not match:
                    break
                columns.append((x+len(match.group(1)),x+len(match.group(1))+len(match.group(2))))
                x+=match.end()
                l=l[match.end():]
        elif columns: # Fetch cells
            r.append([l[f:t].strip() for f,t in columns])
    return r
##
## Convert HTML to plain text
##
rx_html_tags=re.compile("</?[^>+]+>",re.MULTILINE|re.DOTALL)
def strip_html_tags(s):
    t=rx_html_tags.sub("",s)
    for k,v in [("&nbsp;"," "),("&lt;","<"),("&gt;",">"),("&amp;","&")]:
        t=t.replace(k,v)
    return t
