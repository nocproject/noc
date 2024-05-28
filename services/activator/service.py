#!./bin/python
# ----------------------------------------------------------------------
# Activator service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config

class ActivatorService(FastAPIService):
    name = "activator"
    pooled = True
    process_name = "noc-%(name).10s-%(pool).5s"
    use_telemetry = True
    use_watchdog = config.watchdog.enable_watchdog


if __name__ == "__main__":
    ActivatorService().start()
