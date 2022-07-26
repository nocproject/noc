# ----------------------------------------------------------------------
# Service loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any

# NOC modules
from noc.inv.models.capability import Capability
from noc.sa.models.service import Service as ServiceModel
from .base import BaseLoader
from ..models.service import Service


class ServiceLoader(BaseLoader):
    """
    Service loader
    """

    name = "service"
    model = ServiceModel
    data_model = Service

    discard_deferred = True
    workflow_state_sync = True

    post_save_fields = {"capabilities"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_caps = {x.name for x in Capability.objects.filter()}

    def post_save(self, o: ServiceModel, fields: Dict[str, Any]):
        if not fields or "capabilities" not in fields:
            return
        for cc in fields["capabilities"] or []:
            c_name = cc["name"]
            if c_name not in self.available_caps:
                continue
            o.set_caps(c_name, cc["value"], source="etl", scope=self.system.name)
        o.save()

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
            coll = ServiceModel._get_collection()
            self._service_remote_ids = {
                c["remote_id"]: c["_id"]
                for c in coll.find(
                    {"remote_system": v["remote_system"].id, "remote_id": {"$exists": True}},
                    {"remote_id": 1, "_id": 1},
                )
            }
        if v["remote_id"] in self._service_remote_ids:
            return ServiceModel.objects.get(id=self._service_remote_ids[v["remote_id"]])
        return None
