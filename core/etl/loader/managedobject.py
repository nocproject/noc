# ----------------------------------------------------------------------
# Managed Object loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any

# NOC modules
from .base import BaseLoader
from ..models.managedobject import ManagedObject
from noc.core.purgatorium import register
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject as ManagedObjectModel
from noc.sa.models.profile import Profile
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.capability import Capability


class ManagedObjectLoader(BaseLoader):
    """
    Managed Object loader
    """

    name = "managedobject"
    model = ManagedObjectModel
    data_model = ManagedObject
    post_save_fields = {"capabilities"}
    label_enable_setting = "enable_managedobject"
    workflow_delete_event = "remove"
    workflow_state_sync = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["pool"] = Pool.get_by_name
        self.clean_map["fm_pool"] = lambda x: Pool.get_by_name(x) if x else None
        self.clean_map["profile"] = Profile.get_by_name
        self.clean_map["static_service_groups"] = lambda x: [
            str(x.id) for x in ResourceGroup.objects.filter(remote_id__in=x or [])
        ]
        self.clean_map["static_client_groups"] = lambda x: [
            str(x.id) for x in ResourceGroup.objects.filter(remote_id__in=x or [])
        ]
        self.available_caps = {x.name for x in Capability.objects.filter()}

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Deactivating: %s", msg)
            self.c_delete += 1
            try:
                obj = self.model.objects.get(pk=self.mappings[r_id])
                ws = obj.object_profile.workflow.get_wiping_state()
                if ws:
                    obj.set_state(ws)
                obj.container = None
                obj.save()
                # Register deleted objects
                if self.system.remote_system.enable_discoveredobject:
                    register(
                        address=obj.address,
                        pool=obj.pool.bi_id,
                        source="etl",
                        remote_system=self.system.remote_system.bi_id,
                        remote_id=obj.id,
                        is_delete=True,
                    )
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []

    def post_save(self, o: ManagedObjectModel, fields: Dict[str, Any]):
        if not fields or "capabilities" not in fields:
            return
        caps = {}
        for cc in fields["capabilities"] or []:
            c_name = cc["name"]
            if c_name not in self.available_caps:
                continue
            caps[c_name] = cc["value"]
        o.update_caps(caps, source="etl", scope=self.system.name)
