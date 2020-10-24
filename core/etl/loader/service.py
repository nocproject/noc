# ----------------------------------------------------------------------
# Service loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.service import ServiceModel
from noc.sa.models.service import Service


class ServiceLoader(BaseLoader):
    """
    Service loader
    """

    name = "service"
    model = Service
    data_model = ServiceModel
    fields = [
        "id",
        "parent",
        "subscriber",
        "profile",
        "ts",
        "logical_status",
        "logical_status_start",
        "agreement_id",
        "order_id",
        "stage_id",
        "stage_name",
        "stage_start",
        "account_id",
        "address",
        "managed_object",
        "nri_port",
        "cpe_serial",
        "cpe_mac",
        "cpe_model",
        "cpe_group",
        "description",
    ]

    mapped_fields = {
        "parent": "service",
        "subscriber": "subscriber",
        "profile": "serviceprofile",
        "managed_object": "managedobject",
    }

    discard_deferred = True

    def find_object(self, v):
        """
        Find object by remote system/remote id
        :param v:
        :return:
        """
        if not v.get("remote_system") or not v.get("remote_id"):
            self.logger.warning("RS or RID not found")
            return None
        if not hasattr(self, "_service_remote_ids"):
            self.logger.info("Filling service collection")
            coll = Service._get_collection()
            self._service_remote_ids = {
                c["remote_id"]: c["_id"]
                for c in coll.find(
                    {"remote_system": v["remote_system"].id, "remote_id": {"$exists": True}},
                    {"remote_id": 1, "_id": 1},
                )
            }
        if v["remote_id"] in self._service_remote_ids:
            return Service.objects.get(id=self._service_remote_ids[v["remote_id"]])
        return None
