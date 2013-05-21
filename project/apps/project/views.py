# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## project.project application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.project.models import Project


class ProjectApplication(ExtModelApplication):
    """
    Project application
    """
    title = "Project"
    menu = "Projects"
    model = Project
    query_fields = ["code", "name"]
