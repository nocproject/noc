#!./bin/python
# ----------------------------------------------------------------------
# nbi service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import Request

# NOC modules
from noc.core.service.fastapi import FastAPIService
from noc.config import config
from noc.core.perf import metrics

PREFIX_NBI = "/api/nbi/"


class NBIService(FastAPIService):
    name = "nbi"
    use_mongo = True
    if config.features.traefik:
        traefik_backend = "nbi"
        traefik_frontend_rule = "PathPrefix:/api/nbi"

    async def init_api(self):
        await super().init_api()

        @self.app.middleware("http")
        async def update_metrics(request: Request, call_next):
            def to_suppress_writing_metrics():
                return path in ("/health/", "/health", "/metrics", "/mon/", "/mon")

            response = await call_next(request)
            path = request.scope["path"]
            if not to_suppress_writing_metrics():
                api_name = path.split(PREFIX_NBI)[1].split("/")[0]
                metrics["api_requests", ("api", api_name)] += 1
            return response


if __name__ == "__main__":
    NBIService().start()
