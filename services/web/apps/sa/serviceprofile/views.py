# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## sa.serviceprofile application
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.sa.models.serviceprofile import ServiceProfile


class ServiceProfileApplication(ExtDocApplication):
    """
    ServiceProfile application
    """
    title = "Service Profile"
    menu = "Setup | Service Profiles"
    model = ServiceProfile
