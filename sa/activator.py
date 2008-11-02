##
## Service Activator
##
import asyncore,os,logging,socket,pty,signal,time,re,sys
from noc.sa.actions import get_action_class
from noc.sa.profiles import profile_registry
from noc.sa.sae_stream import RPCStream,file_hash
from noc.sa.protocols.sae_pb2 import *

##
## Abstract connection stream
##
class Stream(asyncore.dispatcher):
    def __init__(self,access_profile):
        asyncore.dispatcher.__init__(self)
        self.access_profile=access_profile
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
    
    def handle_close(self):
        if self.current_action:
            self.current_action.close(None)
        self.close()
    
    def handle_read(self):
        try:
            self.in_buffer+=self.recv(8192)
        except:
            return
        self.feed_action()
        
    def writable(self):
        return len(self.out_buffer)>0
    
    def handle_write(self):
        sent=self.send(self.out_buffer)
        self.out_buffer=self.out_buffer[sent:]
        
    def handle_expt(self):
        data=self.socket.recv(8192,socket.MSG_OOB)
        logging.debug("OOB Data: %s"%data)
        
    def write(self,msg):
        self.out_buffer+=msg
        
    def retain_input(self,msg):
        self.in_buffer=msg+self.in_buffer
        
    def feed_action(self):
        if self.in_buffer and self.current_action:
            self.current_action.feed(self.in_buffer)
            self.in_buffer=""

##
## Telnet connection stream
##
class TelnetStream(Stream):
    def prepare_stream(self):
        logging.debug("TelnetStream connecting '%s'"%self.access_profile.address)
        pid,fd=pty.fork()
        if pid==0:
            os.execv("/usr/bin/telnet",["/usr/bin/telnet",self.access_profile.address])
        else:
            self.set_socket(asyncore.file_wrapper(fd))

##
## SSH Connection stream
##
class SSHStream(Stream):
    def prepare_stream(self):
        logging.debug("SSHStream connecting '%s'"%self.access_profile.address)
        pid,fd=pty.fork()
        if pid==0:
            os.execv("/usr/bin/ssh",["/usr/bin/ssh","-o","StrictHostKeyChecking no","-l",self.access_profile.user,self.access_profile.address])
        else:
            self.set_socket(asyncore.file_wrapper(fd))
##
## Values are defined in sae.proto's AccessScheme enum
##
STREAMS={
    TELNET : TelnetStream,
    SSH    : SSHStream,
}

##
##
##
class Service(SAEService):
    def ping(self,controller,request,done):
        done(controller,response=PingResponse())
        
    def pull_config(self,controller,request,done):
        def pull_config_callback(action):
            if action.status:
                c=PullConfigResponse()
                c.config=action.profile().cleaned_config(action.result)
                done(controller,response=c)
            else:
                e=Error()
                e.code=ERR_INTERNAL
                e.text="pull_config internal error"
                done(controller,error=e)
        profile=profile_registry[request.access_profile.profile]
        action=get_action_class("sa.actions.cli")(
            transaction_id=controller.transaction.id,
            stream=STREAMS[request.access_profile.scheme](request.access_profile),
            profile=profile,
            callback=pull_config_callback,
            args={
                "user"     : request.access_profile.user,
                "password" : request.access_profile.password,
                "commands" : profile.command_pull_config,
                })

class ActivatorStream(RPCStream):
    def __init__(self,service,address,port):
        RPCStream.__init__(self,service)
        logging.debug("Connecting to %s:%d"%(address,port))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((address,port))
##
## Activator supervisor and daemon
##
class Activator(object):
    def __init__(self,name,sae_ip,sae_port):
        logging.info("Running activator '%s'"%name)
        self.name=name
        self.sae_ip=sae_ip
        self.sae_port=int(sae_port)
        self.sae_stream=None
        self.sae_reset=0
        self.service=Service()
        self.service.activator=self
        self.streams={}
        self.children={}
        self.is_registred=False
        self.register_transaction=None
        logging.info("Loading profile classes")
        profile_registry.register_all()
        logging.info("Setting signal handlers")
        signal.signal(signal.SIGCHLD,self.sig_chld)
    
    def run(self):
        last_keepalive=time.time()
        while True:
            if self.sae_stream is None and time.time()-self.sae_reset>10:
                self.sae_stream=ActivatorStream(self.service,self.sae_ip,self.sae_port)
                self.register()
            asyncore.loop(timeout=1,count=10)
            
    def reboot(self):
        logging.info("Rebooting")
        os.execv(sys.executable,[sys.executable]+sys.argv)

    def sig_chld(self,signum,frame):
        pid,statis=os.waitpid(-1,os.WNOHANG)
        
    def on_stream_close(self,sae_stream):
        logging.debug("SAE connection lost")
        self.sae_stream=None
        self.sae_reset=time.time()
        
    # Handlers
    ##
    ## Register
    ##
    def register(self):
        def register_callback(transaction,response=None,error=None):
            if error:
                logging.error("Registration error: %s"%error.text)
                self.register_transaction=None
                return
            if transaction.id==self.register_transaction.id:
                logging.info("Registration accepted")
                self.is_registred=True
                self.register_transaction=None
                try:
                    import noc.sa.sae
                    logging.debug("In-budle package. Skipping software updates")
                except ImportError:
                    self.manifest()
            else:
                logging.error("Registration id mismatch")
                self.register_transaction=None
        logging.info("Registering as '%s'"%self.name)
        r=RegisterRequest()
        r.name=self.name
        self.register_transaction=self.sae_stream.proxy.register(r,register_callback)
        
    ##
    ##
    ##
    def manifest(self):
        def manifest_callback(transaction,response=None,error=None):
            if error:
                logging.error("Manifest error: %s"%error.text)
                self.manifest_transaction=None
                return
            if transaction.id==self.manifest_transaction.id:
                update_list=[]
                for cs in response.files:
                    if cs.hash!=file_hash(cs.name):
                        update_list.append(cs.name)
                self.manifest_transaction=None
                if update_list:
                    self.software_upgrade(update_list)
            else:
                logging.error("Transaction id mismatch")
                self.manifest_transaction=None
        logging.info("Requesting manifest")
        r=ManifestRequest()
        self.manifest_transaction=self.sae_stream.proxy.manifest(r,manifest_callback)
    ##
    ## 
    ##
    def software_upgrade(self,update_list):
        def software_upgrade_callback(transaction,response=None,error=None):
            if error:
                logging.error("Upgrade error: %s"%error.text)
                self.software_upgrade_transaction=None
                return
            if transaction.id==self.software_upgrade_transaction.id:
                logging.info("Upgrading software")
                for u in response.codes:
                    logging.info("Upgrade: %s [NOT IMPLEMENTING]"%u.name)
                    logging.debug(u.code)
                self.software_upgrade_transaction=None
                self.reboot()
            else:
                logging.error("Transaction id mismatch")
                self.software_upgrade_transaction=None
        r=SoftwareUpgradeRequest()
        for f in update_list:
            r.names.append(f)
        self.software_upgrade_transaction=self.sae_stream.proxy.software_upgrade(r,software_upgrade_callback)
    
