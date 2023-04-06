#!./bin/python
# ----------------------------------------------------------------------
# bulkhandler service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class BulkHandlerService(FastAPIService):
    name = "bulkhandler"


if __name__ == "__main__":
    BulkHandlerService().start()
