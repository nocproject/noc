# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import tornado.web
from jinja2 import Template
## NOC modules
from cards.managedobject import ManagedObjectCard


class CardRequestHandler(tornado.web.RequestHandler):
    CARDS = {
        "managedobject": ManagedObjectCard
    }
    CARD_TEMPLATE_PATH = "services/card/templates/card.html.j2"
    CARD_TEMPLATE = None

    def initialize(self):
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())

    def get(self, card_type, *args, **kwargs):
        card_template = self.CARDS.get(card_type)
        if not card_template:
            raise tornado.web.HTTPError(404, "Card template not found")
        # Prepare query arguments
        q = {}
        for a in self.request.arguments:
            q[a] = self.get_argument(a)
        #
        card = card_template(**q)
        data = card.render()
        if not data:
            raise tornado.web.HTTPError(404, "Not found")
        self.set_header("Content-Type", "text/html; charset=utf-8")
        self.set_header("Cache-Control", "no-cache, must-revalidate")
        self.write(card.render())
