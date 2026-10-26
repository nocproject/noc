# ---------------------------------------------------------------------
# RefBook Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.main.models.refbook import RefBook
from noc.main.models.refbookfield import RefBookField
from noc.services.web.base.extmodelapplication import ExtModelApplication
from noc.services.web.base.modelinline import ModelInline


class RefBookAdminApplication(ExtModelApplication):
    """
    RefBook application
    """

    model = RefBook

    title = _("Reference Books")
    menu = _("Setup") + " | " + _("Reference Books")
    default_ordering = ["name"]

    fields = ModelInline(RefBookField)
