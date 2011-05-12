# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.Socket application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011
## The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import TreeApplication
from noc.inv.models import Socket, SocketCategory


class SocketApplication(TreeApplication):
    title = "Sockets"
    verbose_name = "Socket"
    verbose_name_plural = "Sockets"
    menu = "Setup | Sockets"
    model = Socket
    category_model = SocketCategory
