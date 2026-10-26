# ----------------------------------------------------------------------
# metrics service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.selfmon.service import SelfMonService

if __name__ == "__main__":
    SelfMonService().start()
