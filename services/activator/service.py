#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.base import Service
from api.activator import ActivatorAPI


class ActivatorService(Service):
    name = "activator"
    pooled = True
    api = [ActivatorAPI]

    def __init__(self):
        super(ActivatorService, self).__init__()

if __name__ == "__main__":
    ActivatorService().start()
