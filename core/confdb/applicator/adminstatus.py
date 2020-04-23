# ----------------------------------------------------------------------
# DefaultAdminStatusApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultAdminStatusApplicator(QueryApplicator):
    """
    Set missed interface's AdminStatus from "hints interfaces defaults admin-status"
    """

    CHECK_QUERY = "Match('hints', 'interfaces', 'defaults', 'admin-status')"
    QUERY = [
        "Match('hints', 'interfaces', 'defaults', 'admin-status', default_status) and "
        "NotMatch('interfaces', X, 'admin-status') and "
        "Fact('interfaces', X, 'admin-status', default_status)"
    ]
