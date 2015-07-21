# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Monitoring API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import ServiceAPI, api


class MonAPI(ServiceAPI):
    """
    Monitoring API
    """
    name = "mon"

    @api
    def stats(self):
        """
        Get service statistics.
        Returns
        status: True
        """
        return {
            "status": True
        }
