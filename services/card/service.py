#!./bin/python
# ----------------------------------------------------------------------
# Card service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config


class CardService(FastAPIService):
    name = "card"

    use_translation = True
    use_jinja = True
    use_mongo = True
    use_watchdog = config.watchdog.enable_watchdog
    if config.features.traefik:
        traefik_backend = "card"
        traefik_frontend_rule = "PathPrefix:/api/card"


if __name__ == "__main__":
    CardService().start()
