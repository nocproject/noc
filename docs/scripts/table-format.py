#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReST table formatter
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

T_SINGLE = 1  # Single table line
T_DOUBLE = 2  # Double table line
T_ROW = 3  # Table row


def iter_tokens(input):
    """
    Generator yielding <type>, <data>
    :param input: File object
    :return:
    """
    for line in input:
        line = line.strip()
        if not line:
            continue
        if line.startswith("+-"):
            yield T_SINGLE, None
        elif line.startswith("+="):
            yield T_DOUBLE, None
        elif "|" in line:
            yield T_ROW, [x.strip() for x in line.split("|")][1:-1]


def iter_format_table(input):
    """
    Reformat ReST tables and yield table lines

    :param input:
    :return:
    """
    # Column widths
    widths = []
    # Table tokens
    table = []
    # Parse table
    for token, tdata in iter_tokens(input):
        if token == T_ROW:
            # Calculate widths
            if len(widths) < len(tdata):
                widths += [0] * (len(tdata) - len(widths))
            for i, c in enumerate(tdata):
                widths[i] = max(widths[i], len(c))
        table += [(token, tdata)]
    # Build single line
    sl = "+%s+" % "+".join("-" * (w + 2) for w in widths)
    # Build double line
    dl = sl.replace("-", "=")
    # Format tab
    fmt = [" %%-%ds " % w for w in widths]
    # Reformat table
    for token, tdata in table:
        if token == T_SINGLE:
            yield sl
        elif token == T_DOUBLE:
            yield dl
        elif token == T_ROW:
            row = tdata
            if len(row) < len(widths):
                # Enlarge
                row += [""] * (len(widths) - len(row))
            yield "|%s|" % "|".join(f % x for f, x in zip(fmt, row))


def format(input, output):
    """
    Receive table from input and write to output
    :param input: File object
    :param output: File object
    :return:
    """
    for line in iter_format_table(input):
        output.write(line + "\n")


if __name__ == "__main__":
    import sys
    format(sys.stdin, sys.stdout)
