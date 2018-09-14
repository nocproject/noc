#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# mrt service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.service.base import Service
from noc.services.mrt.mrt import MRTRequestHandler
from noc.config import config


class MRTService(Service):
    name = "mrt"

    if config.features.traefik:
        traefik_backend = "mrt"
        traefik_frontend_rule = "PathPrefix:/api/mrt"

    def on_activate(self):
        self.sae = self.open_rpc("sae")

    def get_handlers(self):
        return [
            ("/api/mrt/", MRTRequestHandler, {"service": self})
        ]


if __name__ == "__main__":
    MRTService().start()
