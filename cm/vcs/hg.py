##
## Mercurial support
## (http://www.selenic.com/mercurial/wiki/)
##
import noc.cm.vcs
class VCS(noc.cm.vcs.VCS):
    name="hg"
    def check_repository(self):
        if not os.path.exists(os.path.join(self.repo,".hg")):
            self.cmd("init",check=False)