# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Migrate mercurial repo to GridVCS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import sys
import os
import subprocess


class Migration:
    SCRIPT = "scripts/migrate-repo"

    def forwards(self):
        if (os.path.isfile(self.SCRIPT) and
                os.access(self.SCRIPT, os.X_OK)):
            subprocess.check_call([sys.executable, self.SCRIPT, "dns"])

    def backwards(self):
        pass
