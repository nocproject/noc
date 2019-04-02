# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# QueryApplicator class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseApplicator


class QueryApplicator(BaseApplicator):
    # List of confdb queries
    # Each accepts config as input context
    QUERY = None
    CONFIG = {}

    def __init__(self, confdb, **kwargs):
        super(QueryApplicator, self).__init__(confdb)
        for k in self.CONFIG:
            self.config[k] = kwargs.get(k, self.CONFIG[k])

    def apply(self, object):
        if not self.QUERY:
            return
        cfg = {
            "object": object,
            "profile": object.profile.get_profile()
        }
        cfg.update(self.config)
        for q in self.QUERY:
            list(self.confdb.query(q, **cfg))
