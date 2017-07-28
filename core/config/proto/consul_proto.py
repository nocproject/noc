# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Load config from consul
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from base import BaseProtocol
from noc.core.consul import ConsulClient


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
        super(ConsulProtocol, self).__init__(config, url)
        if ":" in self.parsed_url.netloc:
            h, p = self.parsed_url.netloc.rsplit(":", 1)
            self.host, self.port = h, int(p)
        else:
            self.host = self.parsed_url.netloc
            self.port = self.DEFAULT_CONSUL_PORT
        self.token = self.url_query.get("token")
        self.path = self.parsed_url.path[1:]

    @tornado.gen.coroutine
    def load_async(self):
        consul = ConsulClient(
            host=self.host,
            port=self.port,
            token=self.token
        )
        # Convert to dict
        data = {}
        if self.path.endswith("/"):
            pl = len(self.path)
        else:
            pl = len(self.path) + 1
        index, kv_data = yield consul.kv.get(self.path, recurse=True, token=self.token)
        for i in kv_data and kv_data:
            k = i["Key"][pl:]
            v = i["Value"]
            c = k.count("/")
            if not c:
                data[k.replace("/", ".")] = v
            elif c == 1:
                d = k.split("/")
                data.update({
                    d[0]: {
                        d[1]: v
                    }
                })
        # Upload
        self.config.update(data)

    def load(self):
        ioloop = tornado.ioloop.IOLoop.current()
        ioloop.run_sync(self.load_async)

    def dump(self):
        raise NotImplementedError
