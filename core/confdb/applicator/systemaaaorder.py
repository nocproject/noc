# ----------------------------------------------------------------------
# DefaultSystemAAAOrderApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultSystemAAAOrderApplicator(QueryApplicator):
    """
    Set forwarding instance type if not set
    """

    QUERY = [
        "Match('system', 'aaa', 'service', 'local') and "
        "NotMatch('system', 'aaa', 'order', 'local') and "
        "Fact('system', 'aaa', 'order', 'local')"
    ]
