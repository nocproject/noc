# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# aaa.modelprotectionprofile application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.aaa.models.modelprotectionprofile import ModelProtectionProfile
from noc.core.translation import ugettext as _
from noc.models import get_model, is_document

IGNORED_FIELDS = {"id", "bi_id"}


class ModelProtectionProfileApplication(ExtDocApplication):
    """
    ModelProtection Profile application
    """

    title = "ModelProtection Profile"
    menu = [_("Setup"), _("ModelProtection Profile")]
    model = ModelProtectionProfile
    # glyph = "key"

    @view(url=r"^(?P<model_id>\w+\.\w+)/fields/lookup/$", method=["GET"], access="lookup", api=True)
    def api_links(self, request, model_id):
        try:
            model = get_model(model_id=model_id)
        except AssertionError:
            return self.render_json(
                {"status": False, "message": "Not found model by id: %s" % model_id},
                status=self.NOT_FOUND,
            )
        # Get links
        if is_document(model):
            fields = model._fields
        else:
            fields = [f.name for f in model._meta.fields]
        return [{"id": name, "label": name} for name in fields if name not in IGNORED_FIELDS]
