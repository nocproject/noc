# ----------------------------------------------------------------------
# DefaultSTPStatusApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultSTPStatusApplicator(QueryApplicator):
    """
    Apply STP on interfaces
    """

    CHECK_QUERY = "Match('hints', 'protocols', 'spanning-tree', 'status')"
    QUERY = [
        # STP is globally enabled
        "Match('hints', 'protocols', 'spanning-tree', 'status', True) and "
        # Get all physical interfaces and bind to variable X
        "Match('interfaces', X, 'type', 'physical') and "
        # Only admin-status up interfaces
        "Match('interfaces', X, 'admin-status', True) and "
        # Filter out explicitly disabled interfaces
        "NotMatch('hints', 'protocols', 'spanning-tree', 'interface', X, 'off') and "
        # For each interface with stp admin status is not set
        "NotMatch('protocols', 'spanning-tree', 'interface', X, 'admin-status') and "
        # Set stp admin-status to rx and tx
        "Fact('protocols', 'spanning-tree', 'interface', X, 'admin-status', 'on')"
    ]
