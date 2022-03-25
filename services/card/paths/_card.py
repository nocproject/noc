# ----------------------------------------------------------------------
# Card API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.core.service.loader import get_service
from noc.services.card.card import card_request_handler


router1 = APIRouter()


@router1.post("/api/card/search/")
def api_card_search():
    service = get_service()
    return "-api_card_search-"


@router1.get("/api/card/view/")
def api_card_view():
    return "-api_card_view-"

