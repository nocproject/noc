from noc.sa.actions import BaseAction
import logging,httplib,cStringIO,base64,hashlib,random

class Action(BaseAction):
    ARGS=["user","password","address"]
    def prepare_action(self):
        self.set_fsm([
            ("^HTTP/1.[01] 200 .+?\r\n(.+?\r\n\r\n)",self.s_200),
            ("^HTTP/1.[01] 401 .+?\r\n(.+?\r\n\r\n)",self.s_401),
            ("^HTTP/1.[01] \d{3}","FAILURE"),
        ])
        self.in_reconnect=False
        self.http_request(self.profile.method_pull_config,self.profile.path_pull_config)
        
    def reconnect(self):
        self.in_reconnect=True
        self.stream=self.stream.__class__(self.stream.access_profile)
        self.stream.attach_action(self)
    #
    def http_request(self,method,path,headers={}):
        self.last_request=(method,path,headers)
        s="%s %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n"%(method,path,self.args["address"])
        s+="".join(["%s: %s\r\n"%(k,v) for k,v in headers.items()])
        s+="\r\n"
        logging.debug("HTTP Request:\n%s"%s)
        self.stream.write(s)
    
    # 401, Unauthorized
    def s_401(self,match):
        m=httplib.HTTPMessage(cStringIO.StringIO(match.group(1)))
        auth=m.get("WWW-Authenticate")
        scheme,data=m.get("WWW-Authenticate").split(" ",1)
        scheme=scheme.lower()
        d={}
        for s in data.split(","):
            s=s.strip()
            if "=" in s:
                k,v=s.split("=",1)
                if v.startswith("\"") and v.endswith("\""):
                    v=v[1:-1]
                d[k]=v
            else:
                d[s]=None
        method,path,headers=self.last_request
        if scheme=="basic":
            headers["Authorization"]="Basic %s"%base64.b64encode("%s:%s"%(self.args["user"],self.args["password"])).strip()
        elif scheme=="digest":
            H = lambda x: hashlib.md5(x).hexdigest()
            KD= lambda x,y: H("%s:%s"%(x,y))
            A1="%s:%s:%s"%(self.args["user"],d["realm"],self.args["password"])
            A2="%s:%s"%(method,path)
            f={
                "username": self.args["user"],
                "realm"   : d["realm"],
                "nonce"   : d["nonce"],
                "uri"     : path,
            }
            if "qop" not in d:
                noncebit="%s:%s"%(d["nonce"],H(A2))
            elif d["qop"]=="auth":
                nc="00000001"
                cnonce=H(str(random.random()))
                f["nc"]=nc
                f["cnonce"]=cnonce
                f["qop"]=d["qop"]
                noncebit="%s:%s:%s:%s:%s"%(d["nonce"],nc,cnonce,d["qop"],H(A2))
            else:
                raise Exception("qop not supported: %s"%d["qop"])
            f["response"]=KD(H(A1),noncebit)
            headers["Authorization"]="Digest "+", ".join(["%s=\"%s\""%(k,v) for k,v in f.items()])
        else:
            raise Exception("Unknown auth method: %s"%scheme)
        self.reconnect()
        self.http_request(method,path,headers)
        return [
            ("^HTTP/1.[01] 200 .+?\n",self.s_200),
            ("^HTTP/1.[01] \d{3}","FAILURE"),
        ]
    
    # OK
    def s_200(self,match):
        return [(".+",self.s_grab)]
        
    def s_grab(self,match):
        self.status=True
        self.result+=match.group(0)
        return [(".+",self.s_grab)]
        
    def close(self,status):
        if self.in_reconnect:
            self.in_reconnect=False
            return
        # Process HTTP Response
        m=httplib.HTTPMessage(cStringIO.StringIO(self.result))
        self.result=self.result[m.startofbody:]
        if m["Transfer-Encoding"].lower()=="chunked":
            # Unchunk
            buffer=self.result
            result=[]
            while buffer:
                idx=buffer.find("\r\n")
                l=int(buffer[:idx],16)
                if l==0:
                    break
                result+=[buffer[idx+2:l+idx+2]]
                buffer=buffer[idx+4+l:]
            self.result="".join(result)
        super(Action,self).close(self.status)
