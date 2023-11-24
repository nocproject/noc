# ----------------------------------------------------------------------
# set bi_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import subprocess
from pathlib import Path

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if not os.path.exists(Path("fixes", "fix_bi_id")):
            return
        subprocess.check_call(["./noc", "fix", "apply", "fix_bi_id"])
