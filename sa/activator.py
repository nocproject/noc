##
## Service Activator
##
import asyncore,os,logging,socket,pty,signal,time,re,sys,signal
from noc.sa.actions import get_action_class
from noc.sa.profiles import profile_registry
from noc.sa.sae_stream import RPCStream,file_hash
from noc.sa.protocols.sae_pb2 import *
from noc.lib.fileutils import safe_rewrite
from noc.lib.daemon import Daemon

##
## Maximal stream time to life
##
STREAM_MAX_TTL=180

##
## Abstract connection stream
##
class Stream(asyncore.dispatcher):
    def __init__(self,access_profile,activator=None):
        asyncore.dispatcher.__init__(self)
        self.access_profile=access_profile
        self.in_buffer=""
        self.out_buffer=""
        self.current_action=None
        self.start_time=time.time()
        self.activator=activator
        self.pid=None
        self.prepare_stream()
        if self.activator:
            self.activator.register_stream(self)
        
    def prepare_stream(self):
        raise Exception,"Not Implemented"
        
    def is_stale(self):
        return time.time()-self.start_time>STREAM_MAX_TTL
    
    def close(self):
        asyncore.dispatcher.close(self)
        if self.pid:
            pid,status=os.waitpid(self.pid,os.WNOHANG)
            if pid:
                logging.debug("Child pid=%d is already terminated. Zombie released"%pid)
            else:
                logging.debug("Child pid=%d is not terminated. Killing"%self.pid)
                os.kill(self.pid,signal.SIGKILL)
        if self.activator:
            self.activator.release_stream(self)
        
    def attach_action(self,action):
        logging.debug("attach_action %s"%str(action))
        self.current_action=action
        self.feed_action()
        
    def handle_connect(self): pass
    
    def handle_close(self):
        if self.current_action:
            self.current_action.close(None)
        self.close()
            
    def reconnect(self):
        self.to_reconnect=True
    
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
        self.pid,fd=pty.fork()
        if self.pid==0:
            os.execv("/usr/bin/telnet",["/usr/bin/telnet",self.access_profile.address])
        else:
            self.set_socket(asyncore.file_wrapper(fd))

##
## SSH Connection stream
##
class SSHStream(Stream):
    def prepare_stream(self):
        logging.debug("SSHStream connecting '%s'"%self.access_profile.address)
        self.pid,fd=pty.fork()
        if self.pid==0:
            os.execv("/usr/bin/ssh",["/usr/bin/ssh","-o","StrictHostKeyChecking no","-l",self.access_profile.user,self.access_profile.address])
        else:
            self.set_socket(asyncore.file_wrapper(fd))
##
## HTTP Connection stream
##
class HTTPStream(Stream):
    def prepare_stream(self):
        logging.debug("HTTPStream connecting to %s:%d"%(self.access_profile.address,80))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((self.access_profile.address,80))

##
## Values are defined in sae.proto's AccessScheme enum
##
SCHEME_TO_CODE={
    "telnet": TELNET,
    "ssh"   : SSH,
    "http"  : HTTP,
}

CODE_TO_SCHEME={
    TELNET : "telnet",
    SSH    : "ssh",
    HTTP   : "http",
}

STREAMS={
    TELNET : TelnetStream,
    SSH    : SSHStream,
    HTTP   : HTTPStream,
}
##
##
##
PULL_CONFIG_ACTIONS={
    TELNET : get_action_class("sa.actions.cli"),
    SSH    : get_action_class("sa.actions.cli"),
    HTTP   : get_action_class("sa.actions.http"),
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
        try:
            profile=profile_registry[request.access_profile.profile]
        except:
            e=Error()
            e.code=ERR_INVALID_PROFILE
            e.text="Invalid profile '%s'"%request.access_profile.profile
            done(controller,error=e)
            return
        if request.access_profile.scheme not in profile.supported_schemes:
            e=Error()
            e.code=ERR_INVALID_SCHEME
            e.text="Access scheme '%s' is not supported for profile '%s'"%(self.code_to_scheme(request.access_profile.scheme),
                request.access_profile.profile)
            done(controller,error=e)
            return
        args={
            "user"           : request.access_profile.user,
            "password"       : request.access_profile.password,
            "super_password" : request.access_profile.super_password,
        }
        if request.access_profile.scheme in [TELNET,SSH]:
            args["commands"]=profile.command_pull_config
        elif request.access_profile.scheme in [HTTP]:
            args["address"]=request.access_profile.address
        try:
            activator=getattr(self,"activator")
        except:
            activator=None
        action=PULL_CONFIG_ACTIONS[request.access_profile.scheme](
            transaction_id=controller.transaction.id,
            stream=STREAMS[request.access_profile.scheme](request.access_profile,activator),
            profile=profile,
            callback=pull_config_callback,
            args=args)
    # Utility functions
    def scheme_to_code(self,scheme):
        return SCHEME_TO_CODE[scheme]
        
    def code_to_scheme(self,code):
        return CODE_TO_SCHEME[code]

class ActivatorStream(RPCStream):
    def __init__(self,service,address,port):
        RPCStream.__init__(self,service)
        logging.debug("Connecting to %s:%d"%(address,port))
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((address,port))
##
## Activator supervisor and daemon
##
class Activator(Daemon):
    daemon_name="noc-activator"
    def __init__(self,config_path=None,daemonize=True):
        Daemon.__init__(self,config_path,daemonize)
        logging.info("Running activator '%s'"%self.config.get("activator","name"))
        self.sae_stream=None
        self.sae_reset=0
        self.service=Service()
        self.service.activator=self
        self.streams={}
        self.children={}
        self.trap_collector=None
        if self.config.get("activator","listen_traps"):
            from noc.sa.trapcollector import TrapCollector
            self.trap_collector=TrapCollector(self,self.config.get("activator","listen_traps"))
        self.is_registred=False
        self.register_transaction=None
        logging.info("Loading profile classes")
        profile_registry.register_all()
    
    def run(self):
        last_keepalive=time.time()
        while True:
            if self.sae_stream is None and time.time()-self.sae_reset>10:
                self.sae_stream=ActivatorStream(self.service,self.config.get("sae","host"),self.config.getint("sae","port"))
                self.register()
            asyncore.loop(timeout=1,count=5)
            # Close stale streams
            for s in [s for s in self.streams if s.is_stale()]:
                logging.info("Forceful close of stale stream")
                s.close()
            # Finally clean up zombies
            if self.streams:
                while True:
                    try:
                        pid,status=os.waitpid(-1,os.WNOHANG)
                    except:
                        break
                    if pid:
                        logging.debug("Zombie pid=%d is hunted and killed"%pid)
                    else:
                        break
                
    def register_stream(self,stream):
        logging.debug("Registering stream %s"%str(stream))
        self.streams[stream]=None
        
    def release_stream(self,stream):
        logging.debug("Releasing stream %s"%str(stream))
        del self.streams[stream]
                
    def reboot(self):
        logging.info("Rebooting")
        os.execv(sys.executable,[sys.executable]+sys.argv)
        
    def on_stream_close(self,sae_stream):
        logging.debug("SAE connection lost")
        self.sae_stream=None
        self.sae_reset=time.time()
        
    def on_trap_config_change(self,ip,oid):
        self.notify_trap_config_change(ip)
        
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
                if self.config.get("activator","software_update") and not os.path.exists(os.path.join("sa","sae.py")):
                    logging.info("Requesting software update")
                    self.manifest()
                else:
                    logging.info("In-bundle package. Skiping software updates")
                if self.trap_collector:
                    self.get_trap_filter() # Bad place
            else:
                logging.error("Registration id mismatch")
                self.register_transaction=None
        logging.info("Registering as '%s'"%self.config.get("activator","name"))
        r=RegisterRequest()
        r.name=self.config.get("activator","name")
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
                    if not os.path.exists(cs.name) or cs.hash!=file_hash(cs.name):
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
                    logging.info("Upgrade: %s"%u.name)
                    safe_rewrite(u.name,u.code)
                self.software_upgrade_transaction=None
                self.reboot()
            else:
                logging.error("Transaction id mismatch")
                self.software_upgrade_transaction=None
        logging.debug("Requesting software upgrade for %s"%str(update_list))
        r=SoftwareUpgradeRequest()
        for f in update_list:
            r.names.append(f)
        self.software_upgrade_transaction=self.sae_stream.proxy.software_upgrade(r,software_upgrade_callback)
    ##
    ##
    ##
    def get_trap_filter(self):
        def get_trap_filter_callback(transaction,response=None,error=None):
            if error:
                logging.error("get_trap_filter error: %s"%error.text)
                return
            if response and self.trap_collector:
                logging.info("Updating trap filters")
                filters={}
                for r in response.filters:
                    if r.ip not in filters:
                        filters[r.ip]={}
                    for a in r.actions:
                        if a.oid not in filters[r.ip]:
                            filters[r.ip][a.oid]=[]
                        for aa in a.actions:
                            if aa==TA_IGNORE:
                                continue
                            elif aa==TA_NOTIFY_CONFIG_CHANGE:
                                action=self.on_trap_config_change
                            filters[r.ip][a.oid].append(action)
                self.trap_collector.set_trap_filter(filters)
        r=TrapFilterRequest()
        self.sae_stream.proxy.get_trap_filter(r,get_trap_filter_callback)
    ##
    ##
    ##
    def notify_trap_config_change(self,ip):
        def notify_trap_config_change_callback(transaction,response=None,error=None):
            if error:
                logging.error("notify_trap_config_change failed: %s"%error)
                return
        r=NotifyTrapConfigChangeRequest()
        r.ip=ip
        self.sae_stream.proxy.notify_trap_config_change(r,notify_trap_config_change_callback)
