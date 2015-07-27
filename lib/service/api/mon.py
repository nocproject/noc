# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Monitoring API
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import ServiceAPI, api, ServiceAPIRequestHandler


class MonAPIRequestHandler(ServiceAPIRequestHandler):
    SUPPORTED_METHODS = ("GET", "POST")

    def get(self):
        """
        Simple GET response for Consul health check
        """
        self.write("OK")


class MonAPI(ServiceAPI):
    """
    Monitoring API
    """
    name = "mon"
    SUPPORTED_METHODS = ("GET", "POST")
    http_request_handler = MonAPIRequestHandler
    level = ServiceAPI.AL_NODE

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
