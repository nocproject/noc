#!./bin/python
# ----------------------------------------------------------------------
# Card service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
#from noc.core.service.ui import UIService
from noc.core.service.fastapi import FastAPIService
from noc.services.card.card import CardRequestHandler
from noc.services.card.search import SearchRequestHandler
from noc.config import config


class CardService(FastAPIService):
    name = "card"

    use_translation = True
    use_jinja = True
    use_mongo = True
    if config.features.traefik:
        traefik_backend = "card"
        traefik_frontend_rule = "PathPrefix:/api/card"

#    def get_handlers(self):
#        CardRequestHandler.load_cards()
#        return super().get_handlers() + [
#            (r"^/api/card/search/$", SearchRequestHandler),
#            (r"^/api/card/view/(\S+)/(\S+)/$", CardRequestHandler),
#        ]


if __name__ == "__main__":
    CardService().start()
