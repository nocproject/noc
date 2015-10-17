#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Probe Config service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.base import Service
from api.probeconf import ProbeConfAPI


class ProbeConfService(Service):
    name = "probeconf"
    pooled = True

    api = Service.api + [
        ProbeConfAPI
    ]


if __name__ == "__main__":
    ProbeConfService().start()
