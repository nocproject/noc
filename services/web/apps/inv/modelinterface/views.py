# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.modelinterface application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.inv.models.modelinterface import ModelInterface
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


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
        return super(ModelInterfaceApplication, self).cleaned_query(q)
