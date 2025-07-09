# ----------------------------------------------------------------------
# Card API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import inspect
from threading import Lock
import operator
from typing import Optional

# Third-party modules
import cachetools
from fastapi import APIRouter, Header, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, ORJSONResponse
from jinja2 import Template
import orjson

# NOC modules
from noc.aaa.models.user import User
from noc.config import config
from noc.core.debug import error_report, ErrorReport
from noc.core.perf import metrics
from noc.services.card.cards.base import BaseCard
from noc.services.card.base import BaseAPI

user_lock = Lock()

router = APIRouter()

MIN_SEARCH = 2


class HandlerStub(object):
    def __init__(self, user, arguments):
        self.user: "User" = user
        self.arguments = {}
        for key in arguments:
            if arguments[key]:
                self.arguments[key] = arguments[key]

    @property
    def current_user(self):
        return self.user

    def get_argument(self, name: str, default: Optional[str] = None, strict: bool = True):
        """

        :param name: Argument Name
        :param default: default value
        :param strict: Raise exception if not argument
        :return:
        """
        if name not in self.arguments and strict:
            raise HTTPException(404, f"Query parameter '{name}' not specified")
        return self.arguments.get(name, default)


class CardAPI(BaseAPI):
    api_name = "card"
    openapi_tags = ["card API"]

    CARDS = None
    CARD_TEMPLATE_PATH = config.path.card_template_path
    CARD_TEMPLATE = None

    _user_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __init__(self, router: APIRouter):
        super().__init__(router)
        if not self.CARD_TEMPLATE:
            with open(self.CARD_TEMPLATE_PATH) as f:
                self.CARD_TEMPLATE = Template(f.read())
        self.load_cards()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_user_cache"), lock=lambda _: user_lock)
    def get_user_by_name(cls, name):
        try:
            return User.objects.get(username=name)
        except User.DoesNotExist:
            metrics["error", ("type", "user_not_found")] += 1
            return None

    def get_current_user(self, name):
        with ErrorReport():
            user = self.get_user_by_name(name)
        return user

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

    def get_routes(self):
        route_card = {
            "path": "/api/card/view/{card_type}/{card_id}/",
            "method": "GET",
            "endpoint": self.handler_card_view,
            "response_class": HTMLResponse,
            "response_model": None,
            "name": "card-view",
            "description": "",
        }
        route_search = {
            "path": "/api/card/search/",
            "method": "GET",
            "endpoint": self.handler_card_search,
            "response_class": ORJSONResponse,
            "response_model": None,
            "name": "card-search",
            "description": "",
        }
        return [route_card, route_search]

    def handler_card_view(
        self,
        card_type: str,
        card_id: str,
        request: Request,
        remote_user: Optional[str] = Header(None, alias="Remote-User"),
    ):
        current_user = self.get_current_user(remote_user)
        if not current_user:
            raise HTTPException(404, "Not found")
        is_ajax = card_id == "ajax"
        handler = HandlerStub(current_user, request.query_params)
        tpl = self.CARDS.get(card_type)
        if not tpl:
            raise HTTPException(404, "Card template not found")
        try:
            card = tpl(handler, card_id)
            if is_ajax:
                data = card.get_ajax_data()
            else:
                data = card.render()
        except BaseCard.RedirectError as e:
            return RedirectResponse(e.args[0])
        except BaseCard.NotFoundError:
            raise HTTPException(404, "Not found")
        except Exception:
            error_report()
            raise HTTPException(500, "Internal server error")
        if not data:
            raise HTTPException(404, "Not found")

        headers = {"Cache-Control": "no-cache, must-revalidate"}
        if is_ajax:
            od = orjson.dumps(data, option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_NON_STR_KEYS)
            return Response(content=od, media_type="application/json", headers=headers)
        else:
            refresh = request.query_params.get("refresh")
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

    def handler_card_search(
        self, scope: str, query: str, remote_user: Optional[str] = Header(None, alias="Remote-User")
    ):
        query = query.strip()
        if not query or len(query) < MIN_SEARCH:
            raise HTTPException(400, "Query too short")
        card = self.CARDS.get(scope)
        if not card or not hasattr(card, "search"):
            raise HTTPException(404, "Not found")
        handler = HandlerStub(self.get_current_user(remote_user), {})
        return card.search(handler, query)


# Install router
CardAPI(router)
