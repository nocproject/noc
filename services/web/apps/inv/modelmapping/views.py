# ---------------------------------------------------------------------
# inv.modelmapping application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.inv.models.modelmapping import ModelMapping
from noc.core.translation import ugettext as _


class ModelMappingApplication(ExtDocApplication):
    """
    ModelMapping application
    """

    title = _("Model Mapping")
    menu = [_("Setup"), _("Model Mapping")]
    model = ModelMapping
