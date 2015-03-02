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
    def get_interface_defaults(self):
        return {
            "admin_status": True
        }

    def get_subinterface_defaults(self):
        return {
            "admin_status": True
        }
