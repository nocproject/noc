#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Probe Config service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.lib.service.base import Service
from noc.sa.interfaces.base import StringParameter
from api.probeconf import ProbeConfAPI


class ProbeConfService(Service):
    name = "probeconf"
    # One active object probe conf per pool
    leader_group_name = "probeconf-%(pool)s"

    # Dict parameter containing values accepted
    # via dynamic configuration
    config_interface = {
        "loglevel": StringParameter(
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            choices=["critical", "error", "warning", "info", "debug"]
        )
    }

    api = Service.api + [
        ProbeConfAPI
    ]


if __name__ == "__main__":
    ProbeConfService().start()
