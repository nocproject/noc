# ---------------------------------------------------------------------
# main.search application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extapplication import ExtApplication, view
from noc.sa.interfaces.base import UnicodeParameter
from noc.main.models.textindex import TextIndex
from noc.models import get_model
from noc.core.translation import ugettext as _


class SearchApplication(ExtApplication):
    """
    main.search application
    """

    title = _("Search")
    menu = _("Search")
    glyph = "search noc-preview"

    @view(
        url="^$", method=["POST"], access="launch", api=True, validate={"query": UnicodeParameter()}
    )
    def api_search(self, request, query):
        r = []
        for qr in TextIndex.search(query):
            model = get_model(qr["model"])
            if not model:
                continue  # Invalid model
            url = model.get_search_result_url(qr["object"])
            r += [
                {
                    "title": str(qr["title"]),
                    "card": str(qr["card"]),
                    "tags:": [str(x) for x in (qr.get("tags", []) or [])],
                    "url": url,
                    "score": qr["score"],
                }
            ]
        return r
