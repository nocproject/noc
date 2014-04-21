# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ip.ippool application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.ip.models import IPPool


class IPPoolApplication(ExtModelApplication):
    """
    IPPool application
    """
    title = "IP Pool"
    menu = "Setup | IP Pools"
    model = IPPool
