# ---------------------------------------------------------------------
# inv.modelinterface application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.inv.models.modelinterface import ModelInterface
from noc.core.translation import ugettext as _


class ModelInterfaceApplication(ExtDocApplication):
    """
    ModelInterface application
    """

    title = _("Model Interface")
    menu = [_("Setup"), _("Model Interfaces")]
    model = ModelInterface
    query_fields = ["name__icontains", "description__icontains"]

    def cleaned_query(self, q):
        if "label" in q:
            q["name"] = q["label"]
            del q["label"]
        return super().cleaned_query(q)
