##
## SAE-activator protocol stream
##
from noc.sa.protocols.sae_pb2 import Message,Error
import struct,logging,asyncore,socket,random,time

KEEPALIVE_INTERVAL=60

class SAEStream(asyncore.dispatcher):
    def __init__(self,parent,sock=None,address=None):
        asyncore.dispatcher.__init__(self)
        self.parent=parent
        self.in_message_len=None
        self.in_buffer=""
        self.out_buffer=""
        self.last_in=time.time()
        self.last_out=time.time()
        
    def connect_sae(self,address,port):
        logging.debug("Connecting to SAE at %s:%d"%(address,port))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((address,port))
        
    def connect_activator(self,socket):
        logging.debug("Attaching SAEStream to socket")
        self.set_socket(socket)
        
    def handle_connect(self):
        logging.debug("SAEStream connect")
        self.last_in=time.time()
        self.last_out=time.time()
    
    def handle_close(self):
        logging.debug("SAEStream close")
        self.parent.on_stream_close(self)
        
    def handle_read(self):
        self.last_in=time.time()
        try:
            d=self.recv(8192)
        except socket.error:
            self.close()
            return
        if d=="":
            self.close()
            return
        logging.debug("Recv: %s"%repr(d))
        self.in_buffer+=d
        while self.in_buffer:
            if self.in_message_len is None and len(self.in_buffer)>=4:
                self.in_message_len,=struct.unpack("!L",self.in_buffer[:4])
                self.in_buffer=self.in_buffer[4:]
            if self.in_message_len:
                if len(self.in_buffer)<self.in_message_len:
                    break
                msg=Message()
                msg.ParseFromString(self.in_buffer[:self.in_message_len])
                self.in_buffer=self.in_buffer[self.in_message_len:]
                self.in_message_len=None
                self.on_new_message(msg)
            else:
                break

    def writable(self):
        return len(self.out_buffer)>0

    def handle_write(self):
        self.last_out=time.time()
        sent=self.send(self.out_buffer)
        self.out_buffer=self.out_buffer[sent:]

    def handle_expt(self):
        data=self.socket.recv(8192,socket.MSG_OOB)
        logging.debug("OOB Data: %s"%data)

    def write(self,msg):
        logging.debug("Sending: >>>>>\n%s\n<<<<<"%str(msg))
        self.out_buffer+=msg
        
    def send_message(self,method,transaction_id=None,request=None,response=None,error=None):
        if not transaction_id:
            transaction_id=random.randint(0,0x7FFFFFFF)
        msg=Message()
        msg.method=method
        msg.transaction_id=transaction_id
        if request:
            msg.request=request.SerializeToString()
        if response:
            msg.response=response.SerializeToString()
        if error:
            msg.error.error=error.error
            msg.error.message=error.message
        s=msg.SerializeToString()
        logging.debug("Sending %d byte message (Req: %d, Res: %d Err: %d)"%(len(s)+4,len(msg.request),len(msg.response),msg.error.ByteSize()))
        self.write(struct.pack("!L",len(s))+s)
        return transaction_id
        
    def send_error(self,method,transaction_id,error,message):
        e=Error()
        e.error=error
        e.message=message
        self.send_message(method,transaction_id,error=e)
        
    def on_new_message(self,message):
        logging.debug("Recv message: (%s)>>>>>\n%s<<<<<"%(message.method,str(message)))
        if message.error.ByteSize():
            e=Error()
            e.ParseFromString(message.error)
            self.parent.on_error(self,message.transaction_id,e)
            return
        if message.request:
            h=getattr(self.parent,"req_"+message.method)
            msg=h.message_class()
            msg.ParseFromString(message.request)
            h(self,message.transaction_id,msg)
            return
        if message.response:
            h=getattr(self.parent,"res_"+message.method)
            msg=h.message_class()
            msg.ParseFromString(message.response)
            h(self,message.transaction_id,msg)
            return
        # No headers, keepalive
        logging.debug("RECV Keepalive")
        
    def keepalive(self):
        if time.time()-self.last_out>=KEEPALIVE_INTERVAL:
            self.send_message("keepalive")