# ----------------------------------------------------------------------
# config API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from fastapi import APIRouter, Path, Header, HTTPException
from fastapi.responses import HTMLResponse

# NOC modules
from ..base import BaseAPI, FORBIDDEN_MESSAGE
from noc.services.card.card import card_request_handler

router = APIRouter()


class CardAPI(BaseAPI):
    api_name = "card"
    openapi_tags = ["card API"]

    def get_routes(self):
        route_card = {
            "path": "/api/card/view/{card_type}/{card_id}/", # {id1}
            "method": "GET",
            "endpoint": card_request_handler.get,  # self.handler_card,
            "response_class": HTMLResponse,
            "response_model": None,
            "name": "card",
            "description": "",
        }
        return [route_card]

    async def handler_card(
        self, remote_user: Optional[str] = Header(None, alias="Remote-User")
    ):
        return "OK"


# Install router
CardAPI(router)
