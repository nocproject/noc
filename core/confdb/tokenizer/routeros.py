# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# routeros tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import re

# NOC modules
from noc.core.validators import is_int
from .line import LineTokenizer


class RouterOSTokenizer(LineTokenizer):
    name = "routeros"
    rx_param = re.compile(r'([^= ]+="[^"]+"|[^= ]+=\S+|\S+)')

    def iter_context(self, context, tokens):
        for token in tokens:
            if "=" not in token:
                continue
            k, v = token.split("=", 1)
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            yield context + (k, v)

    def iter_line_tokens(self, line):
        """
        Iterate line tokens
        :param line:
        :return:
        """
        for match in self.rx_param.finditer(line):
            yield match.group(0)

    def __iter__(self):
        g = super(RouterOSTokenizer, self).__iter__()
        context = None
        context_fed = False
        n_item = 0
        for tokens in g:
            if tokens[0].startswith("/"):
                # New context
                if context and not context_fed:
                    yield context
                context = tokens
                context_fed = False
                n_item = 0
                continue
            if tokens[0] == "set" and len(tokens) > 1:
                # Process set instruction
                if (
                    tokens[1] == "["
                    and len(tokens) > 4
                    and tokens[2] == "find"
                    and tokens[4] == "]"
                ):
                    # set [ find key=value ] ...
                    item = tokens[3].split("=", 1)[1]
                    for ct in self.iter_context(context + (item,), tokens[5:]):
                        yield ct
                elif is_int(tokens[1]):
                    # set 0 ...
                    for ct in self.iter_context(context + (tokens[1],), tokens[2:]):
                        yield ct
                else:
                    # set XXX
                    for ct in self.iter_context(context, tokens[1:]):
                        yield ct
                context_fed = True
            if tokens[0] == "add" and len(tokens) > 1:
                # Process add instruction
                for ct in self.iter_context(context + (str(n_item),), tokens[1:]):
                    yield ct
                context_fed = True
                n_item += 1
        # Yield last context if not already yielded
        if context and not context_fed:
            yield context
