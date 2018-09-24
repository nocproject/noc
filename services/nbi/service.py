#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import Service
from noc.config import config
from noc.services.nbi.loader import loader


class NBIService(Service):
    name = "nbi"
    if config.features.traefik:
        traefik_backend = "nbi"
        traefik_frontend_rule = "PathPrefix:/api/nbi"

    def get_api(self):
        r = []
        for api in loader.iter_apis():
            handler = loader.get_api(api)
            if handler:
                self.logger.info("[%s] Initializing API", api)
                r += [handler]
            else:
                self.logger.info("[%s] Failed to initialize API", api)
        return r

    def get_handlers(self):
        return [
            (
                "/api/nbi/%s" % api.name, api, {"service": self}
            ) for api in self.get_api()
        ]


if __name__ == "__main__":
    NBIService().start()
