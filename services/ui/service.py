#!./bin/python
# ----------------------------------------------------------------------
# <describe module here>
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.service.fastapi import FastAPIService


class UIService(FastAPIService):
    name = "ui"
    if config.features.traefik:
        traefik_backend = "ui"
        traefik_frontend_rule = "PathPrefix:/api/ui"


if __name__ == "__main__":
    UIService().start()
