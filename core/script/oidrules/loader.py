# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# OID Rule Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
from contextlib import contextmanager

_tls = threading.local()


@contextmanager
def with_resolver(resolver):
    """
    OIDRule resolver context.

    :param resolver: callable accepting name and returning
        OIDRule class with given type
    :return:
    """
    _tls._oid_rule_resolver = resolver
    yield
    del _tls._oid_rule_resolver


def load_rule(data):
    """
    Create OIDRule instance from data structure.
    MUST be called within resolver_context
    :param data: parsed from json file
    :return:
    """
    resolver = getattr(_tls, "_oid_rule_resolver", None)
    assert resolver, "Should be calles within with_resolver context"
    if not isinstance(data, dict):
        raise ValueError("object required")
    if "$type" not in data:
        raise ValueError("$type key is required")
    t = data["$type"]
    rule = resolver(t)
    if not rule:
        raise ValueError("Invalid $type '%s'" % t)
    return rule.from_json(data)
