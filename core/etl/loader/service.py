# ----------------------------------------------------------------------
# Service loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any, Optional

# NOC modules
from noc.inv.models.capability import Capability
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.service import Service as ServiceModel
from noc.sa.models.serviceprofile import ServiceProfile
from noc.core.models.inputsources import InputSource
from .base import BaseLoader
from ..models.service import Service, Instance


class ServiceLoader(BaseLoader):
    """
    Service loader
    """

    name = "service"
    model = ServiceModel
    data_model = Service

    discard_deferred = False
    workflow_state_sync = True
    model_mappings = {"profile": ServiceProfile}

    post_save_fields = {"capabilities", "instances"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_caps = {x.name for x in Capability.objects.filter()}
        self.clean_map["static_service_groups"] = lambda x: [
            x.id
            for x in ResourceGroup.objects.filter(
                remote_id__in=x or [],
                remote_system=self.system.remote_system,
            )
        ]
        self.clean_map["static_client_groups"] = lambda x: [
            x.id
            for x in ResourceGroup.objects.filter(
                remote_id__in=x or [],
                remote_system=self.system.remote_system,
            )
        ]

    def post_save(self, o: ServiceModel, fields: Dict[str, Any]):
        if not fields:
            capabilities, instances = [], []
        else:
            capabilities, instances = fields.get("capabilities"), fields.get("instances")
        caps = {}
        for cc in capabilities or []:
            c_name = cc["name"]
            if c_name not in self.available_caps:
                continue
            caps[c_name] = cc["value"]
        o.update_caps(caps, source="etl", scope=self.system.name)
        # Raise Error in not allowed on config
        o.update_instances(
            source=InputSource.ETL,
            instances=[Instance.model_validate(i).config for i in instances or []],
        )

    def find_object(
        self, v: Dict[str, Any], mappings: Optional[Dict[Any, str]] = None, **kwargs
    ) -> Optional[Any]:
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
