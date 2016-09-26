#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## mrt service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.base import Service
from mrt import MRTRequestHandler


class MRTService(Service):
    name = "mrt"

    def on_activate(self):
        self.sae = self.open_rpc("sae")

    def get_handlers(self):
        return [
            ("/api/mrt/", MRTRequestHandler, {"service": self})
        ]

if __name__ == "__main__":
    MRTService().start()
