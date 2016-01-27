# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed object status handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


def set_up(event):
    event.managed_object.set_status(True, event.timestamp)


def set_down(event):
    event.managed_object.set_status(False, event.timestamp)
