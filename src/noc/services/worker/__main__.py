# ----------------------------------------------------------------------
# worker service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.worker.service import WorkerService


if __name__ == "__main__":
    WorkerService().start()
