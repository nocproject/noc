##
## Version Control System support
##
from noc.lib.registry import Registry
from noc.setup.models import Settings
import os
##
## Registry for VCS
##
class VCSRegistry(Registry):
    name="VCSRegistry"
    subdir="vcs"
    classname="VCS"
    def get(self,repo):
        return self[Settings.get("cm.vcs_type")](repo)
vcs_registry=VCSRegistry()
##
## VCS Metaclass
##
class VCSBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        vcs_registry.register(m.name,m)
        return m
##
## VCS Base Class
##
class VCS(object):
    __metaclass__=VCSBase
    name=None
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