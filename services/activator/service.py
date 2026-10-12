#!./bin/python
# ----------------------------------------------------------------------
# Activator service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import BaseService
from noc.config import config


class ActivatorService(BaseService):
    name = "activator"
    pooled = True
    process_name = "noc-%(name).10s-%(pool).5s"
    use_telemetry = True
    use_watchdog = config.watchdog.enable_watchdog
