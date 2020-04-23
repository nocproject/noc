# ----------------------------------------------------------------------
# DefaultForwardingInstanceTypeApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultForwardingInstanceTypeApplicator(QueryApplicator):
    """
    Set forwarding instance type if not set
    """

    QUERY = [
        "Match('virtual-router', vr, 'forwarding-instance', fi) and "
        "NotMatch('virtual-router', vr, 'forwarding-instance', fi, 'type') and "
        "Fact('virtual-router', vr, 'forwarding-instance', fi, 'type', default)"
    ]
    CONFIG = {"default": "table"}
