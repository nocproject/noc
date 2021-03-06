# ----------------------------------------------------------------------
# DataSteam client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
import logging

# Third-party modules
import orjson

# NOC modules
from noc.core.http.client import fetch, ERR_READ_TIMEOUT, ERR_TIMEOUT
from noc.core.error import NOCError, ERR_DS_BAD_CODE, ERR_DS_PARSE_ERROR
from noc.core.dcs.error import ResolutionError

logger = logging.getLogger(__name__)


class DataStreamClient(object):
    RETRY_TIMEOUT = 1.0

    def __init__(self, name, service=None):
        self.name = name
        self.service = service

    async def on_change(self, data):
        """
        Called on each item received through datastream
        :param data:
        :return:
        """

    async def on_delete(self, data):
        """
        Called on each deleted item received through datastream
        :param data:
        :return:
        """

    async def query(self, change_id=None, filters=None, block=False, limit=None):
        """
        Query datastream
        :param filters:
        :return:
        """
        # Basic URL and query
        base_url = "http://datastream/api/datastream/%s" % self.name
        base_qs = []
        if filters:
            base_qs += ["filter=%s" % x for x in filters]
        if block:
            base_qs += ["block=1"]
        if limit:
            base_qs += ["limit=%d" % limit]
        req_headers = {"X-NOC-API-Access": "datastream:%s" % self.name}
        loop = asyncio.get_running_loop()
        # Continue until finish
        while True:
            # Build URL
            # *datastream* host name will be resolved with *resolve* method
            qs = base_qs[:]
            if change_id:
                qs += ["from=%s" % change_id]
            if qs:
                url = "%s?%s" % (base_url, "&".join(qs))
            else:
                url = base_url
            # Get data
            logger.debug("Request: %s", url)
            t0 = loop.time()
            code, headers, data = await fetch(url, resolver=self.resolve, headers=req_headers)
            dt = loop.time() - t0
            logger.debug("Response: %s %s [%.2fms]", code, headers, dt * 1000)
            if code == ERR_TIMEOUT or code == ERR_READ_TIMEOUT:
                if dt < self.RETRY_TIMEOUT:
                    await asyncio.sleep(self.RETRY_TIMEOUT - dt)
                continue  # Retry on timeout
            elif code != 200:
                logger.info("Invalid response code: %s", code)
                raise NOCError(code=ERR_DS_BAD_CODE, msg="Invalid response code %s" % code)
            # Parse response
            try:
                data = orjson.loads(data)
            except ValueError as e:
                logger.info("Cannot parse response: %s", e)
                raise NOCError(code=ERR_DS_PARSE_ERROR, msg="Cannot parse response: %s" % e)
            # Process result
            for item in data:
                if "$deleted" in item:
                    await self.on_delete(item)
                else:
                    await self.on_change(item)
            # Continue from last change
            if "X-NOC-DataStream-Last-Change" in headers:
                change_id = headers["X-NOC-DataStream-Last-Change"]
            elif not block:
                break  # Empty batch, stop if non-blocking mode

    async def resolve(self, host):
        try:
            svc = await self.service.dcs.resolve(host)
        except ResolutionError:
            return None
        host, port = svc.split(":")
        return host, int(port)
