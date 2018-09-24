# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NBI API Base Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.apiaccess import APIAccessRequestHandler
from noc.core.perf import metrics
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

    def log_request(self, status_code, request):
        method = request.method
        uri = request.uri
        user = "-"  # @todo: API key name
        remote_ip = request.remote_ip
        agent = request.headers.get("User-Agent", "-")
        referer = request.headers.get("Referer", "-")
        self.logger.info(
            "%s %s - \"%s %s\" HTTP/1.1 %s \"%s\" %s %.2fms",
            remote_ip, user, method, uri, status_code,
            referer, agent,
            1000.0 * request.request_time()
        )
        metrics["api_requests", ("api", self.name)] += 1
