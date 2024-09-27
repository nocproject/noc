# ----------------------------------------------------------------------
# Datastream endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Callable, Set
from http import HTTPStatus
import time
import cachetools
import logging
import asyncio
import threading
import random
from queue import Queue, Empty

# Third-party modules
from pymongo.errors import PyMongoError
from fastapi import APIRouter, Query, Header, HTTPException, Response, Depends

# NOC modules
from noc.core.datastream.loader import loader
from noc.core.datastream.base import DataStream
from noc.config import config
from noc.core.ioloop.util import setup_asyncio

router = APIRouter()

logger = logging.getLogger(__name__)

API_ACCESS_HEADER = "X-NOC-API-Access"


@cachetools.cached
def get_format_role(ds, fmt):
    return ds.get_format_role(fmt)


def get_access_tokens_set(datastream, fmt: Optional[str] = None) -> Set[str]:
    tokens = {"datastream:*", f"datastream:{datastream.name}"}
    if fmt:
        role = get_format_role(datastream, fmt)
        if role:
            tokens.add(f"datastream:{role}")
    return tokens


class DatastreamAPI(object):
    def __init__(self, router: APIRouter):
        self.router = router
        self.openapi_tags = ["api", "datastream"]
        self.api_name = "datastream"
        self.ds_queue = {}
        setup_asyncio()
        self.loop = asyncio.get_event_loop()
        self.setup_watchers()
        self.setup_datastream()

    @staticmethod
    def get_datastreams() -> List["DataStream"]:
        r = []
        for name in loader:
            if not getattr(config.datastream, f"enable_{name}", False):
                continue
            ds = loader[name]
            if ds:
                logger.info("[%s] Initializing datastream", name)
                r += [ds]
            else:
                logger.info("[%s] Failed to initialize datastream", name)
        return r

    async def wait(self, ds_name):
        def notify(loop):
            loop.call_soon(event.set)
            # asyncio.get_running_loop().call_soon(event.set)

        if ds_name not in self.ds_queue:
            return
        event = asyncio.Event()
        self.ds_queue[ds_name].put(notify)
        await event.wait()

    @staticmethod
    def has_watch() -> bool:
        """
        Detect cluster has working .watch() implementation
        :return: True if .watch() is working
        """
        # Get one datastream collection
        dsn = next(loader.iter_classes())
        ds = loader[dsn]
        coll = ds.get_collection()
        # Check pymongo has .watch
        if not hasattr(coll, "watch"):
            logger.error("pymongo does not support .watch() method")
            return False
        # Check connection is member of replica set
        if not config.mongo.rs:
            logger.error("MongoDB must be in replica set mode to use .watch()")
            return False
        # Check version, MongoDB 3.6.0 or later required
        client = coll.database.client
        sv = tuple(int(x) for x in client.server_info()["version"].split("."))
        if sv < (3, 6, 0):
            logger.error("MongoDB 3.6 or later require to use .watch()")
            return False
        return True

    def setup_watchers(self):
        # Detect we have working .watch() implementation
        if self.has_watch():
            has_watch = True
        else:
            logger.warning("Realtime change tracking is not available, using polling emulation.")
            has_watch = False
        # Start watcher threads
        self.ds_queue = {}
        for ds in self.get_datastreams():
            if has_watch and getattr(config.datastream, f"enable_{ds.name}_wait"):
                waiter = self.watch_waiter
            else:
                waiter = self.sleep_waiter
            logger.info("Starting %s waiter thread", ds.name)
            queue = Queue()
            self.ds_queue[ds.name] = queue
            thread = threading.Thread(
                target=waiter, args=(ds.get_collection(), queue), name=f"waiter-{ds.name}"
            )
            thread.daemon = True
            thread.start()

    def _run_callbacks(self, queue):
        """
        Execute callbacks from queue
        :param queue:
        :return:
        """
        while True:
            try:
                cb = queue.get(block=False)
            except Empty:
                break
            cb(self.loop)

    def watch_waiter(self, coll, queue):
        """
        Waiter thread tracking mongo's ChangeStream
        :param coll:
        :param queue:
        :return:
        """
        while True:
            with coll.watch(
                pipeline=[{"$project": {"_id": 1}}],
                max_await_time_ms=config.datastream.max_await_time * 1_000,  # Milliseconds
            ) as stream:
                try:
                    for _ in stream:
                        # Change received, call all pending callback
                        self._run_callbacks(queue)
                except PyMongoError as e:
                    logger.error("Unrecoverable watch error: %s", e)
                    time.sleep(1)

    def sleep_waiter(self, coll, queue):
        """
        Simple timeout waiter
        :param coll:
        :param queue:
        :return:
        """
        TIMEOUT = 60
        JITER = 0.1
        while True:
            # Sleep timeout is random of [TIMEOUT - TIMEOUT * JITTER, TIMEOUT + TIMEOUT * JITTER]
            time.sleep(TIMEOUT + (random.random() - 0.5) * TIMEOUT * 2 * JITER)
            self._run_callbacks(queue)

    def get_datastream_handler(self, datastream: "DataStream") -> Callable:
        async def inner_datastream(
            limit: Optional[int] = datastream.DEFAULT_LIMIT,
            ds_filter: Optional[List[str]] = Query(None, alias="filter"),
            ds_id: Optional[List[str]] = Query(None, alias="id"),
            ds_format: Optional[str] = Query(None, alias="format"),
            ds_from: Optional[str] = Query(None, alias="from"),
            ds_filter_policy: Optional[str] = Query(
                None, alias="filter_policy", regex=r"^(default|delete|keep|move)$"
            ),
            block: Optional[int] = None,
        ):
            # Increase limit by 1 to detect datastream has more data
            limit = min(limit, datastream.DEFAULT_LIMIT) + 1
            left = config.datastream.max_reply_size
            # Collect filters
            filters = ds_filter or []
            ids = ds_id or None
            if ids:
                filters += ["id(%s)" % ",".join(ids)]
            # Start from change
            if ds_from:
                change_id = ds_from
            else:
                change_id = None
            # Format
            if ds_format:
                fmt = ds_format
            else:
                fmt = None
            # block argument
            p_block = block
            to_block = bool(p_block) and bool(int(p_block))
            first_change = None
            last_change = None
            nr = 1
            has_more = False
            while True:
                r = []
                try:
                    async for _item_id, change_id, data in datastream.iter_data_async(
                        limit=limit,
                        filters=filters,
                        change_id=change_id,
                        fmt=fmt,
                        filter_policy=ds_filter_policy,
                    ):
                        if not first_change:
                            first_change = change_id
                        left -= len(data)
                        if left < 0:
                            logger.info(
                                "Response getting too large. Sending. [collected=%d, data=%d, limit=%d]",
                                config.datastream.max_reply_size - left + len(data),
                                len(data),
                                config.datastream.max_reply_size,
                            )
                            has_more = True
                            break  # Split large reply
                        last_change = change_id
                        r.append(data)
                        nr += 1
                        if nr == limit:
                            has_more = True
                            break  # Skip last additional item
                except ValueError:
                    raise HTTPException(status_code=HTTPStatus.BAD_REQUEST)
                if to_block and not r:
                    await self.wait(datastream.name)
                else:
                    break
            headers = {
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "X-NOC-DataStream-Total": str(datastream.get_total()),
                "X-NOC-DataStream-Limit": str(limit),
            }
            if first_change:
                headers["X-NOC-DataStream-First-Change"] = str(first_change)
            if last_change:
                headers["X-NOC-DataStream-Last-Change"] = str(last_change)
            if has_more:
                headers["X-NOC-DataStream-More"] = "1"
            return Response(content=f"[{','.join(r)}]", headers=headers)

        return inner_datastream

    def get_verify_token_hander(self, datastream: "DataStream") -> Callable:
        async def verify_token(
            ds_format: Optional[str] = Query(None, alias="format"),
            x_noc_api_access: Optional[str] = Header(None),
            host: Optional[str] = Header(None),
        ):
            if not x_noc_api_access:
                raise HTTPException(status_code=400, detail="X-NOC-API-Access header invalid")
            a_set = get_access_tokens_set(datastream, ds_format) & set(x_noc_api_access.split(","))
            if not a_set:
                raise HTTPException(status_code=403, detail="Not allowed datastream")

        return verify_token

    def setup_datastream(self):
        for ds in self.get_datastreams():
            self.router.add_api_route(
                path=f"/api/datastream/{ds.name}",
                endpoint=self.get_datastream_handler(ds),
                methods=["GET"],
                dependencies=[Depends(self.get_verify_token_hander(ds))],
                # response_model=sig.return_annotation,
                response_model=ds.model,
                tags=self.openapi_tags,
                name=f"{self.api_name}_get_{ds.name}",
                description=f"Getinng info {ds.name} datastream",
            )


# Install endpoints
DatastreamAPI(router)
