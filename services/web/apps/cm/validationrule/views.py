# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# cm.validationrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.cm.models.validationrule import ValidationRule
from noc.cm.models.objectfact import ObjectFact
from noc.sa.models.managedobject import ManagedObject
from noc.core.translation import ugettext as _


class ValidationRuleApplication(ExtDocApplication):
    """
    ValidationRule application
    """
    title = _("Validation Rule")
    menu = [_("Setup"), _("Validation Rules")]
    model = ValidationRule

    def field_scope(self, o):
        try:
            h = o.get_handler()
        except ImportError:
            return ""
        if h:
            r = []
            if h.is_interface():
                r += ["interface"]
            if h.is_object():
                r += ["object"]
            if h.is_topology():
                r += ["topology"]
            return ", ".join(r)
        else:
            return ""

    def field_hits(self, o):
        return ObjectFact.objects.filter(attrs__rule=str(o.id)).count()

    @view(url="^config/(?P<path>.+)$", access=True, api=True)
    def api_config_form(self, request, path):
        """
        Static file server
        """
        if not path.startswith("cm/validators/") and not path.startswith("solutions/"):
            return self.response_not_found()
        return self.render_static(request, path, document_root=".")

    @view(url="^(?P<id>[0-9a-f]{24})/hits/$", access="read", api=True)
    def api_hits(self, request, id):
        rule = self.get_object_or_404(ValidationRule, id=id)
        ar = ObjectFact._get_collection().aggregate([
            {
                "$match": {
                    "attrs.rule": str(rule.id)
                }
            },
            {
                "$group": {
                    "_id": "$object",
                    "hits": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "hits": -1
                }
            }
        ])
        r = []
        for x in ar["result"]:
            mo = ManagedObject.get_by_id(x["_id"])
            if not mo:
                continue
            r += [{
                "managed_object_id": mo.id,
                "managed_object": mo.name,
                "address": mo.address,
                "platform": mo.platform,
                "hits": x["hits"]
            }]
        return r
