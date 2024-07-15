# ----------------------------------------------------------------------
# sa.modeltemplates application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.main.models.modeltemplate import ModelTemplate
from noc.core.translation import ugettext as _


class ModelTemplateApplication(ExtDocApplication):
    """
    Model Template application
    """

    title = "Model Template"
    menu = [_("Setup"), _("Model Templates")]
    model = ModelTemplate
    query_fields = ["name__icontains", "description__icontains"]
    default_ordering = ["name"]
