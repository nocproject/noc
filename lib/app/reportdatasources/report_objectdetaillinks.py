# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ReportObjectDetailLinks datasource
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


class ReportObjectDetailLinks(BaseReportDataSource):
    """Report for MO links detail"""

    UNKNOWN = []
    ATTRS = ["Links"]

    @staticmethod
    def load(ids, attributes):
        match = {"int.managed_object": {"$in": ids}}
        group = {"_id": "$int.managed_object",
                 "links": {"$push": {"link": "$_id",
                                     "iface_n": "$int.name",
                                     "iface_id": "$int._id",
                                     "mo": "$int.managed_object"}}}
        value = get_db()["noc.links"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$unwind": "$interfaces"},
            {"$lookup": {"from": "noc.interfaces", "localField": "interfaces", "foreignField": "_id", "as": "int"}},
            {"$match": match},
            {"$group": group}
        ])

        return dict((v["_id"][0], v["links"]) for v in value if v["_id"])

    def __getitem__(self, item):
        return self.out.get(item, [])
