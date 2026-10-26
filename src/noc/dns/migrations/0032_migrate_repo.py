# ---------------------------------------------------------------------
# Migrate mercurial repo to GridVCS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import subprocess
import sys

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    SCRIPT = "scripts/migrate-repo"

    def migrate(self) -> None:
        if os.path.isfile(self.SCRIPT) and os.access(self.SCRIPT, os.X_OK):
            subprocess.check_call([sys.executable, self.SCRIPT, "dns"])
