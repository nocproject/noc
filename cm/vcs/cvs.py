# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CVS support
## (http://www.nongnu.org/cvs/)
## Experimental, not-working
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.cm.vcs
import os

class VCS(noc.cm.vcs.VCS):
    name="CVS"
    def check_repository(self):
        if not os.path.exists(os.path.join(self.repo,"CVSROOT")):
            self.cmd("init",check=False)
