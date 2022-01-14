#!./bin/python
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config

# from noc.core.perf import metrics
# from noc.core.comp import smart_text


class NBIService(FastAPIService):
    name = "nbi"
    use_mongo = True
    if config.features.traefik:
        traefik_backend = "nbi"
        traefik_frontend_rule = "PathPrefix:/api/nbi"


if __name__ == "__main__":
    NBIService().start()
