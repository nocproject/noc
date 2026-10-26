# ----------------------------------------------------------------------
# Syslog Collector service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.syslogcollector.service import SyslogCollectorService

if __name__ == "__main__":
    SyslogCollectorService().start()
