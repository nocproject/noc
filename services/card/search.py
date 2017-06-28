# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Card search
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.web
import ujson
# NOC modules
from card import CardRequestHandler
from noc.sa.models.useraccess import UserAccess


class SearchRequestHandler(CardRequestHandler):
    def get(self, *args, **kwargs):
        scope = self.get_argument("scope")
        query = self.get_argument("query")
        card = self.CARDS.get(scope)
        if not card or not hasattr(card, "search"):
            raise tornado.web.HTTPError(404)
        result = card.search(self, query)
        self.set_header("Content-Type", "application/json")
        self.write(
            ujson.dumps(result)
        )

    def get_user_domains(self):
        return UserAccess.get_domains(self.current_user)
