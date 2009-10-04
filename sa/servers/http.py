# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Embedded HTTP Server
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.nbsocket import AcceptedTCPSocket, ListenTCPSocket
import urllib
##
## Servers
##
class HTTPServerSocket(AcceptedTCPSocket):
    def __init__(self,factory,socket,server_hub):
        super(HTTPServerSocket,self).__init__(factory,socket)
        self.server_hub=server_hub
        self.context=None
        self.request=""
        self.path=None
        self.host=""
        self.data_size=0
    ##
    ## <!> STUB
    ##
    @classmethod
    def check_access(self,address):
        return True
    ##
    def feed(self,data):
        self.data_size-=len(data)
        self.context.feed(data)
    ##
    ## Parse incoming data
    ##
    def on_read(self,data):
        if self.context is None:
            # Parse request
            self.request+=data
            for s in ["\n\n","\r\n\r\n"]:
                if s in self.request:
                    req,data=self.request.split(s,1)
                    l0,lo=req.split("\n",1)
                    self.debug(l0)
                    r=l0.split(" ")
                    if len(r)!=3 or r[0] not in ["PUT"]:
                        self.error("Invalid HTTP request")
                        self.close()
                        return
                    address,port=self.socket.getpeername()
                    self.path=urllib.unquote(r[1])
                    try:
                        self.context=self.server_hub.get_context("http",address,self.path)
                    except KeyError:
                        self.error("Permission denied: %s %s"%(address,self.path))
                        self.close()
                        return
                    for l in lo.split("\n"):
                        l=l.strip()
                        k,v=[x.strip() for x in l.split(":",1)]
                        k=k.lower()
                        if k=="content-length":
                            self.data_size=int(v)
                        elif k=="host":
                            self.host=v
                    break
        else:
            # Populate data
            self.feed(data)
            if self.data_size<=0:
                # Return response on all data received
                self.write("HTTP/1.1 201 Created\r\nContent-Length: 0\r\n\r\n")
                self.close()

class HTTPServer(ListenTCPSocket):
    def __init__(self,factory,address,server_hub):
        super(HTTPServer,self).__init__(factory,address,80,HTTPServerSocket,server_hub=server_hub)
