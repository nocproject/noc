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
import ujson
import os
import inspect
## NOC modules
from noc.core.service.ui import UIHandler
from noc.services.card.cards.base import BaseCard

from cards.managedobject import ManagedObjectCard
from cards.alarm import AlarmCard
from cards.service import ServiceCard
from cards.tt import TTCard
from cards.subscribersession import SubscriberSessionCard
from cards.totaloutage import TotalOutageCard
from cards.outage import OutageCard
from cards.alarmheat import AlarmHeatCard
from cards.maintainance import MaintainanceCard


class CardRequestHandler(UIHandler):
    CARDS = None
    CARD_TEMPLATE_PATH = "services/card/templates/card.html.j2"
    CARD_TEMPLATE = None

    def initialize(self):
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())
        if not self.CARDS:
            self.CARDS = {}
            for r in ["custom/services/card/cards", "services/card/cards"]:
                if not os.path.isdir(r):
                    continue
                for f in os.listdir(r):
                    if not f.endswith(".py"):
                        continue
                    mn = "noc.%s.%s" % (
                        r.replace("/", "."),
                        f[:-3]
                    )
                    m = __import__(mn, {}, {}, "*")
                    for d in dir(m):
                        c = getattr(m, d)
                        if (inspect.isclass(c) and
                            issubclass(c, BaseCard) and
                            c.__module__ == m.__name__ and
                            getattr(c, "name", None)
                        ):
                            self.CARDS[c.name] = c

    def get(self, card_type, card_id, *args, **kwargs):
        is_ajax = card_id == "ajax"
        tpl = self.CARDS.get(card_type)
        if not tpl:
            raise tornado.web.HTTPError(404, "Card template not found")
        card = tpl(card_id)
        if is_ajax:
            data = card.get_ajax_data()
        else:
            data = card.render()
        if not data:
            raise tornado.web.HTTPError(404, "Not found")
        self.set_header("Cache-Control", "no-cache, must-revalidate")
        if is_ajax:
            self.set_header("Content-Type", "text/json")
            self.write(ujson.dumps(data))
        else:
            self.set_header("Content-Type", "text/html; charset=utf-8")
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
                    "hashed": self.hashed,
                    "card_js": card.card_js,
                    "card_css": card.card_css
                })
            )

    def get_card_template(self):
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())
        return self.CARD_TEMPLATE

