# ----------------------------------------------------------------------
# Card API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from importlib.resources import files
from threading import Lock
import operator
from urllib.parse import unquote

# Third-party modules
import cachetools
from fastapi import APIRouter, Header, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from jinja2 import Template
import orjson

# NOC modules
from noc.aaa.models.user import User
from noc.core.debug import error_report, ErrorReport
from noc.core.perf import metrics
from noc.services.card.cards.base import BaseCard, card_loader
from noc.services.card.base import BaseAPI

user_lock = Lock()

router = APIRouter()

MIN_SEARCH = 2


def get_card_class(name: str) -> type[BaseCard] | None:
    if name not in card_loader:
        return None
    return card_loader[name]


class HandlerStub:
    def __init__(self, user, arguments) -> None:
        self.user: User = user
        self.arguments = {}
        for key in arguments:
            if arguments[key]:
                self.arguments[key] = arguments[key]

    @property
    def current_user(self):
        return self.user

    def get_argument(self, name: str, default: str | None = None, strict: bool = True):
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

    CARD_TEMPLATE = None

    _user_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __init__(self, router: APIRouter) -> None:
        super().__init__(router)

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
            return self.get_user_by_name(name)

    def get_card_template(self):
        if not self.CARD_TEMPLATE:
            template_path = files("noc.services.card").joinpath("templates", "card.html.j2")
            with template_path.open("r", encoding="utf-8") as f:
                self.CARD_TEMPLATE = Template(f.read())
        return self.CARD_TEMPLATE

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
            "response_class": JSONResponse,
            "response_model": None,
            "name": "card-search",
            "description": "",
        }
        r = [route_card, route_search]
        actions = {}
        for card_name, card_class in card_loader.items():
            if card_class.name != card_name:
                raise ValueError(
                    f"Card module name '{card_name}' does not match card name '{card_class.name}'"
                )
            for action in card_class.actions or []:
                actions[action] = getattr(card_class, action)
        for action, endpoint in actions.items():
            r.append(
                {
                    "path": f"/api/card/resourcepool/{action}/",
                    "method": "POST",
                    "endpoint": endpoint,
                    "response_class": JSONResponse,
                    "response_model": None,
                    "name": f"card-{action}",
                    "description": "",
                }
            )
        return r

    def handler_card_view(
        self,
        card_type: str,
        card_id: str,
        request: Request,
        remote_user: str | None = Header(None, alias="Remote-User"),
    ):
        current_user = self.get_current_user(unquote(remote_user))
        if not current_user:
            raise HTTPException(404, "Not found")
        is_ajax = card_id == "ajax"
        handler = HandlerStub(current_user, request.query_params)
        tpl = get_card_class(card_type)
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
        self, scope: str, query: str, remote_user: str | None = Header(None, alias="Remote-User")
    ):
        query = query.strip()
        if not query or len(query) < MIN_SEARCH:
            raise HTTPException(400, "Query too short")
        card = get_card_class(scope)
        if not card:
            raise HTTPException(404, "Not found")
        if not hasattr(card, "search"):
            raise HTTPException(404, "Not found")
        handler = HandlerStub(self.get_current_user(remote_user), {})
        return card.search(handler, query)


# Install router
CardAPI(router)
