#!./bin/python
# ----------------------------------------------------------------------
# Card service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class CardService(FastAPIService):
    name = "card"

    use_translation = True
    use_jinja = True
    use_mongo = True
    traefik_routes_rule = "PathPrefix(`/api/card`)"


if __name__ == "__main__":
    CardService().start()
