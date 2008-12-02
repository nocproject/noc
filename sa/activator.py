##
## Service Activator
##
import os,logging,pty,signal,time,re,sys,signal
from errno import ECONNREFUSED
from noc.sa.actions import action_registry,scheme_registry,ActionSocket
from noc.sa.profiles import profile_registry
from noc.sa.rpc import RPCSocket,file_hash,get_digest
from noc.sa.protocols.sae_pb2 import *
from noc.lib.fileutils import safe_rewrite
from noc.lib.daemon import Daemon
from noc.lib.fsm import FSM,check_state
from noc.lib.nbsocket import ConnectedTCPSocket,SocketFactory


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
        if self.activator.factory.count_subclass_sockets(ActionSocket)>=self.activator.config.getint("activator","max_pull_config"):
            e=Error()
            e.code=ERR_OVERLOAD
            e.text="pull_config concurrent session limit reached"
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
        scheme_class=scheme_registry.get_by_id(request.access_profile.scheme)
        action_class=action_registry[scheme_class.default_action]
        action=action_class(
            transaction_id=controller.transaction.id,
            stream=scheme_class(self.activator.factory,request.access_profile),
            profile=profile,
            callback=pull_config_callback,
            args=args)
##
##
class ActivatorSocket(RPCSocket,ConnectedTCPSocket):
    def __init__(self,factory,address,port,local_address=None):
        ConnectedTCPSocket.__init__(self,factory,address,port,local_address)
        RPCSocket.__init__(self,factory.activator.service)
        
    def activator_event(self,event):
        self.factory.activator.event(event)
    
    def on_connect(self):
        self.activator_event("connect")
    
    def on_close(self):
        self.activator_event("close")
    
    def on_conn_refused(self):
        self.activator_event("refused")


##
## Activator supervisor and daemon
##
class Activator(Daemon,FSM):
    daemon_name="noc-activator"
    FSM_NAME="Activator"
    DEFAULT_STATE="IDLE"
    STATES={
        "IDLE": {
                "timeout" : "CONNECT",
                "close"   : "IDLE",
                },
        "CONNECT" : {
                "timeout" : "IDLE",
                "refused" : "IDLE",
                "close"   : "IDLE",
                "connect" : "CONNECTED",
                },
        "CONNECTED" : {
                "timeout" : "IDLE",
                "close"   : "IDLE",
                "register": "REGISTRED",
                "error"   : "IDLE",
        },
        "REGISTRED" : {
                "timeout" : "IDLE",
                "auth"    : "AUTHENTICATED",
                "close"   : "IDLE",
                "error"   : "IDLE",
        },
        "AUTHENTICATED" : {
                "establish" : "ESTABLISHED",
                "upgrade"   : "UPGRADE",
                "close"   : "IDLE",
        },
        "UPGRADE" : {
                "establish" : "ESTABLISHED",
                "close"     : "IDLE",
        },
        "ESTABLISHED" : {
                "close"   : "IDLE",
                
        }
    }
    def __init__(self):
        Daemon.__init__(self)
        logging.info("Running activator '%s'"%self.config.get("activator","name"))
        self.service=Service()
        self.service.activator=self
        self.factory=SocketFactory(tick_callback=self.tick)
        self.factory.activator=self
        self.children={}
        self.sae_stream=None
        self.trap_collector=None
        logging.info("Loading profile classes")
        action_registry.register_all()
        profile_registry.register_all()
        self.nonce=None
        FSM.__init__(self)
        
    ##
    ## IDLE state 
    ##
    def on_IDLE_enter(self):
        if self.sae_stream:
            self.sae_stream.close()
            self.sae_stream=None
        if self.trap_collector:
            self.stop_trap_collector()
        self.set_timeout(5)
    ##
    ## CONNECT state
    ##
    def on_CONNECT_enter(self):
        self.set_timeout(10)
        self.sae_stream=ActivatorSocket(self.factory,self.config.get("sae","host"),self.config.getint("sae","port"),
            self.config.get("sae","local_address"))
    ##
    ## CONNECTED state
    ##
    def on_CONNECTED_enter(self):
        self.set_timeout(10)
        self.register()
    ##
    ## REGISTRED
    ##
    def on_REGISTRED_enter(self):
        self.set_timeout(10)
        self.auth()
    ##
    ## AUTHENTICATED
    ##
    def on_AUTHENTICATED_enter(self):
        if self.config.get("activator","software_update") and not os.path.exists(os.path.join("sa","sae.py")):
            self.event("upgrade")
        else:
            logging.info("In-bundle package. Skiping software updates")
            self.event("establish")
    ##
    ## UPGRADE
    ##
    def on_UPGRADE_enter(self):
        logging.info("Requesting software update")
        self.manifest()
    ##
    ## ESTABLISHED
    ##
    def on_ESTABLISHED_enter(self):
        if self.config.get("activator","listen_traps"):
            self.start_trap_collector()
    ##
    ##
    ##
    def start_trap_collector(self):
        logging.debug("Starting trap collector")
        from noc.sa.trapcollector import TrapCollector
        self.trap_collector=TrapCollector(self.factory,self.config.get("activator","listen_traps"),162)
        self.get_trap_filter()
        
    def stop_trap_collector(self):
        if self.trap_collector:
            logging.debug("Stopping trap collector")
            self.trap_collector.close()
            self.trap_collector=None
    ##
    ## Main event loop
    ##
    def run(self):
        self.factory.run(run_forever=True)
                
    def register_stream(self,stream):
        logging.debug("Registering stream %s"%str(stream))
        self.streams[stream]=None
        
    def release_stream(self,stream):
        logging.debug("Releasing stream %s"%str(stream))
        del self.streams[stream]
                
    def reboot(self):
        logging.info("Rebooting")
        os.execv(sys.executable,[sys.executable]+sys.argv)

    def on_trap_config_change(self,ip,oid):
        self.notify_trap_config_change(ip)
        
    # Handlers
    ##
    ## Register
    ##
    @check_state("CONNECTED")
    def register(self):
        def register_callback(transaction,response=None,error=None):
            if self.get_state()!="CONNECTED":
                return
            if error:
                logging.error("Registration error: %s"%error.text)
                self.event("error")
                return
            logging.info("Registration accepted")
            self.nonce=response.nonce
            self.event("register")
        logging.info("Registering as '%s'"%self.config.get("activator","name"))
        r=RegisterRequest()
        r.name=self.config.get("activator","name")
        self.sae_stream.proxy.register(r,register_callback)
    ##
    ## Auth
    ##
    @check_state("REGISTRED")
    def auth(self):
        def auth_callback(transaction,response=None,error=None):
            if self.get_state()!="REGISTRED":
                return
            if error:
                logging.error("Authentication failed: %s"%error.text)
                self.event("error")
                return
            logging.info("Authenticated")
            self.event("auth")
        logging.info("Authenticating")
        r=AuthRequest()
        r.name=self.config.get("activator","name")
        r.digest=get_digest(r.name,self.config.get("activator","secret"),self.nonce)
        self.sae_stream.proxy.auth(r,auth_callback)
        
    ##
    ##
    ##
    @check_state("UPGRADE")
    def manifest(self):
        def manifest_callback(transaction,response=None,error=None):
            if self.get_state()!="UPGRADE":
                return
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
                    self.event("establish")
            else:
                logging.error("Transaction id mismatch")
                self.manifest_transaction=None
        logging.info("Requesting manifest")
        r=ManifestRequest()
        self.manifest_transaction=self.sae_stream.proxy.manifest(r,manifest_callback)
    ##
    ## 
    ##
    @check_state("UPGRADE")
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
    @check_state("ESTABLISHED")
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
    # Signal handlers

    # SIGUSR1 returns process info
    def SIGUSR1(self,signo,frame):
        s=[
            ["factory.sockets",len(self.factory)],
        ]
        if self.sae_stream:
            s+=self.sae_stream.stats
        logging.info("STATS:")
        for n,v in s:
            logging.info("%s: %s"%(n,v))
    # SIGCHLD: Zombie hunting
    def SIGCHLD(self,signo,frame):
        while True:
            try:
                pid,status=os.waitpid(-1,os.WNOHANG)
            except:
                break
            if pid:
                logging.debug("Zombie pid=%d is hunted and mercilessly killed"%pid)
            else:
                break