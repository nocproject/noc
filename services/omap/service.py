#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Object Mapper service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from __future__ import absolute_import
# NOC modules
from noc.core.service.base import Service
from .api.omap import OMapAPI


class OMapService(Service):
    name = "omap"

    api = Service.api + [
        OMapAPI
    ]


if __name__ == "__main__":
    OMapService().start()
