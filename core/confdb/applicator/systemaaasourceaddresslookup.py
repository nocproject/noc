# ----------------------------------------------------------------------
# DefaultAAASourceAddressApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultAAASourceAddressLookupApplicator(QueryApplicator):
    """
    Lookup source-address hints from default-interface
    """

    CHECK_QUERY = (
        "NotMatch('hints', 'system', 'aaa', 'service-type', stype, 'default-address') and"
        " Match('hints', 'system', 'aaa', 'service-type', stype, 'default-interface')"
    )
    QUERY = [
        # Getting source-ip from interface address by default-interface
        "((Match('hints', 'system', 'aaa', 'service-type', stype, 'default-interface', interface) and "
        " Match('virtual-router', VR, 'forwarding-instance', FI, 'interfaces', interface, 'unit', unit, 'inet', 'address', source)) and "
        " Fact('hints', 'system', 'aaa', 'service-type', stype, 'default-address', source))"
    ]
