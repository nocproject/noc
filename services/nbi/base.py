# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NBI API Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.apiaccess import APIAccessRequestHandler
from noc.core.log import PrefixLoggerAdapter


class NBIAPI(APIAccessRequestHandler):
    """
    Asynchronous NBI API handler
    """
    name = None

    def initialize(self, service):
        self.service = service
        self.logger = PrefixLoggerAdapter(self.service.logger, self.name)

    @property
    def executor(self):
        return self.service.get_executor("max")

    def get_access_tokens_set(self):
        return {"nbi:*", "nbi:%s" % self.name}
