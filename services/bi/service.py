#!./bin/python
# ----------------------------------------------------------------------
# BI service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
# from noc.core.service.ui import UIService
from noc.core.service.fastapi import FastAPIService

# from noc.services.bi.api.bi import BIAPI
# from noc.core.service.authapi import AuthAPIRequestHandler
from noc.config import config


class BIService(FastAPIService):
    name = "bi"
    #    api = [BIAPI]
    #    api_request_handler = AuthAPIRequestHandler
    use_translation = True
    use_mongo = True
    if config.features.traefik:
        traefik_backend = "bi"
        traefik_frontend_rule = "PathPrefix:/api/bi"

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    BIService().start()
