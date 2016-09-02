# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.systemtemplate application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extmodelapplication import ExtModelApplication, view
from noc.main.models.systemtemtemplate import SystemTemplate
from noc.core.translation import ugettext as _


class SystemTemplateApplication(ExtModelApplication):
    """
    SystemTemplate application
    """
    title = _("System Templates")
    menu = [_("Setup"), _("System Templates")]
    model = SystemTemplate
    query_fields = ["name__icontains"]

