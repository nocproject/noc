# ----------------------------------------------------------------------
# DefaultCDPStatusApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultCDPStatusApplicator(QueryApplicator):
    """
    Apply non-disabled CDP interfaces
    """

    CHECK_QUERY = "Match('hints', 'protocols', 'cdp', 'status')"
    QUERY = [
        # CDP is globally enabled
        "Match('hints', 'protocols', 'cdp', 'status', 'on') and "
        # Get all physical interfaces and bind to variable X
        "Match('interfaces', X, 'type', 'physical') and "
        # Only admin-status up interfaces
        "Match('interfaces', X, 'admin-status', 'on') and "
        # Filter out explicitly disabled interfaces
        "NotMatch('hints', 'protocols', 'cdp', 'interface', X, 'off') and "
        # For each interface with cdp admin status is not set
        "NotMatch('protocols', 'cdp', 'interface', X) and "
        # Set stp admin-status to rx and tx
        "Fact('protocols', 'cdp', 'interface', X)"
    ]
