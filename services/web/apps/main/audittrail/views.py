# ---------------------------------------------------------------------
# main.audittrail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
import orjson

# NOC modules
from noc.services.web.base.extapplication import ExtApplication, view
from noc.core.translation import ugettext as _
from noc.core.clickhouse.connect import connection
from noc.models import get_object, get_model
from noc.core.comp import smart_text

logger = logging.getLogger(__name__)


class AuditTrailApplication(ExtApplication):
    """
    AuditTrails application
    """

    title = _("Audit Trail")
    menu = _("Audit Trail")

    def g_model(self, model_id):
        try:
            md = get_model(model_id)
            if md and hasattr(md, "name"):
                return md
        except Exception as e:
            logger.info("No model: Error %s", e)
            return None

    def field_object_name(self, o):
        try:
            return smart_text(get_object(o.model_id, o.object))
        except AssertionError:
            return smart_text(o.object)

    def instance_to_dict(self, o):
        return {
            "timestamp": o["timestamp"],
            "user": o["user"],
            "model_id": o["model_name"],
            "fav_status": False,
            "object": o["object_id"],
            "op": o["op"],
            "changes": orjson.loads(o["changes"]),
            "expires": o["timestamp"],
            "id": o["change_id"],
            "object_name": o["object_name"],
        }

    def list_data(self, request, formatter):
        """
        Returns a list of requested object objects
        """
        q = self.parse_request_query(request)
        print("QUERY", q)
        # QUERY {'_dc': '1727112212246', '__format': 'ext', '__page': '1', '__start': '0', '__limit': '50'}
        ch = connection(read_only=True)
        data = ch.execute(
            "SELECT * FROM noc.changes ORDER BY timestamp LIMIT %s OFFSET %s FORMAT JSON",
            args=[int(q["__limit"]), int(q["__start"])],
            return_raw=True,
        )
        data = orjson.loads(data)
        out = []
        for d in data["data"]:
            out.append(self.instance_to_dict(d))
        return self.response(
            {"total": data["statistics"]["rows_read"], "success": True, "data": out},
            status=self.OK,
        )

    @view(method=["GET"], url=r"^$", access="read", api=True)
    def api_list(self, request):
        return self.list_data(request, None)
