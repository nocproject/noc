# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.pyrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.main.models.pyrule import PyRule
from noc.core.translation import ugettext as _


class PyRuleApplication(ExtDocApplication):
    """
    PyRule application
    """
    title = _("PyRule")
    icon = "icon_py"
    menu = [_("Setup"), _("PyRule")]
    model = PyRule
    query_fields = ["name__icontains", "description__icontains", "source__icontains"]

    def field_full_name(self, o):
        return o.full_name
