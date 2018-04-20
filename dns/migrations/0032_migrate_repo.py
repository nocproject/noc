# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Migrate mercurial repo to GridVCS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
=======
##----------------------------------------------------------------------
## Migrate mercurial repo to GridVCS
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


## Python modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import os
import subprocess


class Migration:
    SCRIPT = "scripts/migrate-repo"

    def forwards(self):
        if (os.path.isfile(self.SCRIPT) and
                os.access(self.SCRIPT, os.X_OK)):
            subprocess.check_call([self.SCRIPT, "dns"])

    def backwards(self):
<<<<<<< HEAD
        pass
=======
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
