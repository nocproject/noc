# ----------------------------------------------------------------------
# Activator service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.activator.service import ActivatorService

if __name__ == "__main__":
    ActivatorService().start()
