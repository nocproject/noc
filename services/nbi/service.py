#!./bin/python
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import Request

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config
from noc.core.perf import metrics

PREFIX_NBI = "/api/nbi/"


class NBIService(FastAPIService):
    name = "nbi"
    use_mongo = True
    use_router = True

    if config.features.traefik:
        traefik_backend = "nbi"
        traefik_frontend_rule = "PathPrefix:/api/nbi"

    def __init__(self):
        super().__init__()
        self.collect_req_api_metric = True


if __name__ == "__main__":
    NBIService().start()
