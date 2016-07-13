# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## wf.solution application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.wf.models.solution import Solution
from noc.wf.models.workflow import Workflow
from noc.core.translation import ugettext as _


class SolutionApplication(ExtDocApplication):
    """
    Solution application
    """
    title = _("Solution")
    menu = [_("Setup"), _("Solutions")]
    model = Solution

    def field_wf_count(self, obj):
        return Workflow.objects.filter(solution=obj.id).count()
