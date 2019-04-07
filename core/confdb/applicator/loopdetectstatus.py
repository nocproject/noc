# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DefaultLoopDetectStatusApplicator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .query import QueryApplicator


class DefaultLoopDetectStatusApplicator(QueryApplicator):
    QUERY = [
        # LLDP is globally enabled
        "Match('hints', 'protocols', 'loop-detect', 'status', 'on') and "
        # Get all physical interfaces and bind to variable X
        "Match('interfaces', X, 'type', 'physical') and "
        # Only admin-status up interfaces
        "Match('interfaces', X, 'admin-status', 'on') and "
        # Filter out explicitly disabled interfaces
        "NotMatch('hints', 'protocols', 'loop-detect', 'interface', X, 'off') and "
        # For each interface with lldp admin status is not set
        "NotMatch('protocols', 'loop-detect', 'interface', X) and "
        # Set loop-detect interface
        "Fact('protocols', 'loop-detect', 'interface', X)"
    ]
