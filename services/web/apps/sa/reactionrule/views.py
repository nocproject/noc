# ---------------------------------------------------------------------
# sa.reactionrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication
from noc.sa.models.reactionrule import ReactionRule
from noc.core.translation import ugettext as _


class ReactionRuleApplication(ExtDocApplication):
    """
    ObjectNotification application
    """

    title = _("Reaction Rules")
    menu = [_("Setup"), _("Reaction Rule")]
    model = ReactionRule
