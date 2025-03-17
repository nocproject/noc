# ---------------------------------------------------------------------
# fm.dispositionrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.fm.models.dispositionrule import DispositionRule
from noc.core.translation import ugettext as _


class DispositionRuleApplication(ExtDocApplication):
    """
    DispositionRule application
    """

    title = _("Disposition Rule")
    menu = [_("Setup"), _("Disposition Rules")]
    model = DispositionRule
    parent_field = "replace_rule"
    query_condition = "icontains"
