# ----------------------------------------------------------------------
# MRT service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.mrt.service import MRTService


if __name__ == "__main__":
    MRTService().start()
