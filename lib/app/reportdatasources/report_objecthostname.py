# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectCaps datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from .base import BaseReportDataSource
from noc.lib.nosql import get_db


class ReportObjectsHostname(BaseReportDataSource):
    """MO hostname"""

    def __init__(self, mo_ids=(), use_facts=False):
        self.load = self.load_discovery
        super(ReportObjectsHostname).__init__(mo_ids)
        if use_facts:
            self.out.update(self.load_facts(mo_ids))

    @staticmethod
    def load_facts(mos_ids):
        db = get_db()["noc.objectfacts"]
        mos_filter = {"label": "system"}
        if mos_ids:
            mos_filter["object"] = {"$in": mos_ids}
        value = db.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED
                                ).find(mos_filter, {"_id": 0, "object": 1, "attrs.hostname": 1})
        return {v["object"]: v["attrs"].get("hostname") for v in value}

    @staticmethod
    def load_discovery(mos_ids):
        db = get_db()["noc.inv.discovery_id"]
        mos_filter = {}
        if mos_ids:
            mos_filter["object"] = {"$in": mos_ids}
        value = db.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED
                                ).find(mos_filter, {"_id": 0, "object": 1, "hostname": 1})
        return {v["object"]: v.get("hostname") for v in value}
