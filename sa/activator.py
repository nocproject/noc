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
        self.syslog_collector=None
        logging.info("Loading profile classes")
        action_registry.register_all()
        profile_registry.register_all()
        self.nonce=None
        FSM.__init__(self)
        self.next_filter_update=None
        
    ##
    ## IDLE state 
    ##
    def on_IDLE_enter(self):
        if self.sae_stream:
            self.sae_stream.close()
            self.sae_stream=None
        if self.trap_collector:
            self.stop_trap_collector()
        if self.syslog_collector:
            self.stop_syslog_collector()
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
        to_refresh_filters=False
        self.next_filter_update=None
        if self.config.get("activator","listen_traps"):
            self.start_trap_collector()
            to_refresh_filters=True
        if self.config.get("activator","listen_syslog"):
            self.start_syslog_collector()
            to_refresh_filters=True
        if to_refresh_filters:
            self.get_event_filter()
    ##
    ##
    ##
    def start_trap_collector(self):
        logging.debug("Starting trap collector")
        from noc.sa.trapcollector import TrapCollector
        self.trap_collector=TrapCollector(self.factory,self.config.get("activator","listen_traps"),162)
        
    def stop_trap_collector(self):
        if self.trap_collector:
            logging.debug("Stopping trap collector")
            self.trap_collector.close()
            self.trap_collector=None
    ##
    ##
    ##
    def start_syslog_collector(self):
        logging.debug("Starting syslog collector")
        from noc.sa.syslogcollector import SyslogCollector
        self.syslog_collector=SyslogCollector(self.factory,self.config.get("activator","listen_syslog"),514)
        
    def stop_syslog_collector(self):
        if self.syslog_collector:
            logging.debug("Stopping syslog collector")
            self.syslog_collector.close()
            self.syslog_collector=None
    ##
    ## Main event loop
    ##
    def run(self):
        self.factory.run(run_forever=True)
    ##
    def tick(self):
        if self.next_filter_update and time.time()>self.next_filter_update:
            self.get_event_filter()
        super(Activator,self).tick()
                
    def register_stream(self,stream):
        logging.debug("Registering stream %s"%str(stream))
        self.streams[stream]=None
        
    def release_stream(self,stream):
        logging.debug("Releasing stream %s"%str(stream))
        del self.streams[stream]
                
    def reboot(self):
        logging.info("Rebooting")
        os.execv(sys.executable,[sys.executable]+sys.argv)
        
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
    def get_event_filter(self):
        def event_filter_callback(transaction,response=None,error=None):
            if error:
                logging.error("get_event_filter error: %s"%error.text)
                return
            # source -> [(ip,mask,callback)]
            filters={ES_SNMP_TRAP:[],ES_SYSLOG:[]}
            for r in response.filters:
                try:
                    m=re.compile(r.mask)
                except:
                    logging.error("get_event_filter(): invalid REGEXP '%s'"%r.mask)
                    continue
                f=(r.ip,m,
                    {
                    EA_IGNORE        : None,
                    EA_PROXY         : self.on_event_proxy,
                    EA_CONFIG_CHANGED: self.on_event_config_changed,
                    }[r.action]
                )
                filters[r.source].append(f)
            if self.trap_collector:
                self.trap_collector.set_event_filter(filters[ES_SNMP_TRAP])
            if self.syslog_collector:
                self.syslog_collector.set_event_filter(filters[ES_SYSLOG])
            self.next_filter_update=time.time()+response.expire
        s=[]
        if self.trap_collector:
            s.append(ES_SNMP_TRAP)
        if self.syslog_collector:
            s.append(ES_SYSLOG)
        if not s:
            return
        r=EventFilterRequest()
        for es in s:
            r.sources.append(es)
        self.sae_stream.proxy.event_filter(r,event_filter_callback)
    ##
    ##
    ##
    def on_event_proxy(self,source,ip,message,body=None):
        def on_event_proxy_callback(transaction,response=None,error=None):
            if error:
                logging.error("event_proxy failed: %s"%error)
                return
        r=EventProxyRequest()
        r.source=source
        r.ip=ip
        r.message=message
        if body:
            r.body=body
        self.sae_stream.proxy.event_proxy(r,on_event_proxy_callback)
    ##
    def on_event_config_changed(self,source,ip,message,body=None):
        def on_event_config_changed(transaction,response=None,error=None):
            if error:
                logging.error("event_config_changed failed: %s"%error)
                return
        r=EventConfigChangedRequest()
        r.source=source
        r.ip=ip
        self.sae_stream.proxy.event_config_changed(r,on_event_config_changed)
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