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
        self.request=""
        self.data=None
        self.path=None
        self.remote_address=None
    ##
    ## <!> STUB
    ##
    @classmethod
    def check_access(self,address):
        return True
    ##
    ##
    ##
    def on_read(self,data):
        if self.data is None:
            self.request+=data
            if "\r\n\r\n" in self.request:
                self.request,self.data=self.request.split("\r\n\r\n",1)
                headers=self.request.splitlines()
                method,self.path,proto=headers[0].split(" ")
                self.remote_address,port=self.socket.getpeername()
                self.info("HTTP %s '%s %s'"%(self.remote_address,method,self.path))
                getattr(self,"handle_%s"%method)(self.path)
    ##
    ##
    ##
    def handle_GET(self,path):
        try:
            context=self.server_hub.get_context("http",self.remote_address,self.path)
            self.send_response(200,"OK",context.get_url_data(path))
        except KeyError:
            self.send_response(404,"Not Found")
    ##
    ## <!> STUB
    ##
    @classmethod
    def check_access(self,address):
        return True
    
    def send_response(self,code,message,data="",content_type=""):
        self.info("HTTP %s: %d %s"%(self.remote_address,code,message))
        self.debug("HTTP DATA: "+repr(data))
        headers=["HTTP/1.1 %d %s"%(code,message),"Content-Length: %d"%len(data)]
        if content_type:
            headers+=["Content-Type: %s"%content_type]
        self.write("\r\n".join(headers)+"\r\n\r\n"+data)
        self.close(flush=True)

class HTTPServer(ListenTCPSocket):
    def __init__(self,factory,address,server_hub):
        super(HTTPServer,self).__init__(factory,address,80,HTTPServerSocket,server_hub=server_hub)
