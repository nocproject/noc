#!./bin/python
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.service.base import BaseService


class NBIService(BaseService):
    name = "nbi"
    use_mongo = True
    use_router = True
    use_watchdog = config.watchdog.enable_watchdog

    def __init__(self) -> None:
        super().__init__()
        self.collect_req_api_metric = True
