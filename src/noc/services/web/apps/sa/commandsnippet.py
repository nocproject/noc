# ---------------------------------------------------------------------
# main.commandsnippet application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.sa.models.commandsnippet import CommandSnippet
from noc.services.web.base.extmodelapplication import ExtModelApplication


class CommandSnippetApplication(ExtModelApplication):
    """
    commandsnippet application
    """

    title = _("Command Snippets")
    menu = [_("Setup"), _("Command Snippets")]
    model = CommandSnippet
    query_fields = ["name__icontains"]


# @todo: syntax checking of snippet
