# ---------------------------------------------------------------------
# Various text-processing utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import string
from itertools import zip_longest

# Third-party modules
from typing import List, Union, Iterable

rx_header_start = re.compile(r"^\s*[-=]+[\s\+]+[-=]+")
rx_col = re.compile(r"^([\s\+]*)([\-]+|[=]+)")


def default_line_wrapper(p_line):
    return p_line.expandtabs()


def parse_table(
    s,
    allow_wrap=False,
    allow_extend=False,
    expand_columns=False,
    max_width=0,
    footer=None,
    n_row_delim="",
    line_wrapper=default_line_wrapper,
    row_wrapper=None,
):
    """
    Parse string containing table an return a list of table rows.
    Each row is a list of cells.
    Columns are determined by a sequences of ---- or ==== which are
    determines rows bounds.
    Examples:
    First Second Third
    ----- ------ -----
    a     b       c
    ddd   eee     fff
    Will be parsed down to the [["a","b","c"],["ddd","eee","fff"]]

    :param s: Table for parsing
    :type s: str
    :param allow_wrap: Union if cell contins multiple line
    :type allow_wrap: bool
    :param allow_extend: Check if column on row longest then column width, enlarge it and shift rest of columns
    :type allow_extend: bool
    :param expand_columns: Expand columns covering all available width
    :type expand_columns: bool
    :param max_width: Max table width, if table width < max_width extend length, else - nothing
    :type max_width: int
    :param footer: stop iteration if match expression footer
    :type footer: string
    :param n_row_delim: Append delimiter to next cell line
    :type n_row_delim: string
    :param line_wrapper: Call line_wrapper with line argument
    :type line_wrapper: callable
    :param row_wrapper: Call row_wrapper with row argument
    :type row_wrapper: callable
    """
    r = []
    columns = []
    if footer is not None:
        rx_footer = re.compile(footer)
    if line_wrapper and not callable(line_wrapper):
        line_wrapper = None
    if row_wrapper and not callable(row_wrapper):
        row_wrapper = None
    for line in s.splitlines():
        if line_wrapper:
            # Replace tabs with spaces with step 8
            line = line_wrapper(line)
        if not line.strip() and footer is None:
            columns = []
            continue
        if footer is not None and rx_footer.search(line):
            break  # Footer reached, stop
        if not columns and rx_header_start.match(line):
            # Column delimiters found. try to determine column's width
            columns = []
            x = 0
            while line:
                match = rx_col.match(line)
                if not match:
                    break
                spaces = len(match.group(1))
                dashes = len(match.group(2))
                columns += [(x + spaces, x + spaces + dashes)]
                x += match.end()
                line = line[match.end() :]
            if max_width and columns[-1][-1] < max_width:
                columns[-1] = (columns[-1][0], max_width)
            if expand_columns:
                columns = [(cc[0], nc[0] - 1) for cc, nc in zip(columns, columns[1:])] + [
                    columns[-1]
                ]
        elif columns:  # Fetch cells
            if allow_extend:
                # Find which spaces between column not empty
                ll = len(line)
                for i, (f, t) in enumerate(columns):
                    if t < ll and line[t].strip():
                        # If spaces not empty - shift column width equal size row
                        shift = len(line[f:].split()[0]) - (t - f)
                        # Enlarge column
                        columns[i] = (f, t + shift)
                        # Shift rest
                        columns[i + 1 :] = [(v[0] + shift, v[1] + shift) for v in columns[i + 1 :]]
                        break
            if allow_wrap:
                row = [line[f:t] for f, t in columns]
                if r and not row[0].strip():
                    # first column is empty
                    for i, x in enumerate(row):
                        if (
                            x.strip()
                            and not r[-1][i].endswith(n_row_delim)
                            and not x.startswith(n_row_delim)
                        ):
                            r[-1][i] += "%s%s" % (n_row_delim, row_wrapper(x) if row_wrapper else x)
                        else:
                            r[-1][i] += row_wrapper(x) if row_wrapper else x
                else:
                    r += [row]
            else:
                r += [
                    [
                        row_wrapper(line[f:t]).strip() if row_wrapper else line[f:t].strip()
                        for f, t in columns
                    ]
                ]
    if allow_wrap:
        return [[x.strip() for x in rr] for rr in r]
    else:
        return r


#
# Convert HTML to plain text
#
rx_html_tags = re.compile("</?[^>+]+>", re.MULTILINE | re.DOTALL)


def strip_html_tags(s):
    t = rx_html_tags.sub("", s)
    for k, v in [("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
        t = t.replace(k, v)
    return t


#
# Convert XML to list of elements
#
def xml_to_table(s, root, row):
    # pylint: disable=line-too-long
    """
    >>> xml_to_table('<?xml version="1.0" encoding="UTF-8" ?><response><action><row><a>1</a><b>2</b></row><row><a>3</a><b>4</b></row></action></response>','action','row') # noqa
    [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}]
    """
    # Detect root element
    match = re.search(r"<%s>(.*)</%s>" % (root, root), s, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    s = match.group(1)
    row_re = re.compile(r"<%s>(.*?)</%s>" % (row, row), re.DOTALL | re.IGNORECASE)
    item_re = re.compile(r"<([^\]+])>(.*?)</\1>", re.DOTALL | re.IGNORECASE)
    r = []
    for m in [x for x in row_re.split(s) if x]:
        data = item_re.findall(m)
        if data:
            r += [dict(data)]
    return r


#
# Convert list of values to string of ranges
#
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


#
# Convert range string to a list of integers
#
rx_range = re.compile(r"^(\d+)\s*-\s*(\d+)$")


def ranges_to_list(s, splitter=","):
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
    if "to" in s:
        s = s.replace(" to ", "-")
    for p in s.split(splitter):
        p = p.strip()
        try:
            r += [int(p)]
            continue
        except ValueError:
            pass
        match = rx_range.match(p)
        if not match:
            raise SyntaxError
        f, t = [int(x) for x in match.groups()]
        if f >= t:
            raise SyntaxError
        for i in range(f, t + 1):
            r += [i]
    return list(sorted(r))


def replace_re_group(expr, group, pattern):
    if isinstance(expr, bytes):
        return _replace_re_group_binary(expr, group, pattern)
    return _replace_re_group_text(expr, group, pattern)


def _replace_re_group_text(expr: str, group: str, pattern: str) -> str:
    """
    Replace regular expression group with pattern

    >>> replace_re_group("nothing","(?P<groupname>","groupvalue")
    'nothing'
    >>> replace_re_group("the (?P<groupname>simple) test","(?P<groupname>","groupvalue")
    'the groupvalue test'
    >>> replace_re_group("the (?P<groupname> nested (test)>)","(?P<groupname>","groupvalue")
    'the groupvalue'
    """
    r = []
    lg = len(group)
    while expr:
        idx = expr.find(group)
        if idx == -1:
            break
        r += [expr[:idx]]
        expr = expr[idx + lg :]
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
                    r += [pattern]
                    break
    r += [expr]
    return "".join(r)


def _replace_re_group_binary(expr: bytes, group: bytes, pattern: bytes) -> bytes:
    """
    Replace regular expression group with pattern

    >>> replace_re_group("nothing","(?P<groupname>","groupvalue")
    'nothing'
    >>> replace_re_group("the (?P<groupname>simple) test","(?P<groupname>","groupvalue")
    'the groupvalue test'
    >>> replace_re_group("the (?P<groupname> nested (test)>)","(?P<groupname>","groupvalue")
    'the groupvalue'
    """
    r = []
    lg = len(group)
    while expr:
        idx = expr.find(group)
        if idx == -1:
            break
        r += [expr[:idx]]
        expr = expr[idx + lg :]
        level = 1  # Level of parenthesis nesting
        while expr:
            c = expr[0]
            expr = expr[1:]
            if c == 0x5C:  # "\\"
                # Skip quoted character
                expr = expr[1:]
                continue
            elif c == 0x28:  # "("
                # Increase nesting level
                level += 1
                continue
            elif c == 0x29:  # ")"
                # Decrease nesting level
                level -= 1
                if level == 0:
                    # Replace with pattern and search for next
                    r += [pattern]
                    break
    r += [expr]
    return b"".join(r)


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


rx_split_alnum = re.compile(r"(\d+|[^0-9]+)")


def _iter_split_alnum(s: str) -> Iterable[str]:
    """
    Iterator yielding alphabetic and numeric sections if string

    :param s:
    :return:
    """
    for match in rx_split_alnum.finditer(s):
        yield match.group(0)


def split_alnum(s: str) -> List[Union[str, int]]:
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

    def maybe_int(v: str) -> Union[str, int]:
        try:
            return int(v)
        except ValueError:
            return v

    return [maybe_int(x) for x in _iter_split_alnum(s)]


def alnum_key(s: str) -> str:
    """
    Comparable alpha-numeric key
    :param s:
    :return:
    """

    def maybe_formatted_int(v: str) -> str:
        try:
            return "%012d" % int(v)
        except ValueError:
            return v

    return "".join(maybe_formatted_int(x) for x in _iter_split_alnum(s))


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
    for line in s.splitlines():
        if rx_notspace.match(line):
            if len(cr) > 1:
                r += ["\n".join(cr)]
            cr = [line]
            continue
        elif line:
            cr += [line]
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


rx_safe_path = re.compile(r"[^a-z0-9\-\+]+", re.IGNORECASE)


def quote_safe_path(d):
    return rx_safe_path.sub("_", cyr_to_lat(d))


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


def format_table(widths, data, sep=" ", hsep=" "):
    """
    Print formatted table.
    :param widths: list of minimal column widths
    :param data: list of rows, first row is the header
    :param sep: column separator
    :param hsep: header line separator
    """
    # Calculate column widths
    widths = list(widths)
    for row in data:
        widths = [max(x, len(str(y))) for x, y in zip(widths, row)]
    # Build print mask
    mask = sep.join("%%-%ds" % w for w in widths)
    out = [
        # Header line
        mask % tuple(data[0]),
        # Header separator
        hsep.join("-" * w for w in widths),
    ]
    out += [mask % tuple(row) for row in data[1:]]
    return "\n".join(out)


rx_non_numbers = re.compile("[^0-9]+")


def clean_number(n):
    """
    Remove all non-number occurences
    :param n:
    :return:
    """
    return rx_non_numbers.sub("", n)


def safe_shadow(text):
    """
    Shadow string to first and last char
    :param text:
    :return:

    >>> safe_shadow(None)
    'None'
    >>>safe_shadow("s")
    '******'
    >>>safe_shadow("sssssss")
    's******s'
    >>> safe_shadow(1)
    '******'
    >>> safe_shadow([1, 2])
    '******'
    """
    if not text:
        return "None"
    elif not isinstance(text, str):
        return "******"
    elif len(text) > 2:
        return "%s******%s" % (text[0], text[-1])
    else:
        return "******"


def ch_escape(s):
    return s.replace("\n", "\\n").replace("\t", "\\t").replace("\\", "\\\\")


ESC_REPLACEMENTS = {re.escape("\n"): " ", re.escape("\t"): "        "}

rx_escape = re.compile("|".join(ESC_REPLACEMENTS))


def tsv_escape(text):
    return rx_escape.sub(lambda match: ESC_REPLACEMENTS[re.escape(match.group(0))], text)


def parse_table_header(v):
    """
    Parse header structured multiline format:
    Config    Current Agg     Min    Ld Share  Flags Ld Share  Agg Link  Link Up
    Master    Master  Control Active Algorithm       Group     Mbr State Transitions
    :param v:
    :return: Dictionary {start column position: header}
    {10: 'Config Master', 18: 'Current Master', 26: 'Agg Control', 33: 'Min Active',
     43: 'Ld Share Algorithm', 49: 'Flags ', 59: 'Ld Share Group', 63: 'Agg Mbr', 69: 'Link State'}
    """
    from numpy import array

    head = []
    empty_header = None
    header = {}
    for num, lines in enumerate(zip_longest(*v, fillvalue="-")):
        #
        if empty_header is None:
            empty_header = (" ",) * len(lines)
            head += [lines]
            continue
        if set(head[-1]) == {" "} and lines != empty_header:
            head = array(head)
            # Transpone list header string
            header[num] = " ".join(["".join(s).strip() for s in head.transpose().tolist()])
            header[num] = header[num].strip()
            head = []
        head += [lines]
    # last column
    head = array(head)
    header[num] = " ".join(["".join(s).strip(" -") for s in head.transpose().tolist()])
    header[num] = header[num].strip()
    return header


def split_text(text: str, max_chunk: int) -> Iterable[str]:
    """
    Split text by splitline if len > max_chunk
    :param text:
    :param max_chunk:
    :return: Iterable[str]
    """
    size = 0
    result = []
    for line in text.splitlines():
        if size + len(line) <= max_chunk:
            result.append(line)
            size = size + len(line)
        else:
            size = 0
            yield "\n".join(result)
            result = [line]
    yield "\n".join(result)


def filter_non_printable(text: str) -> str:
    return "".join(filter(lambda x: x in string.printable, text))


legend = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "y",
    "ы": "y",
    "ь": "'",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "G",
    "Д": "D",
    "Е": "E",
    "Ё": "Yo",
    "Ж": "Zh",
    "З": "Z",
    "И": "I",
    "Й": "Y",
    "К": "K",
    "Л": "L",
    "М": "M",
    "Н": "N",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "У": "U",
    "Ф": "F",
    "Х": "H",
    "Ц": "Ts",
    "Ч": "Ch",
    "Ш": "Sh",
    "Щ": "Shch",
    "Ъ": "Y",
    "Ы": "Y",
    "Ь": "'",
    "Э": "E",
    "Ю": "Yu",
    "Я": "Ya",
}


def cyr_to_lat(s: str) -> str:
    r: List[str] = []
    for c in s:
        if c in legend:
            r.append(legend[c])
        elif c == " ":
            r.append("_")
        else:
            r.append(c)

    return "".join(r)


def str_distance(s1: str, s2: str) -> int:
    """
    Get the distance between the strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        The distance between the strings.
    """
    s1 = s1.lower()
    s2 = s2.lower()
    n = 0
    if len(s1) != len(s2):
        n += abs(len(s1) - len(s2))
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            n += 1
    return n
