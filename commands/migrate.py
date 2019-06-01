# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Pretty command
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2019 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.runner import MigrationRunner

if __name__ == "__main__":
    runner = MigrationRunner()
    runner.migrate()
