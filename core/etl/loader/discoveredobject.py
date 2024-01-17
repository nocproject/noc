# ----------------------------------------------------------------------
# Discovered Object loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Dict, Any
from core.etl.models.base import BaseModel

# NOC modules
from .base import BaseLoader
from ..models.purgatorium import DiscoveredObject
from noc.main.models.pool import Pool
from noc.core.purgatorium import register


class DiscoveredObjectLoader(BaseLoader):
    """
    Discovered Object loader
    """

    name = "managedobject"
    # model = ManagedObjectModel
    data_model = DiscoveredObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_map["pool"] = Pool.get_by_name

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
            self.pending_deletes = []

    def on_add(self, item: DiscoveredObject) -> None:
        register(
            item.address
        )

    def on_delete(self, item: DiscoveredObject):
        ...

    def on_change(self, o: DiscoveredObject, n: DiscoveredObject):
        ...
