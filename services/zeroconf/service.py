#!./bin/python
# ----------------------------------------------------------------------
# zk service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import BaseService


class ZeroConfService(BaseService):
    name = "zeroconf"
    use_mongo = True
