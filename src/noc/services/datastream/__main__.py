# ----------------------------------------------------------------------
# datastream service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.datastream.service import DataStreamService


if __name__ == "__main__":
    DataStreamService().start()
