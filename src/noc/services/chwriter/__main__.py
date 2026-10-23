# ----------------------------------------------------------------------
# chwriter service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.chwriter.service import CHWriterService


if __name__ == "__main__":
    CHWriterService().start()
