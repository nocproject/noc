# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Simple RIPE whois client
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import logging, socket
from noc.lib.nbsocket import ConnectedTCPSocket
from noc.lib.validators import is_fqdn

WHOIS_SERVER="whois.ripe.net"
WHOIS_PORT=43

class Whois(ConnectedTCPSocket):
    def __init__(self,factory,query,callback=None,fields=None):
        # Find suitable whois server
        if is_fqdn(query):
            # Use TLD.whois-servers.net for domain lookup
            tld=query.split(".")[-1]
            server="%s.whois-servers.net"%tld
        else:
            server=WHOIS_SERVER
        # Try to resolve server
        try:
            server=socket.gethostbyname(server)
        except:
            logging.error("Cannot resolve host %s"%server)
            return
        ConnectedTCPSocket.__init__(self,factory,server,WHOIS_PORT)
        self.query=query.strip()
        self.output=[]
        self.callback=callback
        self.fields=set(fields) if fields else None
        logging.debug("whois(%s)"%self.query)
        
    def on_connect(self):
        self.write(self.query+"\r\n")
    
    def on_read(self,data):
        self.output+=[data]
    
    def on_close(self):
        if self.callback:
            self.callback(self.format())
            
    def format(self):
        out=[]
        last=None
        for l in "".join(self.output).split("\n"):
            l=l.strip()
            if not l or l.startswith("%"):
                continue
            L=l.split(":")
            if len(L)!=2:
                L=[last,L[0]]
            else:
                last=L[0]
            if self.fields is None or L[0] in self.fields:
                out.append([L[0],L[1].strip()])
        return out
##
## Simple whois client function for testing
##
def whois(q,fields=None):
    from noc.lib.nbsocket import SocketFactory
    f=SocketFactory()
    s=[]
    # Find suitable whois server
    w=Whois(f,q,s.append,fields)
    f.run()
    return s[0]
