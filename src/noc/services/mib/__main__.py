# ----------------------------------------------------------------------
# MIB service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.mib.service import MIBService

if __name__ == "__main__":
    MIBService().start()
