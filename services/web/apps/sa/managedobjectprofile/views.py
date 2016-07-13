# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.managedobjectprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.core.translation import ugettext as _


class ManagedObjectProfileApplication(ExtModelApplication):
    """
    ManagedObjectProfile application
    """
    title = _("Managed Object Profile")
    menu = [_("Setup"), _("Managed Object Profiles")]
    model = ManagedObjectProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""

    def field_mo_count(self, o):
        return o.managedobject_set.count()
