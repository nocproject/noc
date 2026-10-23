# ----------------------------------------------------------------------
# Escalator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.escalator.service import EscalatorService


if __name__ == "__main__":
    EscalatorService().start()
