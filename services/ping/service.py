#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ping service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.service.base import Service


class PingService(Service):
    name = "ping"


if __name__ == "__main__":
    PingService().run()
