#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# GrafanaDS service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.service.ui import UIService
from noc.services.grafanads.check import CheckHandler
from noc.services.grafanads.annotations import AnnotationsHandler


class GrafanaDSService(UIService):
    name = "grafanads"
    use_mongo = True

    def get_handlers(self):
        return super(GrafanaDSService, self).get_handlers() + [
            ("^/api/grafanads/annotations", AnnotationsHandler, {"service": self}),
            ("^/api/grafanads/", CheckHandler),
        ]


if __name__ == "__main__":
    GrafanaDSService().start()
