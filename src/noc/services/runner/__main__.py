# ----------------------------------------------------------------------
# runner service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.services.runner.service import RunnerService


if __name__ == "__main__":
    RunnerService().start()
