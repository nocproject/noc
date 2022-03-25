# ----------------------------------------------------------------------
# Card handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import inspect
from threading import Lock
import operator
from typing import Optional

# Third-party modules
from jinja2 import Template
import orjson
import cachetools

# NOC modules
from fastapi import APIRouter, Path, Header, HTTPException, Response
from fastapi.responses import RedirectResponse
from noc.services.card.myhandler import MyHandler
from noc.core.service.ui import UIHandler
from noc.services.card.cards.base import BaseCard
from noc.core.debug import error_report
from noc.aaa.models.user import User
from noc.config import config
from noc.core.debug import ErrorReport
from noc.core.perf import metrics

user_lock = Lock()


class CardRequestHandler(MyHandler):
    CARDS = None
    CARD_TEMPLATE_PATH = config.path.card_template_path
    CARD_TEMPLATE = None

    _user_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __init__(self):
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())
        self.load_cards()
        self.current_user = None

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_user_cache"), lock=lambda _: user_lock)
    def get_user_by_name(cls, name):
        try:
            return User.objects.get(username=name)
        except User.DoesNotExist:
            metrics["error", ("type", "user_not_found")] += 1
            return None

    def get_current_user(self):
        user = None
        with ErrorReport():
            user = self.get_user_by_name(self.request.headers.get("Remote-User"))
        return user

    def get(
        self,
        card_type: str,
        card_id: str,
        refresh: Optional[int] = None,
        remote_user: Optional[str] = Header(None, alias="Remote-User")
    ):
        print('card_type', card_type, type(card_type))
        print('card_id', card_id, type(card_id))
        self.current_user = self.get_user_by_name("admin")
        print('self.current_user', self.current_user, type(self.current_user))

        if not self.current_user:
            raise HTTPException(404, "Not authorized") # tornado.web.HTTPError(404, "Not found")
        is_ajax = card_id == "ajax"
        tpl = self.CARDS.get(card_type)
        print('tpl', tpl, type(tpl))
        if not tpl:
            raise HTTPException(404, "Card template not found") # tornado.web.HTTPError(404, "Card template not found")
        try:
            card = tpl(self, card_id)
            if is_ajax:
                data = card.get_ajax_data()
            else:
                data = card.render()
        except BaseCard.RedirectError as e:
            return RedirectResponse(e.args[0])
        except BaseCard.NotFoundError:
            raise HTTPException(404, "Not found") # raise tornado.web.HTTPError(404, "Not found")
        except Exception:
            error_report()
            raise HTTPException(500, "Internal server error") # tornado.web.HTTPError(500, "Internal server error")
        if not data:
            raise HTTPException(404, "No data found") # tornado.web.HTTPError(404, "Not found")

        headers = {"Cache-Control": "no-cache, must-revalidate"}
        if is_ajax:
            od = orjson.dumps(data, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS)
            return Response(content=od, media_type="application/json", headers=headers)
        else:
            if refresh:
                headers["Refresh"] = str(refresh)
            content = self.get_card_template().render(
                {
                    "card_data": data,
                    "card_title": str(card.object),
                    "hashed": self.hashed,
                    "card_js": card.card_js,
                    "card_css": card.card_css,
                }
            )
            return Response(content=content, media_type="text/html", headers=headers)

    def get_card_template(self):
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())
        return self.CARD_TEMPLATE

    CARDS_PREFIX = os.path.join("services", "card", "cards")

    @classmethod
    def load_cards(cls):
        if not cls.CARDS:
            cls.CARDS = {}
        for p in config.get_customized_paths(cls.CARDS_PREFIX):
            b, _ = p.split(cls.CARDS_PREFIX)
            if not os.path.isdir(p):
                continue
            if b:
                basename = os.path.basename(os.path.dirname(b))
            else:
                basename = "noc"
            for f in os.listdir(p):
                if not f.endswith(".py"):
                    continue
                mn = "%s.%s.%s" % (basename, cls.CARDS_PREFIX.replace(os.path.sep, "."), f[:-3])
                m = __import__(mn, {}, {}, "*")
                for d in dir(m):
                    c = getattr(m, d)
                    if (
                        inspect.isclass(c)
                        and issubclass(c, BaseCard)
                        and c.__module__ == m.__name__
                        and getattr(c, "name", None)
                    ):
                        cls.CARDS[c.name] = c


card_request_handler = CardRequestHandler()
