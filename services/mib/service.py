#!./bin/python
# ----------------------------------------------------------------------
# MIB service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class MIBService(FastAPIService):
    name = "mib"
    use_mongo = True


if __name__ == "__main__":
    MIBService().start()
