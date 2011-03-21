# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HTTP provider
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random
import urllib
import httplib
import base64
import hashlib

##
## HTTP Provider
##
class HTTPProvider(object):
    def __init__(self,access_profile):
        self.access_profile=access_profile
        self.authorization=None
    
    def request(self, method, path, params=None, headers={}):
        if self.authorization:
            headers["Authorization"]=self.authorization
        conn=httplib.HTTPConnection(self.access_profile.address)
        conn.request(method,path,params,headers)
        response=conn.getresponse()
        try:
            if response.status==200:
                return response.read()
            elif response.status==401 and self.authorization is None:
                self.set_authorization(response.getheader("www-authenticate"),method,path)
                return self.request(method,path,params,headers)
            else:
                raise Exception("HTTP Error: %s"%response.status)
        finally:
            conn.close()
            
    def set_authorization(self, auth, method, path):
        scheme,data=auth.split(" ",1)
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
        if scheme=="basic":
            self.authorization="Basic %s"%base64.b64encode("%s:%s"%(self.access_profile.user,self.access_profile.password)).strip()
        elif scheme=="digest":
            H = lambda x: hashlib.md5(x).hexdigest()
            KD= lambda x,y: H("%s:%s"%(x,y))
            A1="%s:%s:%s"%(self.access_profile.user,d["realm"],self.access_profile.password)
            A2="%s:%s"%(method,path)
            f={
                "username": self.access_profile.user,
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
            self.authorization="Digest "+", ".join(["%s=\"%s\""%(k,v) for k,v in f.items()])
        else:
            raise Exception("Unknown auth method: %s"%scheme)
    
    def get(self, path, params=None, headers={}):
        return self.request("GET",path)
    
    def post(self, path, params=None, headers={}):
        if params:
            params=urllib.urlencode(params)
            headers["Content-Type"]="application/x-www-form-urlencoded"
        return self.request("POST",path,params,headers)
    
