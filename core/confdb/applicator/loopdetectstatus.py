# ----------------------------------------------------------------------
# DefaultLoopDetectStatusApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultLoopDetectStatusApplicator(QueryApplicator):
    """
    Apply loop-detect status
    """

    CHECK_QUERY = "Match('hints', 'protocols', 'loop-detect', 'status')"
    QUERY = [
        # loop-detect is globally enabled
        "Match('hints', 'protocols', 'loop-detect', 'status', True) and "
        # Get all physical interfaces and bind to variable X
        "Match('interfaces', X, 'type', 'physical') and "
        # Only admin-status up interfaces
        "Match('interfaces', X, 'admin-status', True) and "
        # Filter out explicitly disabled interfaces
        "NotMatch('hints', 'protocols', 'loop-detect', 'interface', X, 'off') and "
        # For each interface with loop-detect interface is not set
        "NotMatch('protocols', 'loop-detect', 'interface', X) and "
        # Set loop-detect interface
        "Fact('protocols', 'loop-detect', 'interface', X)"
    ]
