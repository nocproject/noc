# ----------------------------------------------------------------------
# Function matcher
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from functools import partial
from typing import List, Tuple, FrozenSet, Callable, Dict, Any, Union, Iterable

# NOC Modules
from noc.core.text import alnum_key


def match(ctx: Dict[str, Union[List, str, int]], expr: Dict[str, Any]) -> bool:
    return build_matcher(expr)(ctx)


def get_matcher(op: str, field: str, value: Any) -> Callable:
    """getting matcher function by operation"""
    if op not in matchers:
        raise ValueError("Unknown matcher: %s", op)
    # Clean Argument
    match op:
        case "$regex":
            value = re.compile(value)
        case "$in" | "$all" | "$any":
            value = frozenset(str(v) for v in value)
        case "$eq":
            value = value
        case _:
            value = alnum_key(value)
    return partial(matchers[op], value, field)


def iter_matchers(expr: Dict[str, Any]) -> Iterable[Callable]:
    for field, matcher in expr.items():
        if field == "$or":
            yield partial(match_or, (build_matcher(m) for m in matcher))
        elif not isinstance(matcher, dict):
            yield partial(match_eq, matcher, field)
        else:
            for op, value in matcher.items():
                yield get_matcher(op, field, value)


def build_matcher(expr: Dict[str, Any]) -> Callable:
    """Build matcher function by expression"""
    # If not tuple, matcher works one time
    return partial(match_and, tuple(iter_matchers(expr)))


def match_or(c_iter: Tuple[Callable, ...], ctx: Dict[str, Any]) -> bool:
    for c in c_iter:
        try:
            if c(ctx):
                return True
        except KeyError:
            return False
    return False


def match_and(c_iter: Tuple[Callable, ...], ctx: Dict[str, Any]) -> bool:
    for c in c_iter:
        try:
            if not c(ctx):
                return False
        except KeyError:
            return False
    return True


def match_regex(rx: re.Pattern, field: str, ctx: Dict[str, Any]) -> bool:
    return bool(rx.search(ctx[field]))


def match_in(c_iter: FrozenSet, field: str, ctx: Dict[str, Any]) -> bool:
    return str(ctx[field]) in c_iter


def match_all(c_iter: FrozenSet, field: str, ctx: Dict[str, Any]) -> bool:
    return not bool(c_iter - set(ctx[field]))


def match_any(c_iter: FrozenSet, field: str, ctx: Dict[str, Any]) -> bool:
    return bool(set(ctx[field]).intersection(c_iter))


def match_gt(cv: str, field: str, ctx: Dict[str, Any]) -> bool:
    return alnum_key(ctx[field]) > cv


def match_gte(cv: str, field: str, ctx: Dict[str, Any]) -> bool:
    return alnum_key(ctx[field]) >= cv


def match_lt(cv: str, field: str, ctx: Dict[str, Any]) -> bool:
    return alnum_key(ctx[field]) < cv


def match_lte(cv: str, field: str, ctx: Dict[str, Any]) -> bool:
    return alnum_key(ctx[field]) <= cv


def match_eq(cv: str, field: str, ctx: Dict[str, Any]) -> bool:
    return ctx[field] == cv


matchers = {
    "$regex": match_regex,
    "$in": match_in,
    "$any": match_any,
    "$all": match_all,
    "$gt": match_gt,
    "$gte": match_gte,
    "$lt": match_lt,
    "$lte": match_lte,
    "$eq": match_eq,
}
