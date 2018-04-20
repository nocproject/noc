# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.managedobjectprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.sa.models import ManagedObjectProfile


class ManagedObjectProfileApplication(ExtModelApplication):
    """
    ManagedObjectProfile application
    """
    title = "Managed Object Profile"
    menu = "Setup | Managed Object Profiles"
    model = ManagedObjectProfile

    def field_row_class(self, o):
        return o.style.css_class_name if o.style else ""

    def field_mo_count(self, o):
        return o.managedobject_set.count()
