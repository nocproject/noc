# ----------------------------------------------------------------------
# DataSteam client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
import logging
from typing import Optional

# Third-party modules
import orjson

# NOC modules
from noc.core.http.async_client import HttpClient, ERR_TIMEOUT, ERR_READ_TIMEOUT
from noc.core.error import NOCError, ERR_DS_BAD_CODE, ERR_DS_PARSE_ERROR
from noc.core.dcs.error import ResolutionError
from noc.core.comp import DEFAULT_ENCODING

logger = logging.getLogger(__name__)


class DataStreamClient(object):
    RETRY_TIMEOUT = 1.0

    def __init__(self, name, service=None):
        self.name = name
        self.service = service
        self._is_ready = False
        self.client = HttpClient(
            headers={"X-NOC-API-Access": f"datastream:{self.name}".encode(DEFAULT_ENCODING)},
            resolver=self.resolve,
        )

    async def on_change(self, data):
        """
        Called on each item received through datastream
        :param data:
        :return:
        """

    async def on_move(self, data):
        """
        Called on each moved item received through datastream
        :param data:
        :return:
        """

    async def on_delete(self, data):
        """
        Called on each deleted item received through datastream
        :param data:
        :return:
        """

    async def on_ready(self):
        """
        Called when initial data is ready and processed.
        :return:
        """

    async def query(
        self,
        change_id: Optional[str] = None,
        filters=None,
        block: bool = False,
        limit: Optional[int] = None,
        ds_format: Optional[str] = None,
        filter_policy: Optional[str] = None,
    ):
        """
        Query datastream
        :param change_id: Staring change id
        :param filters: List of strings with filter expression
        :param block:
        :param limit: Records limit
        :param ds_format: DataStream Format
        :param filter_policy: Metadata changed policy. Behavior if metadata change out of filter scope
                   * default - no changes
                   * delete - return $delete message
                   * keep - ignore filter, return full record
                   * move - return $moved message
        :return:
        """
        # Basic URL and query
        base_url = f"http://datastream/api/datastream/{self.name}"
        base_qs = []
        if filters:
            base_qs += [f"filter={x}" for x in filters]
        if limit:
            base_qs += [f"limit={limit}"]
        if ds_format:
            base_qs += [f"format={ds_format}"]
        if filter_policy:
            base_qs += [f"filter_policy={filter_policy}"]
        loop = asyncio.get_running_loop()
        # Continue until finish
        while True:
            # Build URL
            # *datastream* host name will be resolved with *resolve* method
            qs = base_qs[:]
            if change_id:
                qs += [f"from={change_id}"]
            if qs:
                jqs = "&".join(qs)
                url = f"{base_url}?{jqs}"
            else:
                url = base_url
            # Get data
            logger.debug("Request: %s", url)
            t0 = loop.time()
            code, headers, data = await self.client.get(url)
            # code, headers, data = await fetch(url, resolver=self.resolve, headers=req_headers)
            dt = loop.time() - t0
            logger.debug("Response: %s %s [%.2fms]", code, headers, dt * 1000)
            if code == ERR_TIMEOUT or code == ERR_READ_TIMEOUT:
                if dt < self.RETRY_TIMEOUT:
                    await asyncio.sleep(self.RETRY_TIMEOUT - dt)
                continue  # Retry on timeout
            elif code != 200:
                logger.info("Invalid response code: %s", code)
                raise NOCError(code=ERR_DS_BAD_CODE, msg=f"Invalid response code {code}")
            # Parse response
            try:
                data = orjson.loads(data)
            except ValueError as e:
                logger.info("Cannot parse response: %s", e)
                raise NOCError(code=ERR_DS_PARSE_ERROR, msg=f"Cannot parse response: {e}")
            # Process result
            for item in data:
                if "$deleted" in item:
                    await self.on_delete(item)
                elif "$moved" in item:
                    await self.on_move(item)
                else:
                    await self.on_change(item)
            #
            if not self._is_ready and "X-NOC-DataStream-More" not in headers:
                await self.on_ready()
                self._is_ready = True
            # Continue from last change
            if "X-NOC-DataStream-Last-Change" in headers:
                change_id = headers["X-NOC-DataStream-Last-Change"].decode(DEFAULT_ENCODING)
                continue
            if block and self._is_ready:
                # Do not set block=1 before is_ready, otherwise
                # without data in datastream process will be blocked by _is_ready signal
                base_qs += ["block=1"]
            if not block:
                break  # No data, Stop if non-blocking mode

    async def resolve(self, host):
        try:
            svc = await self.service.dcs.resolve(host)
        except ResolutionError:
            return None
        host, port = svc.split(":")
        return host, int(port)
