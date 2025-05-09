# ----------------------------------------------------------------------
# Managed Object loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import Dict, Any

# Third-party module
from mongoengine.document import Document
from django.db.models.base import Model

# NOC modules
from .base import BaseLoader
from ..models.managedobject import ManagedObject
from noc.core.purgatorium import register
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject as ManagedObjectModel
from noc.sa.models.profile import Profile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.authprofile import AuthProfile
from noc.inv.models.resourcegroup import ResourceGroup
from noc.inv.models.capability import Capability
from noc.inv.models.networksegment import NetworkSegment
from noc.ip.models.vrf import VRF


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

    model_mappings = {
        "segment": NetworkSegment,
        "objectprofile": ManagedObjectProfile,
        "adm_domain": AdministrativeDomain,
        "auth_profile": AuthProfile,
        "vrf": VRF,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["pool"] = Pool.get_by_name
        self.clean_map["fm_pool"] = lambda x: Pool.get_by_name(x) if x else None
        self.clean_map["profile"] = Profile.get_by_name
        self.clean_map["static_service_groups"] = lambda x: [
            str(x.id)
            for x in ResourceGroup.objects.filter(
                remote_id__in=x or [],
                remote_system=self.system.remote_system,
            )
        ]
        self.clean_map["static_client_groups"] = lambda x: [
            str(x.id)
            for x in ResourceGroup.objects.filter(
                remote_id__in=x or [],
                remote_system=self.system.remote_system,
            )
        ]
        self.available_caps = {x.name for x in Capability.objects.filter()}
        self.c_register = 0

    def on_add_register(self, item: ManagedObject) -> None:
        """
        Create new record
        """
        self.register_record(item)
        self.c_add += 1

    def on_change_register(self, o: ManagedObject, n: ManagedObject):
        """
        Create change record
        """
        self.register_record(n)
        self.c_change += 1

    def purge_register(self):
        """
        Delete record
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.info("Deactivating: %s", msg)
            self.c_delete += 1
            pool = Pool.get_by_name(msg.pool)
            register(
                address=msg.address,
                hostname=msg.name,
                description=msg.description,
                pool=pool.bi_id,
                source="etl",
                labels=msg.labels or [],
                remote_system=self.system.remote_system.bi_id,
                remote_id=r_id,
                is_delete=True,
            )

    def register_record(self, item: ManagedObject):
        vv = self.clean(item)
        data = {}
        name, pool = vv.pop("name"), vv.pop("pool")
        description, labels = vv.pop("description", None), vv.pop("labels", None)
        remote_system, remote_id = vv.pop("remote_system"), vv.pop("remote_id")
        del vv["id"]
        service_groups = vv.pop("static_service_groups", None)
        client_groups = vv.pop("static_client_groups", None)
        for k, v in vv.items():
            if not v or k == "pool":
                continue
            # elif isinstance(v, list):
            #     v = ";".join(v)
            elif isinstance(v, enum.Enum):
                continue
            elif isinstance(v, (Document, Model)):
                v = v.id
            data[k] = str(v)
        address = data.pop("address")
        register(
            address=address,
            pool=pool.bi_id,
            source="etl",
            description=description,
            hostname=name,
            remote_system=remote_system.bi_id,
            remote_id=remote_id,
            # checks=item.checks,
            labels=labels or [],
            service_groups=[ResourceGroup.get_by_id(sg).bi_id for sg in service_groups or []],
            client_groups=[ResourceGroup.get_by_id(sg).bi_id for sg in client_groups or []],
            **data,
        )
        self.c_register += 1

    def load(self, return_wo_changes: bool = False):
        """
        Import new data
        """
        if not self.system.remote_system.managed_object_as_discovered:
            return super().load()
        self.on_add = self.on_add_register
        self.on_change = self.on_change_register
        self.purge = self.purge_register
        r = super().load(return_wo_changes=self.system.remote_system.managed_object_as_discovered)
        self.logger.info("Register discovered: %d", self.c_register)
        return r

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
            except self.model.DoesNotExist:
                pass  # Already deleted
            except KeyError:
                pass
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
