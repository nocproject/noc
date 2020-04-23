# ----------------------------------------------------------------------
# CollapseTaggedApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class CollapseTaggedApplicator(QueryApplicator):
    QUERY = [
        "Collapse("
        "  'virtual-router', vr,"
        "  'forwarding-instance', fi,"
        "  'interface', iface,"
        "  'unit', uint,"
        "  'bridge', 'switchport', 'tagged',"
        " joinrange=',')"
    ]
