# ----------------------------------------------------------------------
# OID Rule Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from contextlib import contextmanager
from contextvars import ContextVar
from collections.abc import Callable

cv_oid_rule_resolver: ContextVar[Callable | None] = ContextVar("cv_oid_rule_resolver", default=None)


@contextmanager
def with_resolver(resolver):
    """OIDRule resolver context.

    Args:
        resolver: callable accepting name and returning OIDRule class
            with given type
    """
    cv_oid_rule_resolver.set(resolver)
    yield
    cv_oid_rule_resolver.set(None)


def load_rule(data):
    """Create OIDRule instance from data structure.
    MUST be called within resolver_context

    Args:
        data: parsed from json file
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
        raise ValueError(f"Invalid $type '{t}'")
    return rule.from_json(data)
