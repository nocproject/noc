# ----------------------------------------------------------------------
# NTP applicators
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .query import QueryApplicator


class DefaultNTPVersionApplicator(QueryApplicator):
    CHECK_QUERY = "Match('hints', 'protocols', 'ntp', 'version')"
    QUERY = [
        "Match('hints', 'protocols', 'ntp', 'version', default_version) and "
        "NotMatch('protocols', 'ntp', X, 'version') and "
        "Fact('protocols', 'ntp', X, 'version', default_version)"
    ]


class DefaultNTPModeApplicator(QueryApplicator):
    CHECK_QUERY = "Match('hints', 'protocols', 'ntp', 'mode')"
    QUERY = [
        "Match('hints', 'protocols', 'ntp', 'mode', default_mode) and "
        "NotMatch('protocols', 'ntp', X, 'mode') and "
        "Fact('protocols', 'ntp', X, 'mode', default_mode)"
    ]
