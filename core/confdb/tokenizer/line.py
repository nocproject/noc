# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# line tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from .base import BaseTokenizer


class LineTokenizer(BaseTokenizer):
    """
    Line tokenizer. Splits line to tokens
    """

    name = "line"
    rx_indent = re.compile(r"^\s+")

    def __init__(
        self,
        data,
        eol="\n",
        tab_width=0,
        line_comment=None,
        inline_comment=None,
        keep_indent=False,
        string_quote=None,
        rewrite=None,
    ):
        super(LineTokenizer, self).__init__(data)
        self.eol = eol
        self.tab_width = tab_width
        self.line_comment = line_comment
        self.inline_comment = inline_comment
        self.keep_indent = keep_indent
        self.string_quote = string_quote
        self.rewrite = rewrite

    def iter_lines(self):
        dl = len(self.data)
        i = 0
        leol = len(self.eol)
        while i < dl:
            ni = self.data.find(self.eol, i)
            if ni == -1:
                yield self.data[i:]
                break
            yield self.data[i:ni]
            i = ni + leol

    def iter_line_comments(self, iter):
        for line in iter:
            if not line.lstrip().startswith(self.line_comment):
                yield line

    def iter_inline_comments(self, iter):
        for line in iter:
            i = line.find(self.inline_comment)
            if i != -1:
                line = line[:i]
            yield line

    def iter_not_empty(self, iter):
        for line in iter:
            if line.strip():
                yield line

    def iter_untabify(self, iter):
        tr = " " * self.tab_width
        for line in iter:
            yield line.replace("\t", tr)

    def iter_rewrite(self, iter):
        """
        Apply `rewrite`
        :param iter:
        :return:
        """
        for line in iter:
            for pattern, repl in self.rewrite:
                line, n = pattern.subn(repl, line)
                if n:
                    break
            yield line

    def iter_line_tokens(self, line):
        """
        Iterate line tokens
        :param line:
        :return:
        """
        if self.keep_indent:
            match = self.rx_indent.match(line)
            if match:
                yield match.group(0)
                line = line[match.end() :]
        yield from line.split()

    def iter_line_quoted_tokens(self, line):
        """
        Iterate line tokens considering strings
        :param line:
        :return:
        """
        if self.keep_indent:
            match = self.rx_indent.match(line)
            if match:
                yield match.group(0)
                line = line[match.end() :]
        if self.string_quote in line:
            # Quoted strings
            start = 0
            llen = len(line)
            in_string = False
            while start < llen:
                qi = line.find(self.string_quote, start)
                if qi == -1:
                    qi = llen + 1
                if in_string:
                    yield line[start:qi]
                    in_string = False
                else:
                    for li in line[start : qi - 1].split():
                        yield li
                    in_string = True
                start = qi + 1
        else:
            # No quoted strings
            yield from line.split()

    def __iter__(self):
        g = self.iter_lines()
        if self.tab_width:
            g = self.iter_untabify(g)
        if self.line_comment:
            g = self.iter_line_comments(g)
        if self.inline_comment:
            g = self.iter_inline_comments(g)
        g = self.iter_not_empty(g)
        if self.rewrite:
            g = self.iter_rewrite(g)
        if self.string_quote:
            g_tokens = self.iter_line_quoted_tokens
        else:
            g_tokens = self.iter_line_tokens
        for line in g:
            yield tuple(g_tokens(line))
