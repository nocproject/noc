# ----------------------------------------------------------------------
# DefaultSTPPriorityApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultSTPPriorityApplicator(QueryApplicator):
    """
    Set platform's STP priority if not set explicitly
    """

    CHECK_QUERY = (
        "Match('hints', 'protocols', 'spanning-tree', 'status') and "
        "Match('hints', 'protocols', 'spanning-tree', 'priority')"
    )
    QUERY = [
        # STP is globally enabled
        "Match('hints', 'protocols', 'spanning-tree', 'status', 'on') and "
        # Global priority is set
        "Match('hints', 'protocols', 'spanning-tree', 'priority', X) and "
        # And priority is not configured
        "NotMatch('protocols', 'spanning-tree', 'priority') and "
        # Set priority
        "Fact('protocols', 'spanning-tree', 'priority', X)"
    ]
