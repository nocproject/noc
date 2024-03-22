#!./bin/python
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config


class NBIService(FastAPIService):
    name = "nbi"
    use_mongo = True
    use_router = True
    use_watchdog = config.watchdog.enable_watchdog
    traefik_routes_rule = "PathPrefix(`/api/nbi`)"

    def __init__(self):
        super().__init__()
        self.collect_req_api_metric = True


if __name__ == "__main__":
    NBIService().start()
