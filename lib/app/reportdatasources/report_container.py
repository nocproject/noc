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
        match = {"data.management.managed_object": {"$exists": True}}
        if self.sync_ids:
            match = {"data.management.managed_object": {"$in": self.sync_ids}}
        value = (
            get_db()["noc.objects"]
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .aggregate(
                [
                    {"$match": match},
                    {"$sort": {"data.management.managed_object": 1}},
                    {
                        "$lookup": {
                            "from": "noc.objects",
                            "localField": "container",
                            "foreignField": "_id",
                            "as": "cont",
                        }
                    },
                    {"$project": {"data": 1, "cont.data": 1}},
                ]
            )
        )

        for v in value:
            r = {}
            if "asset" in v["data"]:
                # r[v["data"]["management"]["managed_object"]].update(v["data"]["asset"])
                r.update(v["data"]["asset"])
            if v["cont"]:
                if "data" in v["cont"][0]:
                    # r[v["data"]["management"]["managed_object"]].update(v["cont"][0]["data"].get("address", {}))
                    r.update(v["cont"][0]["data"].get("address", {}))
            yield v["data"]["management"]["managed_object"], r


class ReportContainerData(BaseReportColumn):
    """Report for MO Container"""

    # @container address by container
    name = "containerdata"
    unknown_value = ("",)
    builtin_sorted = False

    def extract(self):
        match = {"data.address.text": {"$exists": True}}
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
                    # {"$sort": {"_id": 1}},
                    {
                        "$project": {
                            "parent_address": "$data.address.text",
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
        for v in value:
            cid = str(v["_id"])
            if "child_cont" in v:
                # ccid = str(v["child_cont"]["_id"])
                r[str(v["child_cont"]["_id"])] = v["parent_address"].strip()
            if cid not in r:
                r[cid] = v["parent_address"].strip()
        for mo_id, container in (
            ManagedObject.objects.filter(id__in=self.sync_ids)
            .values_list("id", "container")
            .order_by("id")
        ):
            if container in r:
                yield mo_id, r[container]
