#!./bin/python
# ----------------------------------------------------------------------
# Activator service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService


class ActivatorService(FastAPIService):
    name = "activator"
    pooled = True
    process_name = "noc-%(name).10s-%(pool).5s"
    use_telemetry = True


if __name__ == "__main__":
    ActivatorService().start()
