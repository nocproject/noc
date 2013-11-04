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
from noc.sa.interfaces.base import StringParameter
from noc.main.models import fts_models


class SearchApplication(ExtApplication):
    """
    main.search application
    """
    title = "Search"
    menu = "Search"
    INDEX = "local/index"
    LIMIT = 1000

    @view(url="^$", method=["POST"], access="launch", api=True,
          validate={
              "query": StringParameter()
          })
    def api_search(self, request, query):
        user = request.user
        index = open_dir(self.INDEX, readonly=True)
        parser = QueryParser("content", index.schema)
        r = []
        q = parser.parse(query)
        with index.searcher() as searcher:
            for hit in searcher.search(q, limit=self.LIMIT):
                o = self.get_object(hit["id"])
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

    def get_object(self, id):
        m, i = id.split(":")
        if not m in fts_models:
            return None
        model = fts_models[m]
        try:
            return model.objects.get(id=int(i))
        except model.DoesNotExist:
            return None
