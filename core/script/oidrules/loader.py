# ----------------------------------------------------------------------
# OID Rule Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional, Callable

cv_oid_rule_resolver: ContextVar[Optional[Callable]] = ContextVar(
    "cv_oid_rule_resolver", default=None
)


@contextmanager
def with_resolver(resolver):
    """
    OIDRule resolver context.

    :param resolver: callable accepting name and returning
        OIDRule class with given type
    :return:
    """
    cv_oid_rule_resolver.set(resolver)
    yield
    cv_oid_rule_resolver.set(None)


def load_rule(data):
    """
    Create OIDRule instance from data structure.
    MUST be called within resolver_context
    :param data: parsed from json file
    :return:
    """
    resolver = cv_oid_rule_resolver.get()
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
