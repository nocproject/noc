#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Card service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.ui import UIService
from card import CardRequestHandler
from search import SearchRequestHandler
from noc.config import config


class CardService(UIService):
    name = "card"

    use_translation = True
    use_jinja = True
    if config.features.traefik:
        traefik_backend = "card"
        traefik_frontend_rule = "PathPrefix:/api/card"

    def get_handlers(self):
        CardRequestHandler.load_cards()
        return super(CardService, self).get_handlers() + [
            ("^/api/card/search/$", SearchRequestHandler),
            ("^/api/card/view/(\S+)/(\S+)/$", CardRequestHandler)
        ]


if __name__ == "__main__":
    CardService().start()
