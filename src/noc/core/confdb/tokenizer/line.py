# ----------------------------------------------------------------------
# line tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from collections.abc import Iterator, Iterable

# NOC modules
from .base import BaseTokenizer


class LineTokenizer(BaseTokenizer):
    """Line tokenizer. Splits line to tokens"""

    name = "line"
    rx_indent = re.compile(r"^\s+")

    def __init__(
        self,
        data: str,
        eol: str = "\n",
        tab_width: int = 0,
        line_comment: str | None = None,
        inline_comment: str | None = None,
        keep_indent: bool = False,
        string_quote: str | None = None,
        rewrite=None,
    ):
        super().__init__(data)
        self.eol = eol
        self.tab_width = tab_width
        self.line_comment = line_comment
        self.inline_comment = inline_comment
        self.keep_indent = keep_indent
        self.string_quote = string_quote
        self.rewrite = rewrite

    def iter_lines(self) -> Iterator[tuple[str]]:
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

    def iter_line_comments(self, iter: Iterable) -> Iterator[tuple[str]]:
        for line in iter:
            if not line.lstrip().startswith(self.line_comment):
                yield line

    def iter_inline_comments(self, iter: Iterable) -> Iterator[tuple[str]]:
        for line in iter:
            i = line.find(self.inline_comment)
            if i != -1:
                line = line[:i]
            yield line

    def iter_not_empty(self, iter: Iterable) -> Iterator[tuple[str]]:
        for line in iter:
            if line.strip():
                yield line

    def iter_untabify(self, iter: Iterable) -> Iterator[tuple[str]]:
        tr = " " * self.tab_width
        for line in iter:
            yield line.replace("\t", tr)

    def iter_rewrite(self, iter: Iterable[str]) -> Iterator[tuple[str]]:
        """Apply `rewrite`

        Args:
            iter
        """
        for line in iter:
            for pattern, repl in self.rewrite:
                line, n = pattern.subn(repl, line)
                if n:
                    break
            yield line

    def iter_line_tokens(self, line: str) -> Iterator[tuple[str]]:
        """Iterate line tokens.

        Args:
            line: Input line.

        Returns:
            Yields tuples of tokens.
        """
        if self.keep_indent:
            match = self.rx_indent.match(line)
            if match:
                yield match.group(0)
                line = line[match.end() :]
        yield from line.split()

    def iter_line_quoted_tokens(self, line: str) -> Iterator[tuple[str]]:
        """Iterate line tokens considering strings.

        Args:
            line: Input line.

        Returns:
            Yields tuples of tokens.
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
                    yield from line[start : qi - 1].split()
                    in_string = True
                start = qi + 1
        else:
            # No quoted strings
            yield from line.split()

    def __iter__(self) -> Iterator[tuple[str]]:
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
            if tokens := tuple(g_tokens(line)):
                yield tokens
