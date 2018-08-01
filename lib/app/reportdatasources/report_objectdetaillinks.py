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
from .base import BaseReportColumn
from noc.lib.nosql import get_db


class ReportObjectDetailLinks(BaseReportColumn):
    """Report for MO links detail"""
    name = "objectdetaillink"
    builtin_sorted = True
    unknown_value = ([], )
    ATTRS = ["Links"]

    def extract(self):
        match = {"int.managed_object": {"$in": self.sync_ids}}
        group = {"_id": "$int.managed_object",
                 "links": {"$push": {"link": "$_id",
                                     "iface_n": "$int.name",
                                     "iface_id": "$int._id",
                                     "mo": "$int.managed_object"}}}
        value = get_db()["noc.links"].with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).aggregate([
            {"$unwind": "$interfaces"},
            {"$lookup": {"from": "noc.interfaces", "localField": "interfaces", "foreignField": "_id", "as": "int"}},
            {"$match": match},
            {"$group": group},
            {"$sort": {"_id": 1}}
        ])
        for val in value:
            yield val["_id"][0], val["links"]
