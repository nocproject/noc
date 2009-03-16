# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.registry import Registry
##
##
##
class GeneratorRegistry(Registry):
    name="GeneratorRegistry"
    subdir="generators"
    classname="Generator"
    apps=["noc.dns"]
generator_registry=GeneratorRegistry()
##
## Metaclass for Generator
##
class GeneratorBase(type):
    def __new__(cls,name,bases,attrs):
        g=type.__new__(cls,name,bases,attrs)
        generator_registry.register(g.name,g)
        return g

##
## Abstract DNS zone generator
##
class Generator(object):
    __metaclass__=GeneratorBase
    name=None
    def get_header(self):
        return """;;
;; WARNING: Auto-generated zone file
;; Do not edit manually
;;
"""
    def get_footer(self):
        return """
;;
;; End of auto-generated zone
;;
"""
    def get_soa(self):
        raise Exception,"SOA Not implemented"
    
    def get_records(self):
        raise Exception,"Records Not implemented"
        
    def get_zone(self,zone):
        self.zone=zone
        s=""
        s+=self.get_header()
        s+=self.get_soa()
        s+=self.get_records()
        s+=self.get_footer()
        return s
        
    def get_include(self,ns):
        raise Exception,"Include file is not implemented"
        
    def format_3_columns(self,records):
        maxlen_1=10
        maxlen_2=3
        records=[r for r in records if len(r)==3]
        for a,b,c in records:
            l=len(a)
            if l>maxlen_1:
                maxlen_1=l
            l=len(b)
            if l>maxlen_2:
                maxlen_2=l
        mask="%%-%ds   %%-%ds   %%s"%(maxlen_1,maxlen_2)
        return "\n".join([mask%tuple(r) for r in records if len(r)==3])
    
    def pretty_time(self,t):
        if t==0:
            return "zero"
        T=["week","day","hour","min","sec"]
        W=[345600,86400,3600,60,1]
        r=[]
        for w in W:
            rr=int(t/w)
            t-=rr*w
            r.append(rr)
        z=[]
        for rr,t in zip(r,T):
            if rr>1:
                z.append("%d %ss"%(rr,t))
            elif rr>0:
                z.append("%d %s"%(rr,t))
        return " ".join(z)
