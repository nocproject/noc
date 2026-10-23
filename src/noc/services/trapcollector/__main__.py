# ----------------------------------------------------------------------
# Syslog Collector service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.trapcollector.service import TrapCollectorService


if __name__ == "__main__":
    TrapCollectorService().start()
