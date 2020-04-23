# ----------------------------------------------------------------------
# InterfaceTypeApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class InterfaceTypeApplicator(QueryApplicator):
    """
    Set missed interface types via profile's .get_interface_type()
    """

    QUERY = [
        "NotMatch('interfaces', X, 'type') and "
        "Set(if_type=profile.get_interface_type(X)) and "
        "Filter(if_type is not None) and "
        "Fact('interfaces', X, 'type', if_type)"
    ]
