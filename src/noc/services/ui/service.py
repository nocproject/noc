#!./bin/python
# ----------------------------------------------------------------------
# UI service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.service.base import BaseService


class UIService(BaseService):
    name = "ui"
    use_mongo = True
    use_watchdog = config.watchdog.enable_watchdog
