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
from cards.service import ServiceCard
from cards.tt import TTCard
from cards.subscribersession import SubscriberSessionCard
from cards.totaloutage import TotalOutageCard


class CardRequestHandler(UIHandler):
    CARDS = {
        "managedobject": ManagedObjectCard,
        "alarm": AlarmCard,
        "service": ServiceCard,
        "subscribersession": SubscriberSessionCard,
        "tt": TTCard,
        "totaloutage": TotalOutageCard
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
        refresh = self.get_argument("refresh", None)
        if refresh:
            try:
                refresh = int(refresh)
                self.set_header("Refresh", str(refresh))
            except ValueError:
                pass
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

