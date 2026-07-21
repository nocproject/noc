# ----------------------------------------------------------------------
# Various testing utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from typing import Any

# NOC modules
from noc.core.hash import dict_hash_int
from noc.core.confdb.engine.base import Engine


def check_query(query: str, args: dict[str, Any], expected: list[dict[str, Any]]) -> bool:
    """
    ConfDB Query result order is undefined,
    so we need additional helper to check
    if all results matched

    :return:
    """
    e = Engine()
    left: dict[int, dict[str, Any]] = {dict_hash_int(ctx): ctx for ctx in expected}
    not_found: set[dict[str, Any]] = set()
    for ctx in e.query(query, **args):
        ctx_hash = dict_hash_int(ctx)
        if ctx_hash in left:
            del left[ctx_hash]
        else:
            not_found.add(ctx)
    for ctx_hash in not_found:
        print(f"Unexpected return result: {not_found[ctx_hash]}")
    for ctx in left:
        print(f"Missed result:  {ctx}")
    return not left and not not_found
