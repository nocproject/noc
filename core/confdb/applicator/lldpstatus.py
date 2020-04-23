# ----------------------------------------------------------------------
# DefaultLLDPStatusApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultLLDPStatusApplicator(QueryApplicator):
    """
    Apply non-disabled LLDP interfaces
    """

    CHECK_QUERY = "Match('hints', 'protocols', 'lldp', 'status')"
    QUERY = [
        # LLDP is globally enabled
        "Match('hints', 'protocols', 'lldp', 'status', 'on') and "
        # Get all physical interfaces and bind to variable X
        "Match('interfaces', X, 'type', 'physical') and "
        # Only admin-status up interfaces
        "Match('interfaces', X, 'admin-status', 'on') and "
        # Filter out explicitly disabled interfaces
        "NotMatch('hints', 'protocols', 'lldp', 'interface', X, 'off') and "
        # For each interface with lldp admin status is not set
        "NotMatch('protocols', 'lldp', 'interface', X, 'admin-status') and "
        # Set lldp admin-status to rx and tx
        "Fact('protocols', 'lldp', 'interface', X, 'admin-status', 'tx') and "
        "Fact('protocols', 'lldp', 'interface', X, 'admin-status', 'rx')"
    ]
