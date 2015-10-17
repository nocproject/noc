# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service config implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
import yaml


class Config(object):
    PATH = "etc/noc.yml"

    def __init__(self, service, **kwargs):
        self._defaults = vars(kwargs)
        self._conf = {}
        self._service = service
        self._logger = logging.getLogger(__name__)
        self._catalog = {}

    def load(self):
        self._service.logger.info("Loading config from %s", self.PATH)
        conf = self._defaults.copy()
        with open(self.PATH) as f:
            data = yaml.load(f)
        # Build config paths
        paths = [
            "noc",
            self._service,
            "%s-global-%s" % (self._service.name,
                              self._defaults["node"])
        ]
        if self._service.pooled:
            paths += [
                "%s-%s-%s" % (
                    self._service.name,
                    self._defaults["pool"],
                    self._defaults["node"]
                )
            ]
        # Build effective config
        for p in paths:
            if p not in data["config"]:
                continue
            conf.update(data["config"][p])
        if conf.get("debug"):
            self._logger.info("Effective config: %s", conf)
        # Notify config changes
        if self._conf:
            for k in conf:
                nv = conf[k]
                ov = self._conf.get(k)
                n = "on_change_%s" % k
                if nv != ov and hasattr(self._service, n):
                    getattr(self._service, n)(ov, nv)
        #
        self._conf = conf
        # Load service catalog
        self._catalog = data["services"]
        if conf.get("debug"):
            self._logger.info("Service catalog: %s", self._catalog)

    def __getattr__(self, item):
        if item.startswith("_") or item in ("load", "get_service"):
            return self.__dict__[item]
        else:
            return self._conf.get(item)

    def get_service(self, name):
        return self._catalog.get(name)
