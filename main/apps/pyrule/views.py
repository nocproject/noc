# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.pyrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models.pyrule import PyRule


class PyRuleApplication(ExtModelApplication):
    """
    PyRule application
    """
    title = "PyRule"
    icon = "icon_py"
    menu = "Setup | PyRule"
    model = PyRule
    query_fields = ["name__icontains"]

    def clean(self, data):
        data = super(PyRuleApplication, self).clean(data)
        try:
            PyRule.compile_text(data["text"])
        except SyntaxError, why:
            raise ValueError("Syntax error: %s" % why)
        return data
