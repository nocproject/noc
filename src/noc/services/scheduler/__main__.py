# ----------------------------------------------------------------------
# Scheduler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.scheduler.service import SchedulerService


if __name__ == "__main__":
    SchedulerService().start()
