##
## Version Control System Driver
##
from noc.setup.models import Settings
import os

# Registered VCSes
vcses={}
# Register vcs class
def register_vcs(name,vcs_class):
    vcses[name]=vcs_class

#
def get_vcs(repo):
    return vcses[Settings.get("cm.vcs_type")](repo)
    
##
## Abstract VCS class
##
class VCS(object):
    def __init__(self,repo):
        self.repo=repo
    # Check wrether repository exists and create when necessary
    def check_repository(self):
        pass
    # Add file to repository
    def add(self,path):
        self.cmd("add %s"%path)
    # Remove file from repository
    def rm(self,path):
        self.cmd("remove %s"%path)
        self.commit(path)
    # Commit single file
    def commit(self,path):
        self.cmd("commit -m 'CM autocommit' %s"%path)
    #
    def cmd(self,cmd,check=True):
        if check:
            self.check_repository()
        os.system("cd %s && %s %s"%(self.repo,Settings.get("cm.vcs_path"),cmd))
##
## Mercurial support
## (http://www.selenic.com/mercurial/wiki/)
##
class Hg(VCS):
    def check_repository(self):
        if not os.path.exists(os.path.join(self.repo,".hg")):
            self.cmd("init",check=False)
#
# Register VCSes
#
register_vcs("hg",Hg)