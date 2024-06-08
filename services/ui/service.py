#!./bin/python
# ----------------------------------------------------------------------
# UI service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config


class UIService(FastAPIService):
    name = "ui"
    traefik_routes_rule = "PathPrefix(`/api/ui`)"
    use_mongo = True
    use_watchdog = config.watchdog.enable_watchdog


if __name__ == "__main__":
    UIService().start()
