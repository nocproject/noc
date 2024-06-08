#!./bin/python
# ----------------------------------------------------------------------
# BI service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class BIService(FastAPIService):
    name = "bi"
    use_translation = True
    use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/bi`)"

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    BIService().start()
