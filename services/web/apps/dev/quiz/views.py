# ----------------------------------------------------------------------
# dev.quiz application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.web.app.extdocapplication import ExtDocApplication
from noc.dev.models.quiz import Quiz
from noc.core.translation import ugettext as _


class QuizApplication(ExtDocApplication):
    """
    Quiz application
    """

    title = "Quiz"
    menu = [_("Setup"), _("Quiz")]
    model = Quiz

    def deserialize(self, data):
        return super().deserialize(data)
