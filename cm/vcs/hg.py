##
## Mercurial support
## (http://www.selenic.com/mercurial/wiki/)
##
import noc.cm.vcs
import os,datetime

class VCS(noc.cm.vcs.VCS):
    name="hg"
    def check_repository(self):
        if not os.path.exists(os.path.join(self.repo,".hg")):
            self.cmd("init",check=False)
    def log(self,path):
        revs=[]
        for l in self.cmd_out("log --template '{rev} {date}\n' %s"%path).split("\n"):
            l=l.strip()
            if not l:
                continue
            rev,date=l.split(" ")
            d,r=date.split("-",1)
            revs+=[noc.cm.vcs.Revision(rev,datetime.datetime.fromtimestamp(float(d)))]
        return revs
    def diff(self,path,rev1,rev2):
        return self.cmd_out("diff -r%s:%s %s"%(rev1.revision,rev2.revision,path))
    def get_revision(self,path,rev):
        return self.cmd_out("cat -r%s %s"%(rev.revision,path))