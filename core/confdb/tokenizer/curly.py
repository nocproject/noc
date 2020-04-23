# ----------------------------------------------------------------------
# curly tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .line import LineTokenizer


class CurlyTokenizer(LineTokenizer):
    name = "curly"

    def __init__(self, data, start_of_context="{", end_of_context="}", explicit_eol=None, **kwargs):
        self.start_of_context = start_of_context
        self.end_of_context = end_of_context
        self.explicit_eol = explicit_eol
        super(CurlyTokenizer, self).__init__(data, **kwargs)

    def iter_strip_explicit_eol(self, iter):
        l_eol = len(self.explicit_eol)
        for tokens in iter:
            if tokens[-1].endswith(self.explicit_eol):
                tokens = tokens[:-1] + (tokens[-1][:-l_eol],)
            yield tokens

    def __iter__(self):
        contexts = []
        eoc = (self.end_of_context,)
        g = super(CurlyTokenizer, self).__iter__()
        if self.explicit_eol:
            g = self.iter_strip_explicit_eol(g)
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
            yield tokens
