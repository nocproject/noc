#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Card service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.ui import UIService
from card import CardRequestHandler
from search import SearchRequestHandler


class CardService(UIService):
    name = "card"
    process_name = "noc-%(name).10s-%(instance).3s"

    use_translation = True
    use_jinja = True

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
