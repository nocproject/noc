#!./bin/python
# ---------------------------------------------------------------------
# Login service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config


class LoginService(FastAPIService):
    name = "login"
    process_name = "noc-%(name).10s-%(instance).2s"
    use_mongo = True
    use_translation = True
    if config.features.traefik:
        traefik_backend = "login"
        traefik_frontend_rule = "PathPrefix:/api/login,/api/auth/auth"

    OPENAPI_TAGS_DOCS = {
        "login": "Authentication services",
        "ext-ui": "Legacy ExtJS UI services. To be removed with decline of legacy UI",
    }


if __name__ == "__main__":
    LoginService().start()
