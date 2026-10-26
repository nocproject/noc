# ----------------------------------------------------------------------
# metricscollector service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.metricscollector.service import MetricsCollectorService

if __name__ == "__main__":
    MetricsCollectorService().start()
