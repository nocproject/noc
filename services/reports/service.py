#!./bin/python
# ----------------------------------------------------------------------
# Reports service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class MyService(FastAPIService):
    name = "reports"
    use_mongo = True


if __name__ == "__main__":
    MyService().start()
