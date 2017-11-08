# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.pyrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.handler import get_handler
from noc.core.translation import ugettext as _
# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication
from noc.main.models.pyrule import PyRule


class PyRuleApplication(ExtModelApplication):
    """
    PyRule application
    """
    title = _("PyRule")
    icon = "icon_py"
    menu = [_("Setup"), _("PyRule")]
    model = PyRule
    query_fields = ["name__icontains"]

    def clean(self, data):
        data = super(PyRuleApplication, self).clean(data)
        if data.get("handler"):
            try:
                get_handler(data["handler"])
            except ImportError, why:
                raise ValueError("Invalid handler: %s" % why)
        else:
            try:
                PyRule.compile_text(data["text"])
            except SyntaxError, why:
                raise ValueError("Syntax error: %s" % why)
        return data
