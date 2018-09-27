#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import Service
from noc.config import config
from noc.services.nbi.loader import loader
from noc.core.perf import metrics
from noc.services.nbi.base import NBIAPI


class NBIService(Service):
    name = "nbi"
    if config.features.traefik:
        traefik_backend = "nbi"
        traefik_frontend_rule = "PathPrefix:/api/nbi"

    def get_api(self):
        r = []
        for api in loader.iter_apis():
            handler = loader.get_api(api)
            if handler:
                self.logger.info("[%s] Initializing API", api)
                r += [handler]
            else:
                self.logger.info("[%s] Failed to initialize API", api)
        return r

    def get_handlers(self):
        return [
            (
                "/api/nbi/%s" % api.name, api, {"service": self}
            ) for api in self.get_api()
        ]

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
            "%s %s - \"%s %s\" HTTP/1.1 %s \"%s\" %s %.2fms",
            remote_ip, user, method, uri, status,
            referer, agent,
            1000.0 * request.request_time()
        )
        metrics["api_requests", ("api", handler.name)] += 1


if __name__ == "__main__":
    NBIService().start()
