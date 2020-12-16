# ----------------------------------------------------------------------
# gis.geocoder application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.lib.app.extapplication import ExtApplication, view
from noc.core.geocoder.loader import loader


class GeoCoderApplication(ExtApplication):
    name = "geocoder"

    @view(url=r"^lookup/$", method=["GET"], access="lookup", api=True)
    def api_lookup(self, request, ref=None):
        q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
        limit = int(q.get(self.limit_param, 0))
        start = int(q.get(self.start_param, 0))
        format = q.get(self.format_param)
        query = q.get(self.query_param)
        scope = config.geocoding.ui_geocoder
        geocoder = loader.get_class(scope)()
        data = [{"id": f"{scope}:{r.id}", "label": r.address} for r in geocoder.iter_query(query)]
        if start:
            data = data[start:]
        if limit:
            data = data[:limit]
        if format == "ext":
            return {"total": len(data), "success": True, "data": data}
        return data
