# ----------------------------------------------------------------------
# ReportObjectContainer datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import ReadPreference

# NOC modules
from .base import BaseReportColumn
from noc.core.mongo.connection import get_db
from noc.sa.models.managedobject import ManagedObject


class ReportContainer(BaseReportColumn):
    """Report for MO Container"""

    # @container address by container
    name = "container"
    unknown_value = ({},)
    builtin_sorted = True

    def extract(self):
        match = {"data.interface": "management"}
        if self.sync_ids:
            match = {
                "data": {"$elemMatch": {"interface": "management", "value": {"$in": self.sync_ids}}}
            }
        value = (
            get_db()["noc.objects"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$match": match},
                    {
                        "$project": {
                            "serial": {
                                "$filter": {
                                    "input": "$data",
                                    "as": "d1",
                                    "cond": {
                                        "$and": [
                                            {"$eq": ["$$d1.interface", "asset"]},
                                            {"$eq": ["$$d1.scope", ""]},
                                            {"$eq": ["$$d1.attr", "serial"]},
                                        ]
                                    },
                                }
                            },
                            "managed_object": {
                                "$filter": {
                                    "input": "$data",
                                    "as": "d1",
                                    "cond": {
                                        "$and": [
                                            {"$eq": ["$$d1.interface", "management"]},
                                            {"$eq": ["$$d1.scope", ""]},
                                            {"$eq": ["$$d1.attr", "managed_object"]},
                                        ]
                                    },
                                }
                            },
                            "address": {
                                "$filter": {
                                    "input": "$data",
                                    "as": "d1",
                                    "cond": {
                                        "$and": [
                                            {"$eq": ["$$d1.interface", "address"]},
                                            {"$eq": ["$$d1.scope", ""]},
                                            {"$eq": ["$$d1.attr", "text"]},
                                        ]
                                    },
                                }
                            },
                        },
                    },
                    {
                        "$project": {
                            "serial": {"$arrayElemAt": ["$serial.value", 0]},
                            "managed_object": {"$arrayElemAt": ["$managed_object.value", 0]},
                            "address": {"$arrayElemAt": ["$address.value", 0]},
                        },
                    },
                    {"$sort": {"managed_object": 1}},
                    {
                        "$lookup": {
                            "from": "noc.objects",
                            "localField": "container",
                            "foreignField": "_id",
                            "as": "cont",
                        }
                    },
                ]
            )
        )

        for v in value:
            r = {}
            if "serial" in v:
                # r[v["data"]["management"]["managed_object"]].update(v["data"]["asset"])
                r["serial"] = v["serial"]
            if v["cont"] and "address" in v["cont"]:
                # r[v["data"]["management"]["managed_object"]].update(v["cont"][0]["data"].get("address", {}))
                r["address"] = v["cont"]["address"]
            yield v["managed_object"], r


class ReportContainerData(BaseReportColumn):
    """Report for MO Container"""

    # @container address by container
    name = "containerdata"
    unknown_value = ("",)
    builtin_sorted = False

    def extract(self):
        match = {"data.interface": "address"}
        # if self.sync_ids:
        #     containers = dict(ManagedObject.objects.filter(id__in=self.sync_ids).values_list("id", "container"))
        #     match = {"_id": {"$in": list(containers)}}
        # if self.sync_ids:
        #     match = {"data.management.managed_object": {"$in": self.sync_ids}}
        value = (
            get_db()["noc.objects"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$match": match},
                    {
                        "$project": {
                            "data": {
                                "$filter": {
                                    "input": "$data",
                                    "as": "d1",
                                    "cond": {
                                        "$and": [
                                            {"$eq": ["$$d1.interface", "address"]},
                                            {
                                                "$or": [
                                                    {"$not": ["$$d1.scope"]},
                                                    {"$eq": ["$$d1.scope", ""]},
                                                ]
                                            },
                                            {"$eq": ["$$d1.attr", "text"]},
                                        ]
                                    },
                                }
                            },
                            "parent_name": "$name",
                        }
                    },
                    {
                        "$project": {
                            "parent_address": {"$arrayElemAt": ["$data.value", 0]},
                            "parent_name": 1,
                            "_id": 1,
                        }
                    },
                    {
                        "$lookup": {
                            "from": "noc.objects",
                            "localField": "_id",
                            "foreignField": "container",
                            "as": "child_cont",
                        }
                    },
                    {
                        "$project": {
                            "parent_address": 1,
                            "parent_name": 1,
                            "_id": 1,
                            "child_cont._id": 1,
                            "child_cont.name": 1,
                        }
                    },
                    {"$unwind": {"path": "$child_cont", "preserveNullAndEmptyArrays": True}},
                ]
            )
        )
        r = {}
        cont_map = {}
        for v in value:
            cid = str(v["_id"])
            if "child_cont" in v and "parent_address" in v and str(v["child_cont"]["_id"]) not in r:
                # r[str(v["child_cont"]["_id"])] = v["parent_address"].strip()
                cont_map[str(v["child_cont"]["_id"])] = v["parent_address"].strip()
            if cid not in r and "parent_address" in v:
                r[cid] = v["parent_address"].strip()
        for mo_id, container in (
            ManagedObject.objects.filter(id__in=self.sync_ids)
            .values_list("id", "container")
            .order_by("id")
        ):
            if container in r:
                yield mo_id, r[container]
            elif container in cont_map:
                yield mo_id, cont_map[container]
