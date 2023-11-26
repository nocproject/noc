#!./bin/python
# ----------------------------------------------------------------------
# zk service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class ZeroConfService(FastAPIService):
    name = "zeroconf"
    use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/zeroconf`)"


if __name__ == "__main__":
    ZeroConfService().start()
