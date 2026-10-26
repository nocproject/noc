# ----------------------------------------------------------------------
# wf.wfmigration application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.wf.models.wfmigration import WFMigration


class WFMigrationApplication(ExtDocApplication):
    """
    WFMigration application
    """

    title = "WF Migration"
    menu = [_("Setup"), _("Migrations")]
    model = WFMigration
