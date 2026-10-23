# ----------------------------------------------------------------------
# Ping service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.ping.service import PingService


if __name__ == "__main__":
    PingService().start()
