#!./bin/python
# ----------------------------------------------------------------------
# datastream service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class DataStreamService(FastAPIService):
    name = "datastream"
    use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/datastream`)"


if __name__ == "__main__":
    DataStreamService().start()
