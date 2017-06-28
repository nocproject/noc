# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.modelmapping application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.inv.models.modelmapping import ModelMapping
from noc.core.translation import ugettext as _


class ModelMappingApplication(ExtDocApplication):
    """
    ModelMapping application
    """
    title = _("Model Mapping")
    menu = [_("Setup"), _("Model Mapping")]
    model = ModelMapping
