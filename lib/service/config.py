# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service config implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import os
import functools
## Third-party modules
import consul.base
import tornado.ioloop
import tornado.gen
import blinker


class Config(object):
    def __init__(self, consul, conf="", dc=None, **kwargs):
        self.change = blinker.signal("confchanged")
        self.ready = blinker.signal("confready")
        self._conf = kwargs.copy()
        self._raw_conf = {}  # level -> dict
        self._logger = logging.getLogger("config")
        self._consul = consul
        self._pending_configs = set(conf.split(":"))
        ioloop = tornado.ioloop.IOLoop.instance()
        for n, conf in enumerate(self._pending_configs):
            self._raw_conf[n] = {}
            ioloop.add_callback(
                functools.partial(self._watch_conf, conf, n)
            )

    @tornado.gen.coroutine
    def _watch_conf(self, conf, level):
        """
        """
        self._logger.debug("Looking for %s (level %s)", conf, level)
        index = None
        while True:
            # Wait for data or updates
            try:
                index, data = yield self._consul.kv.get(
                    conf,
                    index=index,
                    recurse=True
                )
            except consul.base.Timeout:
                continue
            # Apply config
            if data:
                c = dict((
                    d["Key"].rsplit("/", 1)[-1],
                    d["Value"]
                ) for d in data)
                self._raw_conf[level].update(c)
                max_level = max(self._raw_conf.iterkeys())
                k = set(c)
                hidden = set()
                if level != max_level:
                    # Apply data at shadowed level
                    for l in range(level + 1, max_level + 1):
                        hidden |= set(self._raw_conf[l]) & k
                # Apply changes
                for x in k - hidden:
                    if self._conf.get(x) != c[x]:
                        self._conf[x] = c[x]
                        self.change.send(x, value=c[x])
                self._logger.debug("Config: %s", self._conf)
            if conf in self._pending_configs:
                self._pending_configs.remove(conf)
                if not self._pending_configs:
                    self.ready.send(self)

    def __getattr__(self, item):
        if item.startswith("_") or item in ("change", "ready"):
            return self.__dict__[item]
        else:
            return self._conf[item]

    def __getitem__(self, item):
        return self._conf[item]
