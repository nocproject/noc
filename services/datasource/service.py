#!./bin/python
# ----------------------------------------------------------------------
# datasource service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.tornado import TornadoService
from noc.services.datasource.handler import DataSourceRequestHandler


class DataSourceService(TornadoService):
    name = "datasource"
    use_mongo = True

    def get_handlers(self):
        return [(r"/api/datasource/(\S+\.\S+)", DataSourceRequestHandler, {"service": self})]


if __name__ == "__main__":
    DataSourceService().start()
