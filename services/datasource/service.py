#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# datasource service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
# NOC modules
from noc.core.service.base import Service
from noc.services.datasource.handler import DataSourceRequestHandler


class DataSourceService(Service):
    name = "datasource"

    def get_handlers(self):
        return [
            (r"/api/datasource/(\S+\.\S+)", DataSourceRequestHandler, {"service": self})
        ]


if __name__ == "__main__":
    DataSourceService().start()
