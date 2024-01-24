# ----------------------------------------------------------------------
# Discovered Object loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.discoveredobject import DiscoveredObject
from noc.core.purgatorium import register
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject as ManagedObjectModel


class DiscoveredObjectLoader(BaseLoader):
    """
    Discovered Object loader
    """

    name = "discoveredobject"
    model = ManagedObjectModel
    data_model = DiscoveredObject

    def on_add(self, item: DiscoveredObject) -> None:
        pool = Pool.get_by_name(item.pool)
        register(
            address=item.address,
            pool=pool.bi_id,
            source="etl",
            remote_system=self.system.remote_system.bi_id,
            remote_id=item.id,
            **(item.data or {}),
        )

    def purge(self):
        """
        Perform pending deletes
        """
        for item_id, item in reversed(self.pending_deletes):
            self.logger.debug("Delete: %s", item)
            self.c_delete += 1
            pool = Pool.get_by_name(item.pool)
            register(
                address=item.address,
                pool=pool.bi_id,
                source="etl",
                remote_system=self.system.remote_system.bi_id,
                remote_id=item.id,
                is_delete=True,
                **(item.data or {}),
            )
        self.pending_deletes = []

    def on_change(self, o: DiscoveredObject, n: DiscoveredObject):
        self.on_add(n)

    def check(self, chain):
        self.logger.info("Checking")
        return 0
