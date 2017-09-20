#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Web Collector service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.service.base import Service
from noc.services.webcollector.handlers.strizh import StrizhRequestHandler


class WebCollectorService(Service):
    name = "webcollector"
    require_nsq_writer = True
    process_name = "noc-%(name).10s-%(pool).5s"

    def __init__(self):
        super(WebCollectorService, self).__init__()

    def get_handlers(self):
        r = []
        if config.webcollector.enable_strizh:
            r += [(
                r"^/api/webcollector/strizh/",
                StrizhRequestHandler,
                {"service": self}
            )]
        return r

if __name__ == "__main__":
    WebCollectorService().start()
