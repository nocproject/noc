# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dev.quiz application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
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
        print repr(data)
        return super(QuizApplication, self).deserialize(data)
