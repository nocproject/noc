#!./bin/python
# ---------------------------------------------------------------------
# Topo service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import asyncio
import threading

# NOC modules
from noc.config import config
from noc.core.error import NOCError
from noc.core.debug import ErrorReport
from noc.core.change.policy import change_tracker
from noc.core.service.fastapi import FastAPIService
from noc.sa.models.managedobject import ManagedObject, ObjectUplinks
from noc.services.topo.datastream import TopoDataStreamClient
from noc.services.topo.topo import Topo
from noc.services.topo.types import ObjectSnapshot


class TopoService(FastAPIService):
    name = "topo"
    use_mongo = True

    def __init__(self):
        super().__init__()
        self.topo = Topo(check=config.topo.check)
        self.topo_lock = asyncio.Lock()

    async def on_activate(self) -> None:
        await super().on_activate()
        asyncio.get_running_loop().create_task(self.get_topology())

    async def get_topology(self) -> None:
        """
        Request topology.
        """
        self.logger.info("Starting to track topology")
        asyncio.get_running_loop().create_task(self.get_object_mappings())

    async def get_object_mappings(self):
        """
        Coroutine to request object mappings
        """
        self.logger.info("Starting to track object mappings")
        client = TopoDataStreamClient("managedobject", service=self)
        # Track stream changes
        while True:
            try:
                await client.query(
                    limit=config.topo.ds_limit,
                    block=True,
                )
            except NOCError as e:
                self.logger.info("Failed to get topology: %s", e)
                await asyncio.sleep(1)

    async def set_ready(self) -> None:
        """
        Called when topology is loaded and server is ready.
        """
        self.logger.info("Topology is ready.")
        asyncio.get_running_loop().create_task(self.process_topology())

    async def process_topology(self) -> None:
        """
        Topology processing background job
        """

        def inner() -> None:
            """
            Run processing and set event on complete.
            """
            try:
                with ErrorReport(), change_tracker.bulk_changes():
                    affected = self.topo.process()
                    if affected and not config.topo.dry_run:
                        self.logger.info("Commiting uplink changes")
                        # @todo: RCA neighbors
                        up_links = []
                        for obj_id in affected:
                            try:
                                up_links.append(
                                    ObjectUplinks(
                                        object_id=obj_id,
                                        uplinks=list(sorted(self.topo.get_uplinks(obj_id))),
                                        rca_neighbors=list(
                                            sorted(self.topo.get_rca_neighbors(obj_id))
                                        ),
                                    )
                                )
                            except KeyError:
                                self.logger.warning("Deleted object with id: %s", obj_id)
                        ManagedObject.update_uplinks(up_links)
                        self.logger.info("%d changes has been commited", len(affected))
            finally:
                ev_processed.set()

        while True:
            if self.topo.has_dirty():
                ev_processed = asyncio.Event()
                async with self.topo_lock:
                    # Run processing in separate thread in order
                    # to avoid healhcheck blocking.
                    thread = threading.Thread(target=inner, name="process")
                    thread.daemon = True
                    thread.start()
                    # Wait until thread is complete
                    await ev_processed.wait()
            await asyncio.sleep(float(config.topo.interval))

    async def on_change(self, snapshot: ObjectSnapshot) -> None:
        """
        Called on external topology change.

        Args:
            snapshot: Object snapshot.
        """
        async with self.topo_lock:
            self.topo.sync_object(snapshot)

    async def on_delete(self, obj_id: int) -> None:
        """
        Called on managed object deletion.

        Args:
            obj_id: Removed object's id.
        """
        async with self.topo_lock:
            self.topo.remove_object(obj_id)


if __name__ == "__main__":
    TopoService().start()
