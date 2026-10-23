# ----------------------------------------------------------------------
# noc-correlator daemon
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.correlator.service import CorrelatorService


if __name__ == "__main__":
    CorrelatorService().start()
