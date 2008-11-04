from noc.sa.actions import BaseAction
import logging,httplib,cStringIO

class Action(BaseAction):
    ARGS=["user","password","address","post_path"]
    def prepare_action(self):
        self.set_fsm([
            ("^HTTP/1.[01] 200 .+?\n",self.s_200),
            ("^HTTP/1.[01] \d{3}","FAILURE"),
        ])
        if self.args["post_path"]:
            self.http_post(self.args["post_path"])
    
    #
    def http_get(self,path,query=None):
        pass
        
    def http_post(self,path,query=None):
        self.stream.write("POST %s HTTP/1.1\r\nHost: %s\r\n\Connection: close\r\n\r\n"%(self.args["post_path"],self.args["address"]))
    
    # OK
    def s_200(self,match):
        return [(".+",self.s_grab)]
        
    def s_grab(self,match):
        self.status=True
        self.result+=match.group(0)
        return [(".+",self.s_grab)]
        
    def close(self,status):
        # Process HTTP Response
        m=httplib.HTTPMessage(cStringIO.StringIO(self.result))
        self.result=self.result[m.startofbody:]
        super(Action,self).close(self.status)
