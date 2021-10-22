#!./bin/python
# ----------------------------------------------------------------------
# datastream service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config


class DataStreamService(FastAPIService):
    name = "datastream"
    use_mongo = True
    if config.features.traefik:
        traefik_backend = "datastream"
        traefik_frontend_rule = "PathPrefix:/api/datastream"


if __name__ == "__main__":
    DataStreamService().start()
