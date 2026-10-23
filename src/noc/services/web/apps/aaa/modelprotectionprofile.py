# ----------------------------------------------------------------------
# aaa.modelprotectionprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, api
from noc.aaa.models.modelprotectionprofile import (
    ModelProtectionProfile,
    FieldAccess,
    FIELD_PERMISSIONS,
)
from noc.core.translation import ugettext as _
from noc.models import get_model, is_document
from noc.core.comp import smart_text

IGNORED_FIELDS = {"id", "bi_id"}


class ModelProtectionProfileApplication(ExtDocApplication):
    """
    ModelProtection Profile application
    """

    title = "ModelProtection Profile"
    menu = [_("Setup"), _("ModelProtection Profile")]
    model = ModelProtectionProfile
    # glyph = "key"

    @api.get(r"^(?P<model_id>\w+\.\w+)/fields/lookup/$", access="lookup")
    def api_model_fields_lookup(self, request: HttpRequest, model_id):
        try:
            model = get_model(model_id=model_id)
        except AssertionError:
            return self.render_json(
                {"status": False, "message": f"Not found model by id: {model_id}"},
                status=self.NOT_FOUND,
            )
        # Get links
        if is_document(model):
            fields = model._fields
        else:
            fields = [f.name for f in model._meta.fields]
        return [{"id": name, "label": name} for name in fields if name not in IGNORED_FIELDS]

    def instance_to_dict(self, o, fields=None, nocustom=False):
        if isinstance(o, FieldAccess):
            return {
                "name": smart_text(o.name),
                "name__label": smart_text(o.name),
                "permission": o.permission,
                "permission__label": FIELD_PERMISSIONS[o.permission],
            }
        return super().instance_to_dict(o, fields, nocustom)
