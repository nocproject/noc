# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Version Control System support
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.registry import Registry
from lib.fileutils import copy_file
from noc.settings import config
import os,subprocess
##
## Registry for VCS
##
class VCSRegistry(Registry):
    name="VCSRegistry"
    subdir="vcs"
    classname="VCS"
    def get(self,repo):
        return self[config.get("cm","vcs_type")](repo)
vcs_registry=VCSRegistry()
##
##
##
class Revision(object):
    def __init__(self,revision,date):
        self.revision=revision
        self.date=date
    def __str__(self):
        return "%s (%s)"%(self.revision,self.date)
    def __repr__(self):
        return "<Revision %s (%s)>"%(self.revision,self.date)
        
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
    option_commit_message="-m"
    def __init__(self,repo):
        self.repo=repo
    # Check wrether repository exists and create when necessary
    def check_repository(self):
        pass
    # Add file to repository
    def add(self,path):
        self.cmd(["add",path])
    # Remove file from repository
    def rm(self,path):
        self.cmd(["remove",path])
        self.commit(path,"rm")
    # Move file to a new location
    # Dumb emulation
    def mv(self,f,t):
        copy_file(os.path.join(self.repo,f),os.path.join(self.repo,t))
        self.add(t)
        self.rm(f)
        self.commit(t,"mv emulation")
    # Commit single file
    def commit(self,path,message="CM autocommit"):
        self.cmd(["commit",self.option_commit_message,message,path])
    #
    # Execute VCS command.
    # cmd is a list of arguments
    def cmd(self,cmd,check=True):
        if check:
            self.check_repository()
        subprocess.check_call([config.get("cm","vcs_path")]+cmd,cwd=self.repo)
    # Returns an output of cmd
    def cmd_out(self,cmd,check=True):
        if check:
            self.check_repository()
        p=subprocess.Popen([config.get("cm","vcs_path")]+cmd,stdout=subprocess.PIPE,cwd=self.repo)
        d=p.stdout.read()
        return d
    # Returns a list of Revision
    def log(self,path):
        raise Exception("Not supported")
    # Returns unified diff
    def diff(self,path,rev1,rev2):
        raise Exception("Not supported")
    # Returns revision of the file
    def get_revision(self,path,revision):
        raise Exception("Not supported")
    #
    def in_repo(self,path):
        return os.path.exists(os.path.join(self.repo,path))
