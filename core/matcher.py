# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Expression matcher
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.lib.text import split_alnum

__all__ = ["match"]


def match(ctx, expr):
    """
    Returns True if context *ctx* matches against expression *expr*
    :param ctx: dict of context variables
    :param expr: dict of expression
    :return:
    """
    if "$or" in expr:
        for x in expr["$or"]:
            if match(ctx, x):
                return True
        return False
    else:
        for x in expr:
            if x not in ctx:
                return False
            if isinstance(expr[x], dict):
                for m in expr[x]:
                    mf = matchers.get(m)
                    if mf:
                        if not mf(ctx[x], expr[x][m]):
                            return False
                    else:
                        return False
            elif ctx.get(x) != expr[x]:
                return False
        return True


def match_regex(v, rx):
    return bool(re.search(rx, v))


def match_in(v, iter):
    return v in iter


def match_gt(v, cv):
    return split_alnum(v) > split_alnum(cv)


def match_gte(v, cv):
    return split_alnum(v) >= split_alnum(cv)


def match_lt(v, cv):
    return split_alnum(v) < split_alnum(cv)


def match_lte(v, cv):
    return split_alnum(v) <= split_alnum(cv)


matchers = {
    "$regex": match_regex,
    "$in": match_in,
    "$gt": match_gt,
    "$gte": match_gte,
    "$lt": match_lt,
    "$lte": match_lte
}
