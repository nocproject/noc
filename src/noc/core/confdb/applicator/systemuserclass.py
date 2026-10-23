# ----------------------------------------------------------------------
# DefaultAdminStatusApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultUserClassApplicator(QueryApplicator):
    """In case of absence of user-class, get defaults from profile."""

    CHECK_QUERY = "Match('hints', 'system', 'user', 'defaults', 'class')"
    QUERY = [
        "Match('hints', 'system', 'user', 'defaults', 'class', default_class) and "
        "NotMatch('system', 'user', X, 'class') and "
        "Fact('system', 'user', X, 'class', default_class)"
    ]
