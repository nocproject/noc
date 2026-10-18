# ----------------------------------------------------------------------
# gis.geocoder application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.config import config
from noc.services.web.base.extapplication import ExtApplication, api
from noc.core.geocoder.base import geocoder_loader


class GeoCoderApplication(ExtApplication):
    name = "geocoder"

    @api.get(r"^lookup/$", access="lookup")
    def api_lookup(self, request: HttpRequest, ref=None):
        q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
        limit = int(q.get(self.limit_param, 0))
        start = int(q.get(self.start_param, 0))
        fmt = q.get(self.format_param)
        query = q.get(self.query_param)
        scope = config.geocoding.ui_geocoder
        geocoder = geocoder_loader.get(scope)()
        g_data = list(geocoder.iter_query(query))
        if start:
            g_data = g_data[start:]
        if limit:
            g_data = g_data[: limit - 1]
        data = [
            {
                "id": f"{scope}:{r.address}",
                "label": r.address if r.exact else f"{r.address}...",
                "style": "geo-loose" if not r.exact else "",
                "is_loose": not r.exact,
            }
            for r in g_data
        ]
        if fmt == "ext":
            return {"total": len(data), "success": True, "data": data}
        return data
