# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator's embedded servers
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import logging, random, urllib
##
##
##
class ServerContextManager(object):
    def __init__(self,server_hub,context_name):
        self.server_hub=server_hub
        self.context_name=context_name
        self.address=None
        self.path=None
        self.data=[]
    ##
    ## Set request filter
    ##
    def prepare(self,address,path=None):
        self.address=address
        if path:
            self.path=None
        else:
            self.path="/%s-%s-%d"%(str(id(self)),address,random.randint(0,0x7FFFFFFF))
        return self.path
    ##
    ##
    ##
    def get_url(self,address,path=None):
        path=self.prepare(address,path)
        return "%s://%s%s"%(self.context_name,getattr(self.server_hub,"%s_server_address"%self.context_name),urllib.quote(path))
    ##
    ## Pupulate data
    ##
    def feed(self,data):
        self.data+=[data]
    ##
    ## Return collected data
    ##
    def get_data(self):
        return "".join(self.data)
    ##
    ## Register server context
    ##
    def __enter__(self):
        self.server_hub.register_context(self.context_name,self)
        return self
    ##
    ## Unregister server context
    ##
    def __exit__(self,exc_type, exc_val, exc_tb):
        self.server_hub.unregister_context(self.context_name,self)

##
## Server hub
##
class ServersHub(object):
    def __init__(self,activator):
        self.activator=activator
        self.contexts={
            "http" : set(),
            "ftp"  : set(),
        }
        # Auto-load servers
        for context_name in self.contexts:
            l=self.activator.config.get("servers","listen_%s"%context_name)
            setattr(self,"%s_server_address"%context_name,l)
            if l:
                m=__import__("noc.sa.servers.%s"%context_name,{},{},"*")
                setattr(self,"%s_server"%context_name,
                    getattr(m,"%sServer"%context_name.upper())(self.activator.factory,l,self))
            else:
                setattr(self,"%s_server"%context_name,None)
    ##
    ## Register new context
    ##
    def register_context(self,context_name,context):
        logging.debug("Register %s server context: %s"%(context_name,context))
        self.contexts[context_name].add(context)
    ##
    ## Unregister context
    ##
    def unregister_context(self,context_name,context):
        logging.debug("Unregister %s server context: %s"%(context_name,context))
        self.contexts[context_name].remove(context)
    ##
    ##
    ##
    def get_context(self,context_name,address,path):
        for c in self.contexts[context_name]:
            if c.address==address and c.path==path:
                return c
        raise KeyError

    ##
    ## Check IP address has access to context
    ##
    def check_address_access(self,context_name,address):
        return len([c for c in self.contexts[context_name] if c.address==address])>0
    ##
    ## Check IP address has access to path
    ##
    def check_path_access(self,context_name,address,path):
        return len([c for c in self.contexts[context_name] if c.address==address and c.path==path])>0
    ##
    ## Close all servers
    ##
    def close(self):
        for context_name in self.contexts:
            s=getattr(self,"%s_server"%context_name)
            if s:
                s.close()
    ##
    ## Return HTTP Server Context Manager
    ##
    def http(self):
        return ServerContextManager(self,"http")
    ##
    ## Return FTP Server context manager
    ##
    def ftp(self):
        return ServerContextManager(self,"ftp")
