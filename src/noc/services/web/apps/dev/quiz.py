# ----------------------------------------------------------------------
# dev.quiz application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.dev.models.quiz import Quiz
from noc.services.web.base.extdocapplication import ExtDocApplication


class QuizApplication(ExtDocApplication):
    """
    Quiz application
    """

    title = "Quiz"
    menu = [_("Setup"), _("Quiz")]
    model = Quiz

    def deserialize(self, data):
        return super().deserialize(data)
