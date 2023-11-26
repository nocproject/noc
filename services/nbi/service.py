#!./bin/python
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class NBIService(FastAPIService):
    name = "nbi"
    use_mongo = True
    use_router = True
    traefik_routes_rule = "PathPrefix(`/api/nbi`)"

    def __init__(self):
        super().__init__()
        self.collect_req_api_metric = True


if __name__ == "__main__":
    NBIService().start()
