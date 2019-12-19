# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.audittrail application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import logging
from pymongo import ReadPreference

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.audittrail import AuditTrail
from noc.core.translation import ugettext as _
from noc.models import get_object, get_model
from noc.core.comp import smart_text

logger = logging.getLogger(__name__)


class AuditTrailApplication(ExtDocApplication):
    """
    AuditTrails application
    """

    title = _("Audit Trail")
    menu = _("Audit Trail")
    model = AuditTrail
    query_fields = ["model_id", "user"]

    def g_model(self, model_id):
        try:
            md = get_model(model_id)
            if md and hasattr(md, "name"):
                return md
        except Exception as e:
            logger.info("No model: Error %s", e)
            return None

    def queryset(self, request, query=None):
        """
        Filter records for lookup
        """
        if query and self.query_fields:
            for model_id in [
                list(set(a["models"]))
                for a in self.model._get_collection()
                .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
                .aggregate(
                    [
                        {"$unwind": "$model_id"},
                        {"$group": {"_id": "null", "models": {"$push": "$model_id"}}},
                        {"$project": {"models": True, "_id": False}},
                    ]
                )
            ][0]:
                model = self.g_model(model_id)
                if model is None:
                    continue
                for ob in model.objects.filter(name=str(query)):
                    if ob:
                        return self.model.objects.filter(model_id=model_id, object=str(ob.id))

            else:
                return self.model.objects.filter(self.get_Q(request, query))
        else:
            return self.model.objects.all()

    def field_object_name(self, o):
        try:
            return smart_text(get_object(o.model_id, o.object))
        except AssertionError:
            return smart_text(o.object)
