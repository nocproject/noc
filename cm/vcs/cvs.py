# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CVS support
# (http://www.nongnu.org/cvs/)
# Experimental, not-working
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import os
# NOC modules
import noc.cm.vcs


class VCS(noc.cm.vcs.VCS):
    name = "CVS"

    def check_repository(self):
        super(VCS, self).check_repository()
        if not os.path.exists(os.path.join(self.repo, "CVSROOT")):
            self.cmd("init", check=False)
