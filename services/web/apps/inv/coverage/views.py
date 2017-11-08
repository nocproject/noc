# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# inv.coverage application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.translation import ugettext as _
from noc.inv.models.coverage import Coverage
from noc.inv.models.coveredbuilding import CoveredBuilding
from noc.inv.models.coveredobject import CoveredObject
from noc.lib.app.docinline import DocInline
# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication


class CoverageApplication(ExtDocApplication):
    """
    Coverage application
    """
    title = _("Coverage")
    menu = [_("Setup"), _("Coverage")]
    model = Coverage
    query_fields = ["name", "description"]

    objects = DocInline(CoveredObject)
    buildings = DocInline(CoveredBuilding)
