# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectLinkCount datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from pymongo import ReadPreference
# NOC modules
from noc.lib.nosql import get_db
from .base import BaseReportColumn


class ReportObjectConfig(BaseReportColumn):
    """Report for MO link count"""
    name = "config_ts"
    unknown_value = (None, )
    builtin_sorted = True

    def extract(self):
        value = get_db()["noc.gridvcs.config.files"].with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
                {"$match": {"object": {"$in": self.sync_ids}}},
                {"$group": {"_id": "$object", "last_ts": {"$max": "$ts"}}},
                {"$sort": {"_id": 1}}])
        for v in value:
            if not v["_id"]:
                continue
            yield v["_id"], v["last_ts"]
