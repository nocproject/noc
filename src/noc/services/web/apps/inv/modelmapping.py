# ---------------------------------------------------------------------
# inv.modelmapping application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.inv.models.modelmapping import ModelMapping
from noc.services.web.base.extdocapplication import ExtDocApplication


class ModelMappingApplication(ExtDocApplication):
    """
    ModelMapping application
    """

    title = _("Model Mapping")
    menu = [_("Setup"), _("Model Mapping")]
    model = ModelMapping
