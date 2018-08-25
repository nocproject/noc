# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# OIDsRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .oid import OIDRule


class OIDsRule(object):
    """
    Multiple items for single metric
    """
    name = "oids"

    def __init__(self, oids):
        self.oids = oids

    def iter_oids(self, script, metric):
        for rule in self.oids:
            for r in rule.iter_oids(script, metric):
                yield r

    @classmethod
    def from_json(cls, data):
        if "oids" not in data:
            raise ValueError("oids is required")
        if not isinstance(data["oids"], list):
            raise ValueError("oids must be list")
        return OIDsRule(
            oids=[OIDRule.from_json(d) for d in data["oids"]]
        )
