##
## Simple RIPE whois client
##
import asyncore,socket,logging

WHOIS_SERVER="whois.ripe.net"
WHOIS_PORT=43

class Whois(asyncore.dispatcher_with_send):
    def __init__(self,query,callback=None,fields=None,map=None):
        asyncore.dispatcher_with_send.__init__(self,map=map)
        self.query=query.strip()
        self.output=[]
        self.callback=callback
        self.fields=fields
        logging.debug("whois(%s)"%self.query)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connect((WHOIS_SERVER,WHOIS_PORT))
        
    def handle_connect(self):
        self.send(self.query+"\r\n")
    
    def handle_expt(self):
        self.close()
        raise Exception
    
    def handle_read(self):
        self.output+=[self.recv(8192)]
    
    def handle_close(self):
        self.close()
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
#3
def whois(q,fields=None):
    s=[]
    w=Whois(q,s.append,fields)
    asyncore.loop()
    return s