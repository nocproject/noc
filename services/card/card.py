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
from noc.core.service.ui import UIHandler
from cards.managedobject import ManagedObjectCard
from cards.alarm import AlarmCard


class CardRequestHandler(UIHandler):
    CARDS = {
        "managedobject": ManagedObjectCard,
        "alarm": AlarmCard
    }
    CARD_TEMPLATE_PATH = "services/card/templates/card.html.j2"
    CARD_TEMPLATE = None

    def initialize(self):
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())

    def get(self, card_type, card_id, *args, **kwargs):
        tpl = self.CARDS.get(card_type)
        if not tpl:
            raise tornado.web.HTTPError(404, "Card template not found")
        card = tpl(card_id)
        data = card.render()
        if not data:
            raise tornado.web.HTTPError(404, "Not found")
        self.set_header("Content-Type", "text/html; charset=utf-8")
        self.set_header("Cache-Control", "no-cache, must-revalidate")
        self.write(
            self.get_card_template().render({
                "card_data": data,
                "hashed": self.hashed
            })
        )

    def get_card_template(self):
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())
        return self.CARD_TEMPLATE

