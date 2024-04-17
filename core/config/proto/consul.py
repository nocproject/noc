# ----------------------------------------------------------------------
# Load config from consul
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio

# Third-party modules
from consul.base import Timeout

# NOC modules
from noc.core.consul import ConsulClient
from noc.core.comp import smart_text
from noc.core.ioloop.util import run_sync
from .base import BaseProtocol


class ConsulProtocol(BaseProtocol):
    """
    Environment variables mapping
    URL:
        consul:///<ip1>:<port>/<path>?token=<token>
    """

    DEFAULT_CONSUL_PORT = 8500
    REQUEST_TIMEOUT = 30
    CONNECT_TIMEOUT = 30

    def __init__(self, config, url):
        super().__init__(config, url)
        if ":" in self.parsed_url.netloc:
            h, p = self.parsed_url.netloc.rsplit(":", 1)
            self.host, self.port = h, int(p)
        else:
            self.host = self.parsed_url.netloc
            self.port = self.DEFAULT_CONSUL_PORT
        self.token = self.url_query.get("token")
        self.path = self.parsed_url.path[1:]

    async def load_async(self):
        consul = ConsulClient(host=self.host, port=self.port, token=self.token)
        # Convert to dict
        data = {}
        if self.path.endswith("/"):
            pl = len(self.path)
        else:
            pl = len(self.path) + 1
        while True:
            try:
                index, kv_data = await consul.kv.get(self.path, recurse=True, token=self.token)
                break
            except Timeout:
                await asyncio.sleep(2)
        if not kv_data:
            return
        for i in kv_data:
            k = i["Key"][pl:]
            v = i["Value"]
            if "slots" in k or k.endswith("/"):
                # Section
                continue
            if v == b'""' or v == b"''":
                # fix if value is "" - return '""'
                v = ""
            *path, k1 = k.split("/")
            c = data
            for p in path:
                if p not in c:
                    c[p] = {}
                    c = c[p]
                else:
                    c = c[p]
            c[k1] = smart_text(v)
        # print(orjson.dumps(data, option=orjson.OPT_INDENT_2).decode("utf8"))
        # Upload
        self.config.update(data)

    def load(self):
        run_sync(self.load_async)

    def dump(self, section=None):
        raise NotImplementedError
