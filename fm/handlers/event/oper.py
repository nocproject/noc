# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed Object operations
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


def reboot(event):
    """
    Reload managed object
    """
    event.managed_object.scripts.reboot()
