import asyncore,logging,os,socket,re

##
rx_url=re.compile(r"^(?P<scheme>[^:]+)://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^/]+)(?:(?P<port>\d+))?(?P<path>.*)$")

##
## Abstract connection stream
##
class Stream(asyncore.dispatcher):
    def __init__(self,profile,user=None,password=None,host=None,port=None,path=None):
        asyncore.dispatcher.__init__(self)
        self.profile=profile
        self.user=user
        self.password=password
        self.host=host
        self.port=port
        self.path=path
        self.in_buffer=""
        self.out_buffer=""
        self.current_action=None
        self.prepare_stream()
        
    def prepare_stream(self):
        raise Exception,"Not Implemented"
        
    def attach_action(self,action):
        logging.debug("attach_action %s"%str(action))
        self.current_action=action
        self.feed_action()
        
    def handle_connect(self): pass
    
    def handle_close(self): pass
    
    def handle_read(self):
        self.in_buffer+=self.recv(8192)
        self.feed_action()
        
    def writable(self):
        return len(self.out_buffer)>0
    
    def handle_write(self):
        sent=self.send(self.out_buffer)
        self.out_buffer=self.out_buffer[sent:]
        
    def write(self,msg):
        self.out_buffer+=msg
        
    def retain_input(self,msg):
        self.in_buffer=msg+self.in_buffer
        
    def feed_action(self):
        if self.in_buffer and self.current_action:
            self.current_action.feed(self.in_buffer)
            self.in_buffer=""
            
    @classmethod
    def get_stream(cls,profile,url):
        match=rx_url.match(url)
        if not match:
            raise Exception("Invalid URL: %s"%url)
            return
        scheme=match.group("scheme")
        user=match.group("user")
        password=match.group("password")
        host=match.group("host")
        port=match.group("port")
        path=match.group("path")
        if scheme not in STREAMS:
            raise Exception("Invalid scheme: %s"%scheme)
        return STREAMS[scheme](profile=profile,user=user,password=password,host=host,port=port,path=path)
##
## Telnet connection stream
##
class TelnetStream(Stream):
    def prepare_stream(self):
        logging.debug("TelnetStream connecting %s"%self.host)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connect((self.host,23))
##
## SSH Connection stream
##
class SSHStream(Stream):
    def prepare_stream(self):
        logging.debug("SSHStream connecting %s"%self.host)
        pid,fd=os.forkpty()
        if pid==0:
            os.execv("/usr/bin/ssh",["/usr/bin/ssh","-l",self.user,self.host])
        else:
            self.set_socket(asyncore.file_wrapper(fd))
##
##
##
STREAMS={
    "telnet" : TelnetStream,
    "ssh"    : SSHStream,
}