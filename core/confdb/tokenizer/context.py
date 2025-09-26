# ----------------------------------------------------------------------
# Context tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .line import LineTokenizer


class ContextTokenizer(LineTokenizer):
    name = "context"

    def __init__(self, data, end_of_context=None, contexts=None, **kwargs):
        super().__init__(data, **kwargs)
        self.end_of_context = end_of_context
        self.contexts = contexts or []

    def is_matched(self, tokens):
        """
        Check tokens exactly matched context
        :param tokens:
        :return:
        """
        lt = len(tokens)
        for ctx in self.contexts:
            if len(ctx) != lt:
                continue
            matched = True
            for t, ct in zip(tokens, ctx):
                if ct is None:
                    continue
                if hasattr(ct, "match"):
                    # Regexp
                    if not ct.match(t):
                        matched = False
                        break
                elif t != ct:
                    matched = False
                    break
            if matched:
                return True
        return False

    def __iter__(self):
        contexts = []
        for tokens in super().__iter__():
            # Process end of context
            if self.end_of_context and contexts and tokens[0] == self.end_of_context:
                contexts.pop(-1)
                continue
            # Apply current context
            if contexts:
                tokens = contexts[-1] + tokens
            # Check for new context
            if self.is_matched(tokens):
                contexts += [tokens]
            yield tokens
