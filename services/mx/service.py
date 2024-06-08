#!./bin/python
# ----------------------------------------------------------------------
# mx service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.core.mx import MX_STREAM
from noc.core.router.base import Router
from noc.core.msgstream.message import Message
from noc.core.perf import metrics


class MXService(FastAPIService):
    name = "mx"
    use_mongo = True
    use_router = False
    traefik_routes_rule = "PathPrefix(`/api/mx`)"

    def __init__(self):
        super().__init__()
        self.slot_number = 0
        self.total_slots = 0

    async def init_api(self):
        # Postpone initialization process until config datastream is fully processed
        self.ready_event = asyncio.Event()
        self.router = Router()
        asyncio.get_running_loop().create_task(self.get_mx_routes_config())
        # Set by datastream.on_ready
        await self.ready_event.wait()
        # Process as usual
        await super().init_api()

    async def on_route_rules_ready(self) -> None:
        # Pass further initialization
        self.ready_event.set()

    async def on_activate(self):
        self.logger.info("Loader %s chains: %s", len(self.router.chains), list(self.router.chains))
        self.slot_number, self.total_slots = await self.acquire_slot()
        await self.subscribe_stream(MX_STREAM, self.slot_number, self.on_message, async_cursor=True)

    async def on_message(self, msg: Message) -> None:
        metrics["messages"] += 1
        # Apply routes
        self.logger.debug("[%d] Receiving message %s", msg.offset, msg.headers)
        await self.router.route_message(msg, msg_id=msg.offset)
        self.logger.debug("[%s] Finish processing", msg.offset)


if __name__ == "__main__":
    MXService().start()
