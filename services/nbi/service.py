#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six

# NOC modules
from noc.core.service.base import Service
from noc.config import config
from noc.services.nbi.loader import loader
from noc.core.perf import metrics
from noc.services.nbi.base import NBIAPI


class NBIService(Service):
    name = "nbi"
    require_nsq_writer = True
    use_mongo = True
    if config.features.traefik:
        traefik_backend = "nbi"
        traefik_frontend_rule = "PathPrefix:/api/nbi"

    def iter_api(self):
        """
        Iterate existing API handler classes

        :return: Yields API class
        """
        for api in loader.iter_classes():
            handler = loader[api]
            if handler:
                self.logger.info("[%s] Initializing API", api)
                yield handler
            else:
                self.logger.info("[%s] Failed to initialize API", api)

    def get_handlers(self):
        r = []
        for api in self.iter_api():
            path = api.get_path()
            if isinstance(path, six.string_types):
                r += [("/api/nbi/%s" % api.get_path(), api, {"service": self})]
            else:
                r += [("/api/nbi/%s" % p, api, {"service": self}) for p in path]
        return r

    def log_request(self, handler):
        if not isinstance(handler, NBIAPI):
            return
        status = handler.get_status()
        request = handler.request
        method = request.method
        uri = request.uri
        user = request.headers.get("Remote-User", "-")
        if user != "-":
            user = user.encode("quopri")
        remote_ip = request.remote_ip
        agent = request.headers.get("User-Agent", "-")
        referer = request.headers.get("Referer", "-")
        self.logger.info(
            '%s %s - "%s %s" HTTP/1.1 %s "%s" %s %.2fms',
            remote_ip,
            user,
            method,
            uri,
            status,
            referer,
            agent,
            1000.0 * request.request_time(),
        )
        metrics["api_requests", ("api", handler.name)] += 1


if __name__ == "__main__":
    NBIService().start()
