# ----------------------------------------------------------------------
# sa.resourcetemplates application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.resourcetemplate import ResourceTemplate
from noc.core.translation import ugettext as _


class ResourceTemplateApplication(ExtDocApplication):
    """
    Resource Template application
    """

    title = "Resource Template"
    menu = [_("Setup"), _("Resource Templates")]
    model = ResourceTemplate
    query_fields = ["name__icontains", "description__icontains"]
    default_ordering = ["name"]
