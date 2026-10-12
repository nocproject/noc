#!./bin/python
# ----------------------------------------------------------------------
# datastream service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import BaseService
from noc.config import config


class DataStreamService(BaseService):
    name = "datastream"
    use_mongo = True
    use_watchdog = config.watchdog.enable_watchdog
    traefik_routes_rule = "PathPrefix(`/api/datastream`)"
