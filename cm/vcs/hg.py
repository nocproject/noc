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
        super(VCS, self).check_repository()
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
        
    def get_current_revision(self,path):
        l=self.cmd_out(["log","-l","1","--template","{rev} {date}",path])
        if not l:
            return None
        rev,date=l.split(" ")
        if "-" in date:
            date,r=date.split("-",1)
        return noc.cm.vcs.Revision(rev,datetime.datetime.fromtimestamp(float(date)))
        
    def diff(self,path,rev1,rev2):
        return self.cmd_out(["diff","-r%s:%s"%(rev1.revision,rev2.revision),path])
    def get_revision(self,path,rev=None):
        args=["cat"]
        if rev is not None:
            args+=["-r%s"%rev.revision]
        args+=[path]
        return self.cmd_out(args)
    def mv(self,f,t):
        self.cmd(["mv",f,t])
        self.commit(f,"mv")
        self.commit(t,"mv")
    def annotate(self,path):
        revs={} # id -> revision
        data=[]
        for l in self.cmd_out(["annotate",path]).splitlines():
            r,t=l.split(": ",1)
            r=r.strip()
            try:
                r=revs[r]
            except KeyError:
                # Find revision info
                date=self.cmd_out(["log","--template","{date}","-r",r]).strip()
                if "-" in date:
                    date,x=date.split("-",1)
                rev=noc.cm.vcs.Revision(r,datetime.datetime.fromtimestamp(float(date)))
                revs[r]=rev
                r=rev
            data+=[(r,t)]
        return data
                