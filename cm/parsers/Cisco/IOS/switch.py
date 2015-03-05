# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IOS-based switch parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseIOSParser


class IOSSwitchParser(BaseIOSParser):
    def get_interface_defaults(self, name):
        r = super(IOSSwitchParser, self).get_interface_defaults(name)
        r["admin_status"] = True
        return r

    def get_subinterface_defaults(self):
        return {
            "admin_status": True
        }
