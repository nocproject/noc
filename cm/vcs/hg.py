# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Mercurial support
## (http://www.selenic.com/mercurial/wiki/)
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.cm.vcs
import os,datetime

class VCS(noc.cm.vcs.VCS):
    name="hg"
    def check_repository(self):
        if not os.path.exists(os.path.join(self.repo,".hg")):
            self.cmd(["init"],check=False)
    def log(self,path):
        revs=[]
        for l in self.cmd_out(["log","--template","{rev} {date}\n",path]).split("\n"):
            l=l.strip()
            if not l:
                continue
            rev,date=l.split(" ")
            if "-" in date:
                date,r=date.split("-",1)
            revs+=[noc.cm.vcs.Revision(rev,datetime.datetime.fromtimestamp(float(date)))]
        return revs
    def diff(self,path,rev1,rev2):
        return self.cmd_out(["diff","-r%s:%s"%(rev1.revision,rev2.revision),path])
    def get_revision(self,path,rev):
        return self.cmd_out(["cat","-r%s"%rev.revision,path])
    def mv(self,f,t):
        self.cmd(["mv",f,t])
        self.commit(f,"mv")
        self.commit(t,"mv")
