# ----------------------------------------------------------------------
# Expression matcher
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from typing import Iterable

# NOC modules
from noc.core.text import alnum_key


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
            # iter matchers expression - caps, version, platform, vendor
            if x not in ctx:
                return False
            if isinstance(expr[x], dict):
                for m in expr[x]:
                    if ctx[x] is None:
                        continue
                    mf = matchers.get(m)
                    if mf and not isinstance(expr[x][m], tuple):
                        if not mf(ctx[x], expr[x][m]):
                            return False
                    elif mf and isinstance(expr[x][m], tuple) and expr[x][m][0] in ctx[x]:
                        # if caps matchers: "caps": {"$gte": ("DB | Interfaces", 40)}
                        if not mf(str(ctx[x][expr[x][m][0]]), str(expr[x][m][1])):
                            return False
                    else:
                        return False
            elif ctx.get(x) != expr[x]:
                return False
        return True


def match_regex(v, rx):
    return bool(re.search(rx, v))


def match_all(v, iter):
    """
    All logic
    :param v: Caps
    :param iter: Matcher value
    :return:
    """
    if isinstance(v, str):
        return str(v) in iter
    if isinstance(v, Iterable):
        # if v list - check all
        return not bool(set(iter) - set(v))
    return False


def match_in(v, iter):
    if isinstance(v, str):
        return str(v) in iter
    if isinstance(v, Iterable):
        # if v list - check intersection
        return bool(set(v).intersection(set(iter)))
    return False


def match_gt(v, cv):
    return alnum_key(v) > alnum_key(cv)


def match_gte(v, cv):
    return alnum_key(v) >= alnum_key(cv)


def match_lt(v, cv):
    return alnum_key(v) < alnum_key(cv)


def match_lte(v, cv):
    return alnum_key(v) <= alnum_key(cv)


matchers = {
    "$regex": match_regex,
    "$in": match_in,
    "$all": match_in,
    "$gt": match_gt,
    "$gte": match_gte,
    "$lt": match_lt,
    "$lte": match_lte,
}
