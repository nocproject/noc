# ----------------------------------------------------------------------
# Managed Object loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.managedobject import ManagedObject
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject as ManagedObjectModel
from noc.sa.models.profile import Profile
from noc.inv.models.resourcegroup import ResourceGroup


class ManagedObjectLoader(BaseLoader):
    """
    Managed Object loader
    """

    name = "managedobject"
    model = ManagedObjectModel
    data_model = ManagedObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["pool"] = Pool.get_by_name
        self.clean_map["profile"] = Profile.get_by_name
        self.clean_map["static_service_groups"] = lambda x: [
            str(x.id) for x in ResourceGroup.objects.filter(remote_id__in=x)
        ]
        self.clean_map["static_client_groups"] = lambda x: [
            str(x.id) for x in ResourceGroup.objects.filter(remote_id__in=x)
        ]

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Deactivating: %s", msg)
            self.c_delete += 1
            try:
                obj = self.model.objects.get(pk=self.mappings[r_id])
                obj.is_managed = False
                obj.container = None
                obj.tags += ["remote:deleted"]
                obj.save()
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []
