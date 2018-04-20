# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## peer.organisation application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.peer.models import Organisation

class OrganisationApplication(ExtModelApplication):
    """
    Person application
    """
    title = "Organisations"
    menu = "Setup | Organisations"
    model = Organisation
    query_fields = ["organisation__icontains","org_name__icontains"]

