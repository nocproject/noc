# ----------------------------------------------------------------------
# DefaultInterfaceUntaggedVlanApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultInterfaceUntaggedVlanApplicator(QueryApplicator):
    """
    Apply Default Untagged vlan on interfaces
    """

    QUERY = [
        # Get all physical interfaces and bind to variable X
        "Match('interfaces', X, 'type', 'physical') and "
        # Filter out explicitly disabled interfaces
        "NotMatch('hints', 'virtual-router', 'interfaces', 'untagged', 'default', X, 'off') and "
        # For each interface with untagged vlan is not set
        "NotMatch('virtual-router', vr, 'forwarding-instance', fi, 'interfaces', X, 'unit', X, 'bridge', 'switchport','untagged') and "
        # Set untagged vlan
        "Fact('virtual-router', vr, 'forwarding-instance', fi, 'interfaces', X, 'unit', X, 'bridge', 'switchport', 'untagged', default)"
    ]
    CONFIG = {"default": 1}
