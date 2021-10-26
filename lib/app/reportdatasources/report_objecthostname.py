# ----------------------------------------------------------------------
# ReportObjectCaps datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import BaseReportColumn
from noc.core.mongo.connection import get_db
from noc.inv.models.discoveryid import DiscoveryID


class ReportObjectsHostname1(BaseReportColumn):
    name = "hostname"
    unknown_value = ("",)
    builtin_sorted = True

    def extract(self):
        c_did = DiscoveryID._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        )
        for val in c_did.find({"hostname": {"$exists": 1}}, {"object": 1, "hostname": 1}).sort(
            "object"
        ):
            yield val["object"], val["hostname"]


class ReportObjectsHostname2(BaseReportColumn):
    name = "hostname2"
    unknown_value = ("",)
    builtin_sorted = True

    def extract(self):
        db = get_db()["noc.objectfacts"]
        mos_filter = {"label": "system"}
        if self.sync_ids:
            mos_filter["object"] = {"$in": list(self.sync_ids)}
        for val in (
            db.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find(mos_filter, {"_id": 0, "object": 1, "attrs.hostname": 1})
            .sort("object")
        ):
            yield val["object"], val["attrs"].get("hostname", self.unknown_value)


# class ReportObjectsHostname(BaseReportDataSource):
#     """MO hostname"""
#
#     def __init__(self, mo_ids=(), use_facts=False):
#         self.load = self.load_discovery
#         super(ReportObjectsHostname).__init__(mo_ids)
#         if use_facts:
#             self.out.update(self.load_facts(mo_ids))
#
#     @staticmethod
#     def load_facts(mos_ids):
#         db = get_db()["noc.objectfacts"]
#         mos_filter = {"label": "system"}
#         if mos_ids:
#             mos_filter["object"] = {"$in": mos_ids}
#         value = db.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED
#                                 ).find(mos_filter, {"_id": 0, "object": 1, "attrs.hostname": 1})
#         return {v["object"]: v["attrs"].get("hostname") for v in value}
#
#     @staticmethod
#     def load_discovery(mos_ids):
#         db = get_db()["noc.inv.discovery_id"]
#         mos_filter = {}
#         if mos_ids:
#             mos_filter["object"] = {"$in": mos_ids}
#         value = db.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED
#                                 ).find(mos_filter, {"_id": 0, "object": 1, "hostname": 1})
#         return {v["object"]: v.get("hostname") for v in value}
