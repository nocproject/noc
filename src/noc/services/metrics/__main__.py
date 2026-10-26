# ----------------------------------------------------------------------
# Metrics service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.services.metrics.service import MetricsService

if __name__ == "__main__":
    MetricsService().start()
