#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Object Mapper service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import Service
from api.omap import OMapAPI


class OMapService(Service):
    name = "omap"
    process_name = "noc-%(name).10s-%(instance).3s"

    api = Service.api + [
        OMapAPI
    ]

if __name__ == "__main__":
    OMapService().start()
