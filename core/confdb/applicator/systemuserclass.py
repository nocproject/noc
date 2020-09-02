# ----------------------------------------------------------------------
# DefaultAdminStatusApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultUserClassApplicator(QueryApplicator):
    """
    В случае отсутствия user-class, выставляется значение по умолчанию, задаваемое в profile
    """

    CHECK_QUERY = "Match('hints', 'system', 'user', 'defaults', 'class')"
    QUERY = [
        "Match('hints', 'system', 'user', 'defaults', 'class', default_class) and "
        "NotMatch('system', 'user', X, 'class') and "
        "Fact('system', 'user', X, 'class', default_class)"
    ]
