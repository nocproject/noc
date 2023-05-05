#!./bin/python
# ----------------------------------------------------------------------
# BH service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class BHService(FastAPIService):
    name = "bh"


if __name__ == "__main__":
    BHService().start()
