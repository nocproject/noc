# ----------------------------------------------------------------------
# DefaultSystemAAAServiceLocalApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultSystemAAAServiceLocalApplicator(QueryApplicator):
    """
    Set forwarding instance type if not set
    """

    QUERY = [
        "NotMatch('system', 'aaa', 'service', service, 'type', 'local') and "
        "Fact('system', 'aaa', 'service', 'local', 'type', 'local')"
    ]
    CONFIG = {"default": "local"}
