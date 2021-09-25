# ----------------------------------------------------------------------
# IfaceTypeJunosApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.confdb.applicator.query import QueryApplicator


class IfaceTypeJunosApplicator(QueryApplicator):
    """
    Set missed interface types from matchers
    """

    QUERY = [
        "("
        "Match('meta', 'matchers', 'is_work_em') "
        "and Match('interfaces', X) and Re('^em.+', X)) or "
        "(Match('meta', 'matchers', 'is_srx_6xx') "
        "and Match('interfaces', X) and Re('^reth.+', X)) "
        "and Fact('interfaces', X, 'type', 'physical')"
    ]
