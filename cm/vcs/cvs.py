##
## CVS support
## (http://www.nongnu.org/cvs/)
## Experimental, not-working
##
import noc.cm.vcs
import os
from noc.setup.models import Settings

class VCS(noc.cm.vcs.VCS):
    name="CVS"
    def check_repository(self):
        if not os.path.exists(os.path.join(self.repo,"CVSROOT")):
            self.cmd("init",check=False)
    def cmd(self,cmd,check=True):
        if check:
            self.check_repository()
        os.system("cd %s && %s -d %s %s"%(self.repo,Settings.get("cm.vcs_path"),self.repo,cmd))