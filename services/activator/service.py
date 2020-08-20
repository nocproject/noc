#!./bin/python
# ----------------------------------------------------------------------
# Activator service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.tornado import TornadoService
from noc.services.activator.api.activator import ActivatorAPI


class ActivatorService(TornadoService):
    name = "activator"
    pooled = True
    api = [ActivatorAPI]
    process_name = "noc-%(name).10s-%(pool).5s"
    use_telemetry = True

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    ActivatorService().start()
