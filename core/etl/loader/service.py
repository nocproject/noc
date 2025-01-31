# ----------------------------------------------------------------------
# Service loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any, List

# NOC modules
from noc.inv.models.capability import Capability
from noc.sa.models.service import Service as ServiceModel
from noc.sa.models.serviceinstance import ServiceInstance
from noc.sa.models.serviceprofile import ServiceProfile
from noc.core.models.inputsources import InputSource
from noc.core.models.serviceinstanceconfig import InstanceType
from .base import BaseLoader
from ..models.service import Service, Instance


class ServiceLoader(BaseLoader):
    """
    Service loader
    """

    name = "service"
    model = ServiceModel
    data_model = Service

    discard_deferred = True
    workflow_state_sync = True
    model_mappings = {"profile": ServiceProfile}

    post_save_fields = {"capabilities", "instances"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_caps = {x.name for x in Capability.objects.filter()}

    def post_save(self, o: ServiceModel, fields: Dict[str, Any]):
        self.apply_instances(o, fields.get("instances") or [])
        if not fields or "capabilities" not in fields:
            return
        for cc in fields["capabilities"] or []:
            c_name = cc["name"]
            if c_name not in self.available_caps:
                continue
            o.set_caps(c_name, cc["value"], source="etl", scope=self.system.name)
        o.save()

    @classmethod
    def apply_instances(cls, o: ServiceModel, fields: List[Dict[str, Any]]):
        """Synchronize Service Instances"""
        instances = {i["remote_id"]: Instance(**i) for i in fields}
        for si in ServiceInstance.objects.filter(service=o.id, remote_id__exists=True):
            if si.remote_id not in instances:
                o.deregister_instance(si.type, source=InputSource.ETL)
                continue
            i = instances.pop(si.remote_id)
            si.register_endpoint(InputSource.ETL, addresses=i.addresses, port=i.port)
            if si.fqdn != i.fqdn:
                si.fqdn = i.fqdn
                si.save()
        for i in instances.values():
            si = o.register_instance(
                type=InstanceType.NETWORK_HOST if not i.nri_port else InstanceType.NETWORK_CHANNEL,
                source=InputSource.ETL,
                fqdn=i.fqdn,
                remote_id=i.remote_id,
            )
            si.register_endpoint(InputSource.ETL, addresses=i.addresses, port=i.port)

    def find_object(self, v: Dict[str, Any]):
        """
        Find object by remote system/remote id

        Attrs:
            v: Object attributes
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
