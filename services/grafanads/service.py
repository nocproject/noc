#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## GrafanaDS service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.ui import UIService
from check import CheckHandler
from annotations import AnnotationsHandler


class GrafanaDSService(UIService):
    name = "grafanads"
    process_name = "noc-%(name).10s-%(instance).2s"

    def get_handlers(self):
        return super(GrafanaDSService, self).get_handlers() + [
            ("^/annotations", AnnotationsHandler, {"service": self}),
            ("^/", CheckHandler)
        ]

if __name__ == "__main__":
    GrafanaDSService().start()
