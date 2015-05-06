# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various text-processing utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
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
rx_header_start = re.compile(r"^\s*[-=]+\s+[-=]+")
rx_col = re.compile(r"^(\s*)([\-]+|[=]+)")


def parse_table(s):
    """
    >>> parse_table("First Second Third\\n----- ------ -----\\na     b       c\\nddd   eee     fff\\n")
    [['a', 'b', 'c'], ['ddd', 'eee', 'fff']]
    >>> parse_table("First Second Third\\n----- ------ -----\\na             c\\nddd   eee     fff\\n")
    [['a', '', 'c'], ['ddd', 'eee', 'fff']]
    """
    r = []
    columns = []
    for l in s.splitlines():
        if not l.strip():
            columns = []
            continue
        if rx_header_start.match(l):
            # Column delimiters found. try to determine column's width
            columns = []
            x = 0
            while l:
                match = rx_col.match(l)
                if not match:
                    break
                columns.append((x + len(match.group(1)),
                                x + len(match.group(1)) + len(
                                    match.group(2))))
                x += match.end()
                l = l[match.end():]
        elif columns:  # Fetch cells
            r.append([l[f:t].strip() for f, t in columns])
    return r

##
## Convert HTML to plain text
##
rx_html_tags = re.compile("</?[^>+]+>", re.MULTILINE | re.DOTALL)


def strip_html_tags(s):
    t = rx_html_tags.sub("", s)
    for k, v in [("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"),
        ("&amp;", "&")]:
        t = t.replace(k, v)
    return t


##
## Convert XML to list of elements
##
def xml_to_table(s, root, row):
    """
    >>> xml_to_table('<?xml version="1.0" encoding="UTF-8" ?><response><action><row><a>1</a><b>2</b></row><row><a>3</a><b>4</b></row></action></response>','action','row')
    [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}]
    """
    # Detect root element
    match = re.search(r"<%s>(.*)</%s>" % (root, root), s,
        re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    s = match.group(1)
    row_re = re.compile(r"<%s>(.*?)</%s>" % (row, row),
        re.DOTALL | re.IGNORECASE)
    item_re = re.compile(r"<([^\]+])>(.*?)</\1>",
        re.DOTALL | re.IGNORECASE)
    r = []
    for m in [x for x in row_re.split(s) if x]:
        data = item_re.findall(m)
        if data:
            r += [dict(data)]
    return r


##
## Convert list of values to string of ranges
##
def list_to_ranges(s):
    """
    >>> list_to_ranges([])
    ''
    >>> list_to_ranges([1])
    '1'
    >>> list_to_ranges([1,2])
    '1-2'
    >>> list_to_ranges([1,2,3])
    '1-3'
    >>> list_to_ranges([1,2,3,5])
    '1-3,5'
    >>> list_to_ranges([1,2,3,5,6,7])
    '1-3,5-7'
    >>> list_to_ranges(range(1,4001))
    '1-4000'
    """

    def f():
        if last_start == last_end:
            return str(last_start)
        else:
            return "%d-%d" % (last_start, last_end)

    last_start = None
    last_end = None
    r = []
    for i in sorted(s):
        if last_end is not None and i == last_end + 1:
            last_end += 1
        else:
            if last_start is not None:
                r += [f()]
            last_start = i
            last_end = i
    if last_start is not None:
        r += [f()]
    return ",".join(r)

##
## Convert range string to a list of integers
##
rx_range = re.compile(r"^(\d+)\s*-\s*(\d+)$")


def ranges_to_list(s):
    """
    >>> ranges_to_list("1")
    [1]
    >>> ranges_to_list("1, 2")
    [1, 2]
    >>> ranges_to_list("1, 10-12")
    [1, 10, 11, 12]
    >>> ranges_to_list("1, 10-12, 15, 17-19")
    [1, 10, 11, 12, 15, 17, 18, 19]
    """
    r = []
    for p in s.split(","):
        p = p.strip()
        try:
            r += [int(p)]
            continue
        except:
            pass
        match = rx_range.match(p)
        if not match:
            raise SyntaxError
        f, t = [int(x) for x in match.groups()]
        if f >= t:
            raise SyntaxError
        for i in range(f, t + 1):
            r += [i]
    return sorted(r)


##
## Replace regular expression group with pattern
##
def replace_re_group(expr, group, pattern):
    """
    >>> replace_re_group("nothing","(?P<groupname>","groupvalue")
    'nothing'
    >>> replace_re_group("the (?P<groupname>simple) test","(?P<groupname>","groupvalue")
    'the groupvalue test'
    >>> replace_re_group("the (?P<groupname> nested (test)>)","(?P<groupname>","groupvalue")
    'the groupvalue'
    """
    r = ""
    lg = len(group)
    while expr:
        idx = expr.find(group)
        if idx == -1:
            return r + expr  # No more groups found
        r += expr[:idx]
        expr = expr[idx + lg:]
        level = 1  # Level of parenthesis nesting
        while expr:
            c = expr[0]
            expr = expr[1:]
            if c == "\\":
                # Skip quoted character
                expr = expr[1:]
                continue
            elif c == "(":
                # Increase nesting level
                level += 1
                continue
            elif c == ")":
                # Decrease nesting level
                level -= 1
                if level == 0:
                    # Replace with pattern and search for next
                    r += pattern
                    break
    return r + expr


def indent(text, n=4):
    """
    Indent each line of text with spaces
    
    :param text: text
    :param n: amount of spaces to ident
    
    >>> indent("")
    ''
    >>> indent("the quick brown fox\\njumped over an lazy dog\\nend")
    '    the quick brown fox\\n    jumped over an lazy dog\\n    end'
    """
    if not text:
        return ""
    i = " " * n
    return i + text.replace("\n", "\n" + i)


def split_alnum(s):
    """
    Split line to a sequence of iterating alpha and digit strings

    :param s:
    :type s: str
    :return: list
    :rtype: list

    >>> split_alnum("Fa 0/1")
    ['Fa ', 0, '/', 1]
    >>> split_alnum("Fa 0/1.15")
    ['Fa ', 0, '/', 1, '.', 15]
    >>> split_alnum("ge-1/0/1")
    ['ge-', 1, '/', 0, '/', 1]
    >>> split_alnum("ge-1/0/1.15")
    ['ge-', 1, '/', 0, '/', 1, '.', 15]
    """
    def convert(x):
        try:
            return int(x)
        except ValueError:
            return x
    r = []
    digit = None
    for c in s:
        d = c.isdigit()
        if d != digit:
            digit = d
            r += [c]
        else:
            r[-1] += c
    return [convert(x) for x in r]

rx_notspace = re.compile(r"^\S+")


def find_indented(s):
    """
    Parses following text structure:

    section 1 header
        line 1
        line 2
    section 2 header
        line 1
        line 2

    >>> find_idented("section0\\nsection 1\\n  line 1-1\\n  line 1-2\\n\\n"\
                     "section 2\\n  line 2-1\\n  line 2-2")
    ['section 1\n  line 1-1\n  line 1-2', 'section 2\n  line 2-1\n  line 2-2']
    :param s:
    :return:
    """
    r = []
    cr = []
    for l in s.splitlines():
        if rx_notspace.match(l):
            if len(cr) > 1:
                r += ["\n".join(cr)]
            cr = [l]
            continue
        elif l:
            cr += [l]
    if len(cr) > 1:
        r += ["\n".join(cr)]
    return r


def parse_kv(kmap, data, sep=":"):
    """
    :param kmap: text -> dict mapping
    :param data:
    :return: dict
    """
    r = {}
    for line in data.splitlines():
        if sep not in line:
            continue
        k, v = line.strip().split(sep, 1)
        k = k.strip().lower()
        if k in kmap:
            r[kmap[k]] = v.strip()
    return r


def str_dict(d):
    """
    Convert dict to key=value, key=value, .... string
    :type d: dict
    :rtype: str
    """
    return ", ".join("%s=%s" % (k, d[k]) for k in d)

rx_safe_path = re.compile("[^a-z0-9\-\+]+", re.IGNORECASE)


def quote_safe_path(d):
    return rx_safe_path.sub("_", d)


def to_seconds(v):
    """
    Convert string value to seconds.
    Available acronyms are h, d, w, m, y
    """
    m = 1
    if v.endswith("h"):
        v = v[:-1]
        m = 3600
    elif v.endswith("d"):
        v = v[:-1]
        m = 24 * 3600
    elif v.endswith("w"):
        v = v[:-1]
        m = 7 * 24 * 3600
    elif v.endswith("m"):
        v = v[:-1]
        m = 30 * 24 * 3600
    elif v.endswith("y"):
        v = v[:-1]
        m = 365 * 24 * 3600
    try:
        v = int(v)
    except ValueError:
        raise "Invalid time: %s" % v
    return v * m
