# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Pretty command
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2019 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.core.management import call_command
# NOC modules
from noc.core.migration.runner import MigrationRunner

if __name__ == "__main__":
    call_command("syncdb", interactive=False,
                 load_initial_data=False)
    runner = MigrationRunner()
    runner.migrate()
