# ----------------------------------------------------------------------
# sa.modeltemplates application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api, HttpResponse
from noc.main.models.modeltemplate import ModelTemplate, Param
from noc.core.translation import ugettext as _
from noc.models import get_model


class ModelTemplateApplication(ExtDocApplication):
    """
    Model Template application
    """

    title = "Model Template"
    menu = [_("Setup"), _("Model Templates")]
    model = ModelTemplate
    query_fields = ["name__icontains", "description__icontains"]
    default_ordering = ["name"]

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields=fields, nocustom=nocustom)
        if isinstance(o, Param):
            field = [x for x in ModelTemplate.get_templating_fields() if x.id == r["name"]]
            if field:
                r["name__label"] = field[0].label
            else:
                r["name__label"] = r["name"].capitalize()
            if field and field[0].model_id and r["default_expression"]:
                m = get_model(field[0].model_id)
                r |= {
                    "default_dictionary": r["default_expression"],
                    "default_dictionary__label": m.get_by_id(r["default_expression"]).name,
                }
        return r

    def clean(self, data):
        for p in data.get("params") or []:
            if "default_dictionary" in p:
                del p["default_dictionary"]
            if "default_expression" in p:
                p["default_expression"] = str(p["default_expression"])
        return super().clean(data)

    @api.get(r"^directory/(?P<type>\w+)/fields/?$", access="read")
    def api_get_template_fields(self, request: HttpRequest, type):
        r = ModelTemplate.get_templating_fields()
        return sorted([x.model_dump() for x in r], key=lambda x: x["id"].lower())

    @api.get(r"^directory/(?P<type>\w+)/fields/(?P<field>[\w_]+)/?$", access="read")
    def api_get_template_field(self, request: HttpRequest, type, field):
        r = [x for x in ModelTemplate.get_templating_fields() if x.id == field]
        if not r:
            return HttpResponse("", status=self.NOT_FOUND)
        return r[0].model_dump()
