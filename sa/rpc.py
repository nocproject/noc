# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SAE RPC Protocol
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.protocols.sae_pb2 import Message,Error
import struct,logging,random,time,hashlib,zlib
from google.protobuf.service import RpcController
from noc.sa.protocols.sae_pb2 import *
from noc.lib.nbsocket import Protocol
from noc.lib.debug import error_report

##
## RPC Controller
##
class Controller(RpcController):
    def __init__(self,stream):
        RpcController.__init__(self)
        self.stream=stream
        self.transaction=None
    def Reset(self):
        pass
    def Failed(self):
        pass
    def ErrorText(self):
        pass
    def StartCancel(self):
        pass
    def SetFailed(self, reason):
        pass
    def IsCancelled(self):
        pass
    def NotifyOnCancel(self,callback):
        pass

##
## Transaction structure
##
class Transaction(object):
    def __init__(self,factory,id,method=None,callback=None):
        logging.debug("Creating transaction id=%s method=%s callback=%s"%(id,method,callback))
        self.factory=factory
        self.id=id
        self.method=method
        self.callback=callback
        
    def commit(self,response=None,error=None):
        if self.callback:
            self.callback(self,response,error)
        self.factory.delete_transaction(self.id)
        
    def rollback(self):
        self.factory.delete_transaction(self.id)
##
## Transaction storage
##
class TransactionFactory(object):
    def __init__(self):
        self.transactions={}
        
    def __len__(self):
        return len(self.transactions)
        
    # Generate unique id
    def __get_id(self):
        while True:
            id=random.randint(0,0x7FFFFFFF)
            if id not in self.transactions:
                return id

    def has_key(self,id):
        return id in self.transactions
        
    def __getitem__(self,id):
        return self.transactions[id]
        
    # Begins transaction, remembers callback and returns transaction id
    def begin(self,id=None,method=None,callback=None):
        if id:
            if id in self.transactions:
                raise Exception("Transaction is already exists")
        else:
            id=self.__get_id()
        t=Transaction(self,id,method,callback)
        self.transactions[id]=t
        return t
        
    def delete_transaction(self,id):
        del self.transactions[id]
##
## Stream is a <len><data><len><data>..... sequence
## Where len is an 32 bit integer in network order
##
class Int32Protocol(Protocol):
    def parse_pdu(self):
        r=[]
        while len(self.in_buffer)>=4:
            l=struct.unpack("!L",self.in_buffer[:4])[0]
            if len(self.in_buffer)>=4+l:
                r+=[self.in_buffer[4:4+l]]
                self.in_buffer=self.in_buffer[4+l:]
            else:
                break
        return r
##
##
##
class CompressedInt32Protocol(Protocol):
    def parse_pdu(self):
        r=[]
        while len(self.in_buffer)>=4:
            l=struct.unpack("!L",self.in_buffer[:4])[0]
            if len(self.in_buffer)>=4+l:
                try:
                    pdu=zlib.decompress(self.in_buffer[4:4+l])
                    r+=[pdu]
                except:
                    logging.error("Failed to decompress PDU")
                self.in_buffer=self.in_buffer[4+l:]
            else:
                break
        return r
##
##
##
class RPCSocket(object):
    protocol_class=CompressedInt32Protocol
    def __init__(self,service):
        self.service=service
        self.proxy=Proxy(self,SAEService_Stub)
        self.transactions=TransactionFactory()
        self.stat_rpc_requests=0
        self.stat_rpc_responses=0
        self.stat_rpc_errors=0
        
    def on_read(self,data):
        logging.debug("on_read: %s"%repr(data))
        msg=Message()
        msg.ParseFromString(data)
        logging.debug("rpc_handle_message:\n%s"%msg)
        if msg.error.ByteSize():
            self.stat_rpc_errors+=1
            self.rpc_handle_error(msg.id,msg.error)
        elif msg.request.ByteSize():
            self.stat_rpc_requests+=1
            self.rpc_handle_request(msg.id,msg.request)
        elif msg.response.ByteSize():
            self.stat_rpc_responses+=1
            self.rpc_handle_response(msg.id,msg.response)
            
    def rpc_handle_request(self,id,request):
        logging.debug("rpc_handle_request")
        if self.transactions.has_key(id):
            self.send_error(id,ERR_TRANSACTION_EXISTS,"Transaction %s is alreasy exists"%id)
            return
        method=self.service.GetDescriptor().FindMethodByName(request.method)
        if method:
            req=self.service.GetRequestClass(method)()
            req.ParseFromString(request.serialized_request)
            logging.debug("Request accepted:\nid: %s\n%s"%(id,str(req)))
            controller=Controller(self)
            controller.transaction=self.transactions.begin(id=id,method=request.method)
            try:
                self.service.CallMethod(method,controller,req,self.send_response)
            except:
                self.send_error(id,ERR_INTERNAL,"RPC Call to %s failed"%request.method)
                error_report()
        else:
            self.send_error(id,ERR_INVALID_METHOD,"invalid method '%s'"%request.method)
        
    def rpc_handle_response(self,id,response):
        logging.debug("rpc_handle_response:\nid: %s\n%s"%(id,str(response)))
        if not self.transactions.has_key(id):
            logging.error("Invalid transaction: %s"%id)
            return
        t=self.transactions[id]
        method=self.service.GetDescriptor().FindMethodByName(t.method)
        if method:
            res=self.service.GetResponseClass(method)()
            res.ParseFromString(response.serialized_response)
            t.commit(response=res)
        else:
            logging.error("Invalid method: %s"%t.method)
            t.rollback()
    
    def rpc_handle_error(self,id,error):
        logging.debug("rpc_handle_error:\nid: %s\n%s"%(id,str(error)))
        if not self.transactions.has_key(id):
            logging.error("Invalid transaction: %s"%id)
            return
        self.transactions[id].commit(id,error=error)
        
    # Format and write SAE RPC PDU
    def write_message(self,msg):
        s=zlib.compress(msg.SerializeToString())
        self.write(struct.pack("!L",len(s))+s)
        
    def send_request(self,id,method,request):
        logging.debug("send_request\nmethod: %s\n%s"%(method,str(request)))
        m=Message()
        m.id=id
        m.request.method=method
        m.request.serialized_request=request.SerializeToString()
        self.write_message(m)
        return id
        
    def send_response(self,controller,response=None,error=None):
        id=controller.transaction.id
        logging.debug("send_response:\nid: %d\nresponse:\n%s\nerror:\n%s"%(id,str(response),str(error)))
        if not self.transactions.has_key(id):
            raise Exception("Invalid transaction")
        m=Message()
        m.id=id
        if error:
            m.error.code=error.code
            m.error.text=error.text
        if response:
            m.response.serialized_response=response.SerializeToString()
        self.write_message(m)
        controller.transaction.commit()
        
    def send_error(self,id,code,text):
        logging.debug("send_error:\nid: %s\ncode: %s\ntext: %s"%(id,code,text))
        m=Message()
        m.id=id
        m.error.code=code
        m.error.text=text
        self.write_message(m)
        
    def call(self,method,request,callback):
        t=self.transactions.begin(method=method,callback=callback)
        self.send_request(t.id,method,request)
        return t
        
    def _stats(self):
        return [
            ("rpc.requests",  self.stat_rpc_requests),
            ("rpc.responses", self.stat_rpc_responses),
            ("rpc.errors",    self.stat_rpc_errors),
        ]
    stats=property(_stats)
##
## Proxy class for RPC interface
##
class Proxy(object):
    def __init__(self,stream,stub_class):
        self.stream=stream
        self.stub=stub_class(stream.service)
    def __getattr__(self,name):
        return lambda request,callback: self.stream.call(name,request,callback)
##
## file hash for software update services
##
def file_hash(path):
    f=open(path)
    data=f.read()
    f.close()
    return hashlib.sha1(data).hexdigest()
##
## Generic hash for digest authetications
##
def H(s):
    return hashlib.sha1(s).hexdigest()

##
## Generate random nonce for digest authetuication
##
def get_nonce():
    ur=random.SystemRandom()
    return H(H(str(ur.random())[2:])+str(ur.random())[2:])

##
## Compute digest for Activator authentications
##
def get_digest(name,password,nonce):
    return H(H(name+":"+password)+":"+nonce)
    
