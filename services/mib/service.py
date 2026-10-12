#!./bin/python
# ----------------------------------------------------------------------
# MIB service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import BaseService


class MIBService(BaseService):
    name = "mib"
    use_mongo = True
