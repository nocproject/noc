# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Various testing utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function

# Third-party modules
import six
from typing import List, Dict, Set, Any

# NOC modules
from noc.core.hash import dict_hash_int
from noc.core.confdb.engine.base import Engine


def check_query(query, args, expected):
    # type: (six.text_type, Dict[six.text_type, Any], List[Dict[six.text_type, Any]]) -> bool
    """
    ConfDB Query result order is undefined,
    so we need additional helper to check
    if all results matched

    :param query:
    :param args:
    :param expected:
    :return:
    """
    e = Engine()
    left = {
        dict_hash_int(ctx): ctx for ctx in expected
    }  # type: Dict[int, Dict[six.text_type, Any]]
    not_found = set()  # type: Set[Dict[six.text_type, Any]]
    for ctx in e.query(query, **args):
        ctx_hash = dict_hash_int(ctx)
        if ctx_hash in left:
            del left[ctx_hash]
        else:
            not_found.add(ctx)
    for ctx_hash in not_found:
        print("Unexpected return result: %s" % not_found[ctx_hash])
    for ctx in left:
        print("Missed result:  %s" % ctx)
    return not left and not not_found
