# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.search application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.sa.interfaces.base import UnicodeParameter
from noc.main.models.fts_queue import FTSQueue


class SearchApplication(ExtApplication):
    """
    main.search application
    """
    title = "Search"
    menu = "Search"
    INDEX = "local/index"
    LIMIT = 1000
    glyph = "search noc-preview"

    @view(url="^$", method=["POST"], access="launch", api=True,
          validate={
              "query": UnicodeParameter()
          })
    def api_search(self, request, query):
        user = request.user
        index = open_dir(self.INDEX, readonly=True)
        parser = QueryParser("content", index.schema)
        r = []
        q = parser.parse(query)
        with index.searcher() as searcher:
            for hit in searcher.search(q, limit=self.LIMIT):
                o = FTSQueue.get_object(hit["id"])
                if not o:
                    continue  # Not found in database
                li = o.get_search_info(user)
                if not li:
                    continue  # Not accessible for user
                r += [{
                    "id": hit["id"],
                    "title": hit["title"],
                    "card": hit["card"],
                    "tags": hit.get("tags"),
                    "info": li
                }]
        return r
