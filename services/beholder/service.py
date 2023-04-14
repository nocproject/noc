#!./bin/python
# ----------------------------------------------------------------------
# beholder service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class BeholderService(FastAPIService):
    name = "beholder"


if __name__ == "__main__":
    BeholderService().start()
