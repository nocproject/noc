# ---------------------------------------------------------------------
# Various text-processing utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import string
from itertools import zip_longest, pairwise
from typing import overload, Any
from collections.abc import Iterable, Sequence, Iterator


rx_header_start = re.compile(r"^\s*[-=]+[\s\+]+[-=]+")
rx_col = re.compile(r"^([\s\+]*)([\-]+|[=]+)")


def default_line_wrapper(p_line: str) -> str:
    """
    Expand tab characters in a line.

    Args:
        p_line: Input line.

    Returns:
        The input line with all tab characters expanded.
    """
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
                columns.append((x + spaces, x + spaces + dashes))
                x += match.end()
                line = line[match.end() :]
            if max_width and columns[-1][-1] < max_width:
                columns[-1] = (columns[-1][0], max_width)
            if expand_columns:
                columns = [(cc[0], nc[0] - 1) for cc, nc in pairwise(columns)] + [columns[-1]]
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
                            r[-1][i] += f"{n_row_delim}{row_wrapper(x) if row_wrapper else x}"
                        else:
                            r[-1][i] += row_wrapper(x) if row_wrapper else x
                else:
                    r.append(row)
            else:
                r.append(
                    [
                        row_wrapper(line[f:t]).strip() if row_wrapper else line[f:t].strip()
                        for f, t in columns
                    ]
                )
    if allow_wrap:
        return [[x.strip() for x in rr] for rr in r]
    return r


rx_html_tags = re.compile("</?[^>+]+>", re.MULTILINE | re.DOTALL)


def strip_html_tags(s: str) -> str:
    """
    Remove HTML tags from a string and decode a small subset of HTML entities.

    Args:
        s: Input string containing HTML markup.

    Returns:
        Plain text with HTML tags removed. The entities `&nbsp;`,
        `&lt;`, `&gt;`, and `&amp;` are replaced with their
        corresponding characters.

    Notes:
        This function performs simple text processing and is not a
        full HTML parser.
    """
    t = rx_html_tags.sub("", s)
    for k, v in [("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"), ("&amp;", "&")]:
        t = t.replace(k, v)
    return t


def xml_to_table(s: str, root: str, row: str) -> list[dict[str, str]]:
    """
    Extract a table from a simple XML document.

    The function searches for the specified root element, then extracts
    all child elements with the given row name. Each direct child element
    of a row is converted into a key-value pair.

    Args:
        s: XML document as a string.
        root: Name of the root element containing the table.
        row: Name of the row element.

    Returns:
        A list of dictionaries representing table rows. Returns an empty
        list if the specified root element is not found.

    Notes:
        This function uses regular expressions and is intended only for
        simple, well-formed XML. It is not a general-purpose XML parser.
    """
    # pylint: disable=line-too-long
    """
    >>> xml_to_table('<?xml version="1.0" encoding="UTF-8" ?><response><action><row><a>1</a><b>2</b></row><row><a>3</a><b>4</b></row></action></response>','action','row') # noqa
    [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}]
    """
    # Detect root element
    match = re.search(rf"<{root}>(.*)</{root}>", s, re.DOTALL | re.IGNORECASE)
    if not match:
        return []
    s = match.group(1)
    row_re = re.compile(rf"<{row}>(.*?)</{row}>", re.DOTALL | re.IGNORECASE)
    item_re = re.compile(r"<([^\]+])>(.*?)</\1>", re.DOTALL | re.IGNORECASE)
    r: list[dict[str, str]] = []
    for m in [x for x in row_re.split(s) if x]:
        data = item_re.findall(m)
        if data:
            r.append(dict(data))
    return r


def list_to_ranges(s: Iterable[int]) -> str:
    """
    Convert an iterable of integers to a compact range representation.

    Consecutive values are merged into ranges, while isolated values are
    represented as single numbers. The input is sorted before processing.

    Args:
        s: Iterable of integer values.

    Returns:
        A comma-separated string of individual values and inclusive ranges.
        Returns an empty string if the input is empty.

    Examples:
        ``[1, 2, 3, 5, 6, 7]`` -> ``"1-3,5-7"``
        ``[1, 3, 5]`` -> ``"1,3,5"``
    """

    def f():
        if last_start == last_end:
            return str(last_start)
        return f"{int(last_start)}-{int(last_end)}"

    last_start = None
    last_end = None
    r: list[str] = []
    for i in sorted(s):
        if last_end is not None and i == last_end + 1:
            last_end += 1
        else:
            if last_start is not None:
                r.append(f())
            last_start = i
            last_end = i
    if last_start is not None:
        r.append(f())
    return ",".join(r)


rx_range = re.compile(r"^(\d+)\s*-\s*(\d+)$")


def ranges_to_list(s: str, splitter: str = ",") -> list[int]:
    """
    Convert a string of integer ranges to a sorted list of integers.

    Individual values and inclusive ranges are accepted. Ranges may be
    specified either as ``N-M`` or ``N to M``.

    Args:
        s: Comma-separated string containing integer values and ranges.
        splitter: Separator between items. Defaults to ``,``
            .

    Returns:
        A sorted list of integers.

    Raises:
        SyntaxError: If the input contains an invalid range or malformed
            syntax.

    Examples:
        ``"1,10-12"`` -> ``[1, 10, 11, 12]``
        ``"1,10 to 12"`` -> ``[1, 10, 11, 12]``
    """
    r: list[int] = []
    if "to" in s:
        s = s.replace(" to ", "-")
    for p in s.split(splitter):
        p = p.strip()
        try:
            r.append(int(p))
            continue
        except ValueError:
            pass
        match = rx_range.match(p)
        if not match:
            raise SyntaxError
        f, t = [int(x) for x in match.groups()]
        if f >= t:
            raise SyntaxError
        r.extend(range(f, t + 1))
    return sorted(r)


@overload
def replace_re_group(expr: str, group: str, pattern: str) -> str: ...


@overload
def replace_re_group(expr: bytes, group: bytes, pattern: bytes) -> bytes: ...


def replace_re_group(expr: str | bytes, group: str | bytes, pattern: str | bytes) -> str | bytes:
    """
    Replace regular expression groups in text or binary data.

    Args:
        expr: Input string or byte sequence containing regex groups.
        group: Group prefix to search for.
        pattern: Replacement value.

    Returns:
        Input data with matching groups replaced.

    Raises:
        TypeError: If text and binary arguments are mixed.
    """
    if isinstance(expr, bytes):
        return _replace_re_group_binary(expr, group, pattern)
    return _replace_re_group_text(expr, group, pattern)


def _replace_re_group_text(expr: str, group: str, pattern: str) -> str:
    """
    Replace matching regular expression groups in a text string.

    The function searches for groups starting with the specified prefix
    and replaces their complete contents, including nested parentheses,
    with the given pattern.

    Args:
        expr: Input text containing regular expression groups.
        group: Group prefix to search for (for example, ``"(?P<name>"``).
        pattern: Replacement text.

    Returns:
        Text with matching groups replaced.

    Notes:
        This is a lightweight parser for simple regular expression group
        syntax and does not handle all possible regex constructs.
    """
    r = []
    lg = len(group)
    while expr:
        idx = expr.find(group)
        if idx == -1:
            break
        r.append(expr[:idx])
        expr = expr[idx + lg :]
        level = 1  # Level of parenthesis nesting
        while expr:
            c = expr[0]
            expr = expr[1:]
            if c == "\\":
                # Skip quoted character
                expr = expr[1:]
                continue
            if c == "(":
                # Increase nesting level
                level += 1
                continue
            if c == ")":
                # Decrease nesting level
                level -= 1
                if level == 0:
                    # Replace with pattern and search for next
                    r.append(pattern)
                    break
    r.append(expr)
    return "".join(r)


def _replace_re_group_binary(expr: bytes, group: bytes, pattern: bytes) -> bytes:
    """
    Replace matching regular expression groups in binary data.

    The function searches for groups starting with the specified byte prefix
    and replaces their complete contents, including nested parentheses,
    with the given byte pattern.

    Args:
        expr: Input byte sequence containing regular expression groups.
        group: Group prefix to search for (for example, ``b"(?P<name>"``).
        pattern: Replacement byte sequence.

    Returns:
        Byte sequence with matching groups replaced.

    Notes:
        This is a lightweight parser for simple regular expression group
        syntax and does not handle all possible regex constructs.
    """
    r = []
    lg = len(group)
    while expr:
        idx = expr.find(group)
        if idx == -1:
            break
        r.append(expr[:idx])
        expr = expr[idx + lg :]
        level = 1  # Level of parenthesis nesting
        while expr:
            c = expr[0]
            expr = expr[1:]
            if c == 0x5C:  # "\\"
                # Skip quoted character
                expr = expr[1:]
                continue
            if c == 0x28:  # "("
                # Increase nesting level
                level += 1
                continue
            if c == 0x29:  # ")"
                # Decrease nesting level
                level -= 1
                if level == 0:
                    # Replace with pattern and search for next
                    r.append(pattern)
                    break
    r.append(expr)
    return b"".join(r)


def indent(text: str, n: int = 4) -> str:
    """
    Indent each line of text by a fixed number of spaces.

    Args:
        text: Input text.
        n: Number of spaces to prepend to each line. Defaults to 4.

    Returns:
        The indented text. Empty input returns an empty string.

    Examples:
        ``"foo\\nbar"`` with ``n=2`` returns ``"  foo\\n  bar"``.
    """
    if not text:
        return ""
    i = " " * n
    return i + text.replace("\n", "\n" + i)


rx_split_alnum = re.compile(r"(\d+|[^0-9]+)")


def _iter_split_alnum(s: str) -> Iterable[str]:
    """
    Iterate over alphanumeric and non-alphanumeric sections of a string.

    The input string is split into consecutive numeric and non-numeric
    parts. Numeric sections contain only decimal digits; all other
    characters are grouped together.

    Args:
        s: Input string.

    Yields:
        Consecutive numeric or non-numeric sections of the string.
    """
    for match in rx_split_alnum.finditer(s):
        yield match.group(0)


def split_alnum(s: str) -> list[str | int]:
    """
    Split a string into alternating numeric and non-numeric parts.

    Numeric sections are converted to integers, while non-numeric sections
    remain strings.

    Args:
        s: Input string.

    Returns:
        A list containing strings and integers extracted from the input.

    Examples:
        ``"Fa 0/1"`` -> ``["Fa ", 0, "/", 1]``
        ``"ge-1/0/1.15"`` -> ``["ge-", 1, "/", 0, "/", 1, ".", 15]``
    """

    def maybe_int(v: str) -> str | int:
        try:
            return int(v)
        except ValueError:
            return v

    return [maybe_int(x) for x in _iter_split_alnum(s)]


def alnum_key(s: str) -> str:
    """
    Generate a comparable alphanumeric sorting key.

    Numeric parts of the input string are converted to zero-padded values,
    allowing strings containing numbers to be compared in natural order.

    Args:
        s: Input string.

    Returns:
        A string key suitable for lexicographical comparison.

    Examples:
        ``"ge-1/0/10"`` produces a key that sorts after
        ``"ge-1/0/2"``.
    """

    def maybe_formatted_int(v: str) -> str:
        try:
            return f"{int(v):012d}"
        except ValueError:
            return v

    return "".join(maybe_formatted_int(x) for x in _iter_split_alnum(s))


rx_notspace = re.compile(r"^\S+")


def find_indented(s: str) -> list[str]:
    """
    Extract top-level sections with their indented content.

    The input is split into sections where a non-indented line starts a new
    section. Following indented non-empty lines are considered part of the
    section. Sections without indented content are ignored.

    Args:
        s: Input text.

    Returns:
        A list of section strings, each containing a header and its
        indented lines.

    Examples:
        Input::

            section 1
              line 1
              line 2

            section 2
              line 3

        Returns::

            [
                "section 1\\n  line 1\\n  line 2",
                "section 2\\n  line 3",
            ]
    """
    r = []
    cr = []
    for line in s.splitlines():
        if rx_notspace.match(line):
            if len(cr) > 1:
                r.append("\n".join(cr))
            cr = [line]
            continue
        if line:
            cr.append(line)
    if len(cr) > 1:
        r.append("\n".join(cr))
    return r


def parse_kv(kmap: dict[str, str], data: str, sep: str = ":") -> dict[str, str]:
    """
    Parse key-value pairs from text using a key mapping.

    Lines containing the separator are parsed as key-value pairs.
    Input keys are stripped, converted to lowercase, and mapped to
    output keys using ``kmap``. Unknown keys are ignored.

    Args:
        kmap: Mapping of input keys to output keys.
        data: Text containing key-value pairs.
        sep: Key-value separator. Defaults to ``":"``.

    Returns:
        Dictionary containing mapped keys and parsed string values.
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


def str_dict(d: dict[str, Any]) -> str:
    """
    Convert a dictionary to a comma-separated key=value string.

    Args:
        d: Mapping to convert.

    Returns:
        String containing dictionary entries formatted as
        ``key=value`` pairs separated by commas.
    """
    return ", ".join(f"{k}={v}" for k, v in d.items())


_seconds_multipliers = {
    "h": 3600,
    "d": 24 * 3600,
    "w": 7 * 24 * 3600,
    "m": 30 * 24 * 3600,
    "y": 365 * 24 * 3600,
}


def to_seconds(v: str) -> int:
    """
    Convert a time string to a number of seconds.

    Supported suffixes are:
    - ``h`` — hours
    - ``d`` — days
    - ``w`` — weeks
    - ``m`` — months (30 days)
    - ``y`` — years (365 days)

    Args:
        v: Time value as a string.

    Returns:
        Time value converted to seconds.

    Raises:
        ValueError: If the input value is not a valid integer time value.
    """
    multiplier = 1
    if v[-1:] in _seconds_multipliers:
        multiplier = _seconds_multipliers[v[-1]]
        v = v[:-1]
    try:
        return int(v) * multiplier
    except ValueError as e:
        msg = f"Invalid time: {v}"
        raise ValueError(msg) from e


def format_table(
    widths: Iterable[int],
    data: Sequence[Sequence[object]],
    sep: str = " ",
    hsep: str = " ",
) -> str:
    """
    Format tabular data as an aligned text table.

    The first row is treated as a header and is followed by a separator
    line. Column widths are automatically expanded to fit the longest
    value in each column.

    Args:
        widths: Initial minimum width for each column.
        data: Table rows. The first row is used as the header.
        sep: Separator between columns.
        hsep: Separator used in the header underline.

    Returns:
        Formatted table as a string.
    """
    # Calculate column widths
    widths = list(widths)
    for row in data:
        widths = [max(x, len(str(y))) for x, y in zip(widths, row)]
    # Build print mask
    mask = sep.join(f"%-{int(w)}s" for w in widths)
    out = [
        # Header line
        mask % tuple(data[0]),
        # Header separator
        hsep.join("-" * w for w in widths),
    ]
    out += [mask % tuple(row) for row in data[1:]]
    return "\n".join(out)


rx_non_numbers = re.compile("[^0-9]+")


def clean_number(n: str) -> str:
    """
    Remove all non-digit characters from a string.

    Args:
        n: Input string containing digits and other characters.

    Returns:
        String containing only decimal digits.
    """
    return rx_non_numbers.sub("", n)


def safe_shadow(text: object) -> str:
    """
    Mask sensitive text while preserving first and last characters.

    Non-string values and short strings are replaced with a fixed mask.
    Empty values are represented as ``"None"``.

    Args:
        text: Value to mask.

    Returns:
        Masked string representation.

    Examples:
        ``"secret"`` -> ``"s******t"``
        ``"x"`` -> ``"******"``
        ``None`` -> ``"None"``
    """
    if not text:
        return "None"
    if not isinstance(text, str):
        return "******"
    if len(text) > 2:
        return f"{text[0]}******{text[-1]}"
    return "******"


def ch_escape(s: str) -> str:
    """
    Escape characters for ClickHouse string literals.

    Escapes newline and tab characters using ClickHouse-compatible escape
    sequences and escapes backslashes.

    Args:
        s: Input string.

    Returns:
        String with characters escaped for ClickHouse.
    """
    return s.replace("\n", "\\n").replace("\t", "\\t").replace("\\", "\\\\")


ESC_REPLACEMENTS = {re.escape("\n"): " ", re.escape("\t"): "        "}

rx_escape = re.compile("|".join(ESC_REPLACEMENTS))


def tsv_escape(text: str) -> str:
    """
    Escape characters that are not allowed in TSV fields.

    Replaces newline characters with spaces and tab characters with spaces
    to keep field boundaries intact.

    Args:
        text: Input field value.

    Returns:
        Escaped text suitable for TSV output.
    """
    return rx_escape.sub(lambda match: ESC_REPLACEMENTS[re.escape(match.group(0))], text)


def parse_table_header(v: Sequence[str]) -> dict[int, str]:
    """
    Parse a multiline table header into column names.

    The input contains multiple header lines. Columns are detected by
    their character positions and vertically merged into complete names.

    Args:
        v: Header lines.

    Returns:
        Mapping of column start positions to parsed column names.

    Examples:
        Given the following multiline header::

            Config    Current Agg     Min    Ld Share  Flags Ld Share  Agg Link  Link Up
            Master    Master  Control Active Algorithm       Group     Mbr State Transitions

        returns::

            {
                10: "Config Master",
                18: "Current Master",
                26: "Agg Control",
                33: "Min Active",
                43: "Ld Share Algorithm",
                49: "Flags",
                59: "Ld Share Group",
                63: "Agg Mbr",
                69: "Link State",
            }
    """
    from numpy import array

    head = []
    empty_header = None
    header = {}
    for num, lines in enumerate(zip_longest(*v, fillvalue="-")):
        if empty_header is None:
            empty_header = (" ",) * len(lines)
            head.append(lines)
            continue
        if set(head[-1]) == {" "} and lines != empty_header:
            head = array(head)
            # Transpone list header string
            header[num] = " ".join(["".join(s).strip() for s in head.transpose().tolist()])
            header[num] = header[num].strip()
            head = []
        head.append(lines)
    # last column
    head = array(head)
    header[num] = " ".join(["".join(s).strip(" -") for s in head.transpose().tolist()])
    header[num] = header[num].strip()
    return header


def split_text(text: str, max_chunk: int) -> Iterator[str]:
    """
    Split text into chunks by line boundaries.

    Lines are accumulated until adding another line would exceed
    the specified maximum chunk size. Chunks preserve original line
    separation.

    Args:
        text: Input text.
        max_chunk: Maximum chunk size in characters.

    Yields:
        Text chunks containing one or more complete lines.
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
    """
    Remove non-printable characters from a string.

    Args:
        text: Input string.

    Returns:
        String containing only printable characters.
    """
    return "".join(x for x in text if x in string.printable)


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
    """
    Transliterate Cyrillic characters to Latin characters.

    Cyrillic letters are replaced according to the transliteration table.
    Spaces are replaced with underscores; all other characters are preserved.

    Args:
        s: Input string.

    Returns:
        Transliterated string.
    """
    r: list[str] = []
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


def find_balanced(s: str, /, start: int = 0, closing: str = ")") -> int:
    """
    Find balanced closing symbol's index.

    Symbol at `start` position considered an "opening bracked".
    Function tracks all opening and closing braces until the
    matching pair for open brace found.

    Args:
        s: String to search.
        start: Starting position, symbol in this posiiton
            is an "opening brace".
        closing: Closing brace symbol.

    Returns:
        index of closing brace: if matched.
        -1: otherwise
    """
    n = 1
    opening = s[start]
    for i in range(start + 1, len(s)):
        match s[i]:
            case c if c == opening:
                n += 1
            case c if c == closing:
                n -= 1
                if not n:
                    return i
            case _:
                pass
    return -1
