# ----------------------------------------------------------------------
# curly tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Iterable, Iterator, Tuple

# NOC modules
from .line import LineTokenizer


class CurlyTokenizer(LineTokenizer):
    name = "curly"

    def __init__(
        self,
        data,
        start_of_context: str = "{",
        end_of_context: str = "}",
        explicit_eol: Optional[str] = None,
        start_of_group: Optional[str] = None,
        end_of_group: Optional[str] = None,
        **kwargs,
    ):
        self.start_of_context = start_of_context
        self.end_of_context = end_of_context
        self.explicit_eol = explicit_eol
        self.start_of_group = start_of_group
        self.end_of_group = end_of_group
        super().__init__(data, **kwargs)

    def iter_strip_explicit_eol(self, iter: Iterable) -> Iterator[Tuple[str]]:
        l_eol = len(self.explicit_eol)
        for tokens in iter:
            if tokens[-1].endswith(self.explicit_eol):
                tokens = (*tokens[:-1], tokens[-1][:-l_eol])
            yield tokens

    def repeat_groups(self, tokens: Tuple[str]) -> Iterator[Tuple[str]]:
        if tokens[-1] == self.end_of_group and self.start_of_group in tokens:
            idx = tokens.index(self.start_of_group)
            prefix = tokens[:idx]
            for item in tokens[idx + 1 : -1]:
                yield (*prefix, item)
        else:
            yield tokens

    def __iter__(self) -> Iterator[Tuple[str]]:
        contexts = []
        eoc = (self.end_of_context,)
        g = super().__iter__()
        if self.explicit_eol:
            g = self.iter_strip_explicit_eol(g)
        to_repeat = self.start_of_group is not None and self.end_of_group is not None
        for tokens in g:
            if tokens == eoc:
                # Pop context
                contexts.pop(-1)
                continue
            if contexts:
                tokens = contexts[-1] + tokens
            if tokens[-1] == self.start_of_context:
                # Push context
                tokens = tokens[:-1]
                contexts += [tokens]
            if to_repeat:
                yield from self.repeat_groups(tokens)
            else:
                yield tokens
