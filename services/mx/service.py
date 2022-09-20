#!./bin/python
# ----------------------------------------------------------------------
# mx service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
from typing import Dict, Any

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.error import NOCError
from noc.core.mx import MX_STREAM
from noc.config import config
from noc.core.liftbridge.message import Message
from noc.core.router.base import Router
from noc.core.perf import metrics
from noc.services.mx.datastream import RouteDataStreamClient


class MXService(FastAPIService):
    name = "mx"
    use_mongo = True

    if config.features.traefik:
        traefik_backend = "mx"
        traefik_frontend_rule = "PathPrefix:/api/mx"

    def __init__(self):
        super().__init__()
        self.slot_number = 0
        self.total_slots = 0
        self.router = Router()

    async def init_api(self):
        # Postpone initialization process until config datastream is fully processed
        self.ready_event = asyncio.Event()
        asyncio.get_running_loop().create_task(self.get_mx_routes_config())
        # Set by datastream.on_ready
        await self.ready_event.wait()
        # Process as usual
        await super().init_api()

    async def get_mx_routes_config(self):
        """
        Subscribe and track datastream changes
        """
        client = RouteDataStreamClient("cfgmxroute", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track MX route settings")
            try:
                await client.query(limit=config.message.ds_limit, block=True)
            except NOCError as e:
                self.logger.info("Failed to get MX route settings: %s", e)
                await asyncio.sleep(1)

    async def on_ready(self) -> None:
        # Pass further initialization
        self.ready_event.set()

    async def on_activate(self):
        #     self.router.load()
        self.logger.info("Loader rules %s", len(self.router.chains))
        self.slot_number, self.total_slots = await self.acquire_slot()
        await self.subscribe_stream(MX_STREAM, self.slot_number, self.on_message, async_cursor=True)

    async def update_route(self, data: Dict[str, Any]) -> None:
        self.router.change_route(data)

    async def delete_route(self, r_id: str) -> None:
        self.router.delete_route(r_id)

    async def on_message(self, msg: Message) -> None:
        metrics["messages"] += 1
        # Apply routes
        self.logger.debug("[%d] Receiving message %s", msg.offset, msg.headers)
        await self.router.route_message(msg)
        self.logger.debug("[%s] Finish processing", msg.offset)


if __name__ == "__main__":
    MXService().start()
