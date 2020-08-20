#!./bin/python
# ----------------------------------------------------------------------
# mib service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.tornado import TornadoService
from noc.services.mib.api.mib import MIBAPI


class MIBService(TornadoService):
    name = "mib"
    api = [MIBAPI]
    use_mongo = True


if __name__ == "__main__":
    MIBService().start()
