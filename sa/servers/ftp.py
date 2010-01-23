# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Embedded FTP Server
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.nbsocket import AcceptedTCPSocket, ListenTCPSocket
import os, socket, time
##
## Socket for data transfer
##
class FTPDataStreamSocket(AcceptedTCPSocket):
    def __init__(self,factory,socket,data_stream):
        self.data_stream=data_stream
        self.server_socket=self.data_stream.server_socket
        self.data=""
        self.fed_data=self.data_stream.fed_data
        super(FTPDataStreamSocket,self).__init__(factory,socket)
        if self.data_stream.fed_data:
            self.write(self.data_stream.fed_data)
    
    def on_connect(self):
        self.data_stream.on_stream_connect(self)
        self.t0=time.time()
    
    def on_read(self,data):
        self.data+=data
    
    def on_close(self):
        dt=time.time()-self.t0
        if dt>0 and self.data:
            l=len(self.data)
            self.debug("Transfer complete. %d bytes in %10.4f seconds. %10.2f bytes/sec"%(l,dt,float(l)/dt))
        self.server_socket.on_data_stream_close(self.data)
    
    def set_transfer_response(self,code,message):
        self.server_socket.send_response(code,message)

##
## Listener for passive mode data transfer
##
class FTPDataStream(ListenTCPSocket):
    def __init__(self,factory,server_socket):
        super(FTPDataStream,self).__init__(factory,server_socket.server_hub.ftp_server_address,0,FTPDataStreamSocket,data_stream=self)
        self.create_socket()
        self.server_socket=server_socket
        self.transfer_response=None
        self.fed_data=""
    ##
    ## Return listening port
    ##
    def get_port(self):
        return self.socket.getsockname()[1]
    ##
    def on_stream_connect(self,stream):
        self.close()
        self.server_socket.data_stream=stream
        if self.transfer_response:
            self.server_socket.send_response(self.transfer_response[0],self.transfer_response[1])
    ##
    def set_transfer_response(self,code,message):
        self.transfer_response=(code,message)
    ##
    def feed_data(self,data):
        self.fed_data+=data
##
## FTP Server
##
class FTPServerSocket(AcceptedTCPSocket):
    def __init__(self,factory,socket,server_hub):
        super(FTPServerSocket,self).__init__(factory,socket)
        self.server_hub=server_hub
        self.context=None
        self.request=""
        self.path=None
        self.host=""
        self.data_stream=None
        self.data_stream_callback=None
        self.context=None
        self.current_type="A"
        self.cwd="/"
    ##
    ## <!> STUB
    ##
    @classmethod
    def check_access(self,address):
        return True
    ##
    ## Send Response to client
    ##
    def send_response(self,code,message):
        self.write("%s %s\r\n"%(code,message))
    ##
    ## Create new data stream
    ##
    def create_data_stream(self):
        if self.data_stream:
            self.data_stream.close()
        self.data_stream=FTPDataStream(self.factory,self)
        self.data_stream_callback=None
    ##
    ##
    ##
    def set_data_stream_callback(self,cb):
        if self.data_stream:
            self.data_stream_callback=cb
    ##
    ## Feed collected data to context
    ##
    def feed(self,data):
        if self.context:
            self.context.feed(data)
    ##
    ## Send 220 response on connect
    ##
    def on_connect(self):
        self.send_response(220,"FTP Server Ready")
    ##
    ## Process incoming data
    ##
    def on_read(self,data):
        self.request+=data
        if "\r\n" in self.request:
            cmd,self.request=self.request.split("\r\n",1)
            if " " in cmd:
                cmd,args=cmd.split(" ",1)
            else:
                args=""
            self.debug("Incoming command: %s (%s)"%(cmd,args))
            if cmd=="USER":
                self.send_response(331,"Password required for %s"%args)
            elif cmd=="PASS":
                self.send_response(230,"User logged in")
            elif cmd=="SYST":
                self.send_response(215,"UNIX Type %s"%os.uname()[0])
            elif cmd=="QUIT":
                self.close()
            elif cmd=="PWD":
                self.send_response(257,"'%s' is the current directory"%self.cwd)
            elif cmd=="PASV":
                self.create_data_stream()
                p=self.data_stream.get_port()
                port=(self.server_hub.ftp_server_address+"."+str(p/256)+"."+str(p%256)).replace(".",",")
                self.send_response(227,"Entering Passive Mode (%s)"%port)
            elif cmd=="EPSV":
                self.create_data_stream()
                self.send_response(229,"Entering extended passive mode (|||%d|)"%self.data_stream.get_port())
            elif cmd=="STOR":
                address,port=self.socket.getpeername()
                path=os.path.join(self.cwd,args.replace("//","/"))
                try:
                    self.context=self.server_hub.get_context("ftp",address,path)
                except KeyError:
                    self.error("Permission denied: %s %s"%(address,path))
                    self.send_response(554,"Permission denied")
                    return
                self.data_stream.set_transfer_response(150,"File OK. Ready to receive")
                self.set_data_stream_callback(self.ds_stor)
            elif cmd=="RETR":
                address,port=self.socket.getpeername()
                path=os.path.join(self.cwd,args.replace("//","/"))
                if not self.has_data(path):
                    self.error("Permission denied: %s %s"%(address,path))
                    self.send_response(554,"Permission denied")
                    return
                self.data_stream.feed_data(self.get_url_data(path))
                self.data_stream.set_transfer_response(150,"File OK. Ready to transmit")
                self.set_data_stream_callback(self.ds_send_226)
            elif cmd=="TYPE":
                if args in ["A","L7"]:
                    self.current_type="A"
                    self.send_response(200,"Type set to %s"%args)
                elif args in ["I","L8"]:
                    self.current_type="I"
                    self.send_response(200,"Type set to %s"%args)
                else:
                    self.send_response(504,"Unsupported type %s"%args)
            elif cmd=="CWD":
                self.cwd=os.path.join(self.cwd,args)
                self.send_response(250,"'%s' is the current directory"%self.cwd)
            else:
                self.send_response(502,"Command %s is not implemented"%cmd)
    ##
    ## Close data stream if open
    ##
    def on_close(self):
        if self.data_stream:
            self.data_stream.close()
        super(FTPServerSocket,self).on_close()
    ##
    ## Called on data stream close
    ##
    def on_data_stream_close(self,data):
        self.debug("Closing data stream")
        if self.data_stream_callback:
            self.data_stream_callback(data)
        self.data_stream=None
        self.data_stream_callback=None
    ##
    ## Send 226 Transfer Complete
    ##
    def ds_send_226(self,data):
        self.send_response(226,"Transfer Complete")
    ##
    def ds_stor(self,data):
        self.send_response(226,"Transfer Complete")
        if self.context:
            self.context.feed(data)
##
## FTP Server listener
##
class FTPServer(ListenTCPSocket):
    def __init__(self,factory,address,server_hub):
        super(FTPServer,self).__init__(factory,address,21,FTPServerSocket,server_hub=server_hub)
