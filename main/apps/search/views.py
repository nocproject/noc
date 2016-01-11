# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.search application
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.interfaces.base import UnicodeParameter
from noc.main.models.textindex import TextIndex


class SearchApplication(ExtApplication):
    """
    main.search application
    """
    title = "Search"
    menu = "Search"
    glyph = "search noc-preview"

    @view(url="^$", method=["POST"], access="launch", api=True,
          validate={
              "query": UnicodeParameter()
          })
    def api_search(self, request, query):
        def get_info(model, id):
            return [
                model.lower(),
                "history",
                {"args": [str(id)]}
            ]

        return [{
            "id": "%s:%s" % (qr.model, qr.object),
            "title": str(qr.title),
            "card": str(qr.card),
            "tags:": [str(x) for x in qr.tags],
            "info": get_info(qr.model, qr.object)
        } for qr in TextIndex.search(query)]
