# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dynamic menus for "sa" module
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC Modules
from noc.lib.app.site import DynamicMenu
from noc.lib.app.site import site
from noc.lib.app.access import HasPerm, PermitLogged
from noc.sa.models.commandsnippet import CommandSnippet


class SnippetsMenu(DynamicMenu):
    """
    Snippets submenu
    """
    title = "Snippets"
    icon = "icon_page_go"

    @property
    def items(self):
        run_perm = HasPerm("sa:runsnippet:launch")
        for s in CommandSnippet.objects.filter(display_in_menu=True).order_by(
            "name"):
            if s.permission_name:
                s_perm = HasPerm(s.effective_permission_name)
            else:
                s_perm = PermitLogged()
            yield (s.name,
                   "sa.runsnippet",
                   lambda user: (run_perm & s_perm).check(None, user)
                )


DYNAMIC_MENUS = [
    SnippetsMenu()
]
