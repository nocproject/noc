#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# mib service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import Service
from noc.services.mib.api.mib import MIBAPI


class MIBService(Service):
    name = "mib"
    api = [MIBAPI]


if __name__ == "__main__":
    MIBService().start()
