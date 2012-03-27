# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.pyrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models import PyRule


class PyRuleApplication(ExtModelApplication):
    """
    PyRule application
    """
    title = "PyRule"
    menu = "Setup | PyRule"
    model = PyRule
    icon = "icon_script_edit"
    query_fields = ["name__icontains"]
