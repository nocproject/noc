# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# main.commandsnippet application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.sa.models.commandsnippet import CommandSnippet
from noc.core.translation import ugettext as _


class CommandSnippetApplication(ExtModelApplication):
    """
    commandsnippet application
    """
    title = _("Command Snippets")
    menu = [_("Setup"), _("Command Snippets")]
    model = CommandSnippet
    query_fields = ["name__icontains"]

# @todo: syntax checking of snippet

