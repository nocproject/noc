#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Node Manager service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.base import Service


class NMService(Service):
    name = "nm"
    # One active Node Manager per node
    leader_group_name = "nm-%(dc)s-%(node)s"

if __name__ == "__main__":
    NMService().start()
