#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Node Manager service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.lib.service.base import Service
from noc.sa.interfaces.base import StringParameter


class NMService(Service):
    name = "nm"
    # One active Node Manager per node
    leader_group_name = "nm-%(dc)s-%(node)s"

    # Dict parameter containing values accepted
    # via dynamic configuration
    config_interface = {
        "loglevel": StringParameter(
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            choices=["critical", "error", "warning", "info", "debug"]
        )
    }


if __name__ == "__main__":
    NMService().start()
