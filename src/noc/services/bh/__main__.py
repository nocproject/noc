# ----------------------------------------------------------------------
# BH service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.bh.service import BHService

if __name__ == "__main__":
    BHService().start()
