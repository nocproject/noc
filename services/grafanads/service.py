#!./bin/python
# ---------------------------------------------------------------------
# GrafanaDS service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class GrafanaDSService(FastAPIService):
    name = "grafanads"
    use_mongo = True


if __name__ == "__main__":
    GrafanaDSService().start()
