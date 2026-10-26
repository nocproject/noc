# ---------------------------------------------------------------------
# main.pool application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.main.models.pool import Pool
from noc.services.web.base.extdocapplication import ExtDocApplication


class PoolApplication(ExtDocApplication):
    """
    Pool application
    """

    title = _("Pool")
    menu = [_("Setup"), _("Pools")]
    model = Pool
    glyph = "database"
    default_ordering = ["name"]
