# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.iLO2.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetConfig

EXCLUDE_TARGETS=set([
    "/map1/firmware1",
    "/map1/log1",
])

class Script(noc.sa.script.Script):
    name="HP.iLO2.get_config"
    implements=[IGetConfig]
    ##
    ##
    ##
    def walk(self,dir):
        r=self.cli("show %s"%dir).split("\n")
        if r[0]!="status=0" and r[1]!="status_tag=COMMAND COMPLETED":
            return []
        r=r[5:]
        
        state=None
        targets=[]
        properties=[]
        for l in r:
            l=l.strip()
            if l in ["Targets","Properties","Verbs"]:
                state=l
                continue
            if not l:
                continue
            if state=="Targets":
                targets+=[l]
            elif state=="Properties":
                properties+=[l]
        result=[(dir,[p.split("=",1) for p in properties if "=" in p])]
        for t in targets:
            path="%s/%s"%(dir,t)
            if path in EXCLUDE_TARGETS:
                continue
            result+=self.walk(path)
        return result
    
    def execute(self):
        r=[]
        for dir,args in self.walk("/map1"):
            if not args:
                continue
            r+=["set %s %s"%(dir," ".join(["%s=%s"%(k,v) for k,v in args]))]
        config="\n".join(sorted(r))
        return self.cleaned_config(config)
