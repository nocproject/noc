# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHNetworkSegment datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.inv.models.networksegment import NetworkSegment


class CHAdministrativeDomainDataSource(BaseDataSource):
    name = "ch_networksegment"

    def extract(self):
        ns_id = dict(NetworkSegment.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED).scalar("id", "bi_id"))
        ns = NetworkSegment._get_collection().with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)

        for sub in ns.find({},
                           {"_id": 1, "bi_id": 1, "name": 1, "parent": 1}).sort("parent"):
            yield (
                sub["bi_id"],
                sub["_id"],
                sub["name"],
                ns_id.get(sub["parent"], "") if sub.get("parent") else ""
            )
