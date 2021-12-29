#!./bin/python
# ----------------------------------------------------------------------
# BI service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config


class BIService(FastAPIService):
    name = "bi"
    use_translation = True
    use_mongo = True
    if config.features.traefik:
        traefik_backend = "bi"
        traefik_frontend_rule = "PathPrefix:/api/bi"

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    BIService().start()
