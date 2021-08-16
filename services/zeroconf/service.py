#!./bin/python
# ----------------------------------------------------------------------
# zk service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.service.fastapi import FastAPIService


class ZeroConfService(FastAPIService):
    name = "zeroconf"
    use_mongo = True
    if config.features.traefik:
        traefik_backend = "ui"
        traefik_frontend_rule = "PathPrefix:/api/zeroconf"


if __name__ == "__main__":
    ZeroConfService().start()
