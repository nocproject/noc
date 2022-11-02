# ---------------------------------------------------------------------
# KBEntryTemplate Manager
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extmodelapplication import ExtModelApplication
from noc.kb.models.kbentrytemplate import KBEntryTemplate
from noc.core.translation import ugettext as _


class KBEntryApplication(ExtModelApplication):
    """
    AdministrativeDomain application
    """

    title = _("Templates")
    menu = [_("Setup"), _("Templates")]
    model = KBEntryTemplate
