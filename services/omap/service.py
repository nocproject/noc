#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object Mapper service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.lib.service.base import Service
from noc.sa.interfaces.base import StringParameter
from api.omap import OMapAPI


class OMapService(Service):
    name = "omap"
    pooled = False

    # Dict parameter containing values accepted
    # via dynamic configuration
    config_interface = {
        "loglevel": StringParameter(
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            choices=["critical", "error", "warning", "info", "debug"]
        )
    }

    api = Service.api + [
        OMapAPI
    ]


if __name__ == "__main__":
    OMapService().start()
