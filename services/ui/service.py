#!./bin/python
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.service.fastapi import FastAPIService


class UIService(FastAPIService):
    name = "ui"
    use_watchdog = config.watchdog.enable_watchdog
    if config.features.traefik:
        traefik_backend = "ui"
        traefik_frontend_rule = "PathPrefix:/api/ui"
    use_mongo = True


if __name__ == "__main__":
    UIService().start()
