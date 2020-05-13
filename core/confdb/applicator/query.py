# ----------------------------------------------------------------------
# QueryApplicator class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseApplicator


class QueryApplicator(BaseApplicator):
    # List of ConfDB queries
    # Each accepts config as input context
    QUERY = None
    # ConfDB query string to fulfill can_apply()
    # None - always apply
    CHECK_QUERY = None
    # List of
    CONFIG = {}

    def __init__(self, object, confdb, **kwargs):
        super().__init__(object, confdb)
        for k in self.CONFIG:
            self.config[k] = kwargs.get(k, self.CONFIG[k])

    def apply(self):
        if not self.QUERY:
            return
        cfg = {"object": self.object, "profile": self.object.profile.get_profile()}
        cfg.update(self.config)
        for q in self.QUERY:
            list(self.confdb.query(q, **cfg))

    def can_apply(self):
        if not super().can_apply():
            return False
        if not self.CHECK_QUERY:
            return True
        cfg = {"object": self.object, "profile": self.object.profile.get_profile()}
        cfg.update(self.config)
        return any(self.confdb.query(self.CHECK_QUERY, **cfg))
