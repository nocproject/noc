# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base dynamic dashboard
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging


class BaseDashboard(object):
    name = None

    class NotFound(Exception):
        pass

    def __init__(self, object):
        self.object = self.resolve_object(object)
        self.logger = logging.getLogger("dashboard.%s" % self.name)

    def resolve_object(self, object):
        """
        Resolve symbolic object link to name
        """
        return object

    def render(self):
        """
        Render dashboard and return grafana's dashboard JSON
        """
        return None
