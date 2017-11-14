# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Card handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import inspect
from threading import Lock
import operator
# Third-party modules
import tornado.web
from jinja2 import Template
import ujson
import cachetools
# NOC modules
from noc.core.service.ui import UIHandler
from noc.services.card.cards.base import BaseCard
from noc.core.debug import error_report
from noc.main.models import User
from noc.config import config

user_lock = Lock()


class CardRequestHandler(UIHandler):
    CARDS = None
    CARD_TEMPLATE_PATH = config.path.card_template_path
    CARD_TEMPLATE = None

    _user_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def initialize(self):
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_user_cache"), lock=lambda _: user_lock)
    def get_user_by_name(cls, name):
        try:
            return User.objects.get(username=name)
        except User.DoesNotExist:
            return None

    def get_current_user(self):
        return self.get_user_by_name(
            self.request.headers.get("Remote-User")
        )

    def get(self, card_type, card_id, *args, **kwargs):
        if not self.current_user:
            raise tornado.web.HTTPError(404, "Not found")
        is_ajax = card_id == "ajax"
        tpl = self.CARDS.get(card_type)
        if not tpl:
            raise tornado.web.HTTPError(404, "Card template not found")
        try:
            card = tpl(self, card_id)
            if is_ajax:
                data = card.get_ajax_data()
            else:
                data = card.render()
        except BaseCard.RedirectError as e:
            return self.redirect(e.args[0])
        except Exception:
            error_report()
            raise tornado.web.HTTPError(500, "Internal server error")
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

    @classmethod
    def load_cards(cls):
        if not cls.CARDS:
            cls.CARDS = {}
            custom_path = os.path.join(config.path.custom_path, "services/card/cards")
            for r in [custom_path, "services/card/cards"]:
                if not os.path.exists(r):
                    continue
                if r.startswith(".."):
                    r = r.replace(config.path.custom_path, "")[1:]
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
                        if (
                            inspect.isclass(c) and
                            issubclass(c, BaseCard) and
                            c.__module__ == m.__name__ and
                            getattr(c, "name", None)
                        ):
                            cls.CARDS[c.name] = c
