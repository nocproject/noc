# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# wf.workflow application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.wf.models.workflow import Workflow
from noc.core.translation import ugettext as _


class WorkflowApplication(ExtDocApplication):
    """
    Workflow application
    """
    title = "Workflows"
    menu = [_("Setup"), _("Workflow")]
    model = Workflow
