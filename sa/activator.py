# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service Activator Daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
import os,logging,pty,signal,time,re,sys,signal,Queue,cPickle,tempfile
from errno import ECONNREFUSED
from noc.sa.profiles import profile_registry
from noc.sa.script import script_registry,ScriptSocket
from noc.sa.rpc import RPCSocket,file_hash,get_digest
from noc.sa.protocols.sae_pb2 import *
from noc.sa.protocols.pm_pb2 import *
from noc.sa.servers import ServersHub
from noc.lib.fileutils import safe_rewrite
from noc.lib.daemon import Daemon
from noc.lib.fsm import FSM,check_state
from noc.lib.nbsocket import ConnectedTCPSocket,ConnectedTCPSSLSocket,SocketFactory,PTYSocket,HAS_SSL,ListenUDPSocket,AcceptedTCPSocket,ListenTCPSocket
from noc.lib.debug import DEBUG_CTX_CRASH_PREFIX
from noc.lib.pmhash import pmhash
from threading import Lock

##
##
##
class Service(SAEService):
    def ping(self,controller,request,done):
        done(controller,response=PingResponse())
        
    def script(self,controller,request,done):
        def script_callback(script):
            if script.result:
                c=ScriptResponse()
                c.result=script.result
                done(controller,response=c)
            else:
                e=Error()
                if script.to_cancel: # Timeout
                    e.code=ERR_TIMEOUT
                    e.text="Timed out"
                else:
                    e.code=ERR_SCRIPT_EXCEPTION
                    e.text=script.error_traceback
                done(controller,error=e)
        try:
            profile=profile_registry[request.access_profile.profile]
        except:
            e=Error()
            e.code=ERR_INVALID_PROFILE
            e.text="Invalid profile '%s'"%request.access_profile.profile
            done(controller,error=e)
            return
        try:
            script_class=script_registry[request.script]
        except:
            e=Error()
            e.code=ERR_INVALID_SCRIPT
            e.text="Invalid script '%s'"%request.script
            done(controller,error=e)
            return
        if request.access_profile.scheme not in profile.supported_schemes:
            e=Error()
            e.code=ERR_INVALID_SCHEME
            e.text="Access scheme '%s' is not supported for profile '%s'"%(self.code_to_scheme(request.access_profile.scheme),
                request.access_profile.profile)
            done(controller,error=e)
            return
        # Check host was checked by ping. Reject executing of script on known unreachable hosts
        if self.activator.ping_check_results\
                and request.access_profile.address in self.activator.ping_check_results\
                and not self.activator.ping_check_results[request.access_profile.address]:
            e=Error()
            e.code=ERR_DOWN
            e.text="Host is down"
            done(controller,error=e)
            return
        # Check [activator]/max_pull_config limit
        if not self.activator.can_run_script():
            e=Error()
            e.code=ERR_OVERLOAD
            e.text="script concurrent session limit reached"
            done(controller,error=e)
            return
        kwargs={}
        for a in request.kwargs:
            kwargs[str(a.key)]=cPickle.loads(str(a.value))
        self.activator.run_script(request.script,request.access_profile,script_callback,**kwargs)
    
    def ping_check(self,controller,request,done):
        def ping_check_callback(unreachable):
            u=set(unreachable)
            r=PingCheckResponse()
            self.activator.ping_check_results={} # Reset previous ping checks
            for a in request.addresses:
                if a in u:
                    r.unreachable.append(a)
                    self.activator.ping_check_results[a]=False
                else:
                    r.reachable.append(a)
                    self.activator.ping_check_results[a]=True
            done(controller,response=r)
        self.activator.ping_check([a for a in request.addresses],ping_check_callback)
##
## Activator-SAE channel
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
## SSL-enabled Activator socket
##
class ActivatorSSLSocket(RPCSocket,ConnectedTCPSSLSocket):
    def __init__(self,factory,address,port,local_address=None):
        ConnectedTCPSSLSocket.__init__(self,factory,address,port,local_address)
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
## External fping process.
## Runs fping, supplies a list of checked hosts
## and reads a list uf unreachable hosts
##
class FPingProbeSocket(PTYSocket):
    def __init__(self,factory,fping_path,addresses,callback):
        self.result=""
        # Write hosts list to temporary file
        h,self.tmp_path=tempfile.mkstemp()
        f=os.fdopen(h,"w")
        f.write("\n".join(addresses)+"\n")
        f.close()
        self.callback=callback
        # Fping requires root to read hosts from file. Run it through the wrapper
        PTYSocket.__init__(self,factory,["./scripts/stdin-wrapper",self.tmp_path,fping_path,"-A","-u"])
        
    def on_close(self):
        os.unlink(self.tmp_path)
        # fping issues duplicated addresses sometimes.
        # Remove duplicates
        r={}
        for u in [x.strip() for x in self.result.split("\n") if x.strip()]:
            r[u]=None
        self.callback(r.keys())
        
    def on_read(self,data):
        self.result+=data
##
## PM Collector socket
##
class PMCollectorSocket(ListenUDPSocket):
    def __init__(self,activator,address,port):
        self.activator=activator
        super(PMCollectorSocket,self).__init__(activator.factory,address,port)

    def on_read(self,data,address,port):
        msg=PMMessage()
        try:
            msg.ParseFromString(data)
        except:
            return
        # Check hash
        if pmhash(address,self.activator.pm_data_secret,[d.timestamp for d in msg.result]+[d.timestamp for d in msg.data])!=msg.checksum:
            logging.error("Invalid PM hash in packet from %s"%address)
            return
        # Queue data
        self.activator.queue_pm_result([(d.probe_name,d.probe_type,d.timestamp,d.service,d.result,d.message) for d in msg.result if d.probe_name])
        self.activator.queue_pm_data([(d.name,d.timestamp,d.is_null,d.value) for d in msg.data if d.name])
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
        self.activator_name=self.config.get("activator","name")
        logging.info("Running activator '%s'"%self.activator_name)
        self.stand_alone_mode=self.config.get("activator","software_update") and not os.path.exists(os.path.join("sa","sae.py"))
        self.service=Service()
        self.service.activator=self
        self.factory=SocketFactory(tick_callback=self.tick)
        self.factory.activator=self
        self.children={}
        self.ping_check_results={} # address -> last ping check result
        self.sae_stream=None
        self.event_sources=set()
        self.trap_collectors=[]   # List of SNMP Trap collectors
        self.syslog_collectors=[] # List of SYSLOG collectors
        self.pm_data_collectors=[] # List of PM Data collectors
        logging.info("Loading profile classes")
        profile_registry.register_all() # Should be performed from ESTABLISHED state
        script_registry.register_all()
        self.nonce=None
        FSM.__init__(self)
        self.next_filter_update=None
        self.next_crashinfo_check=None
        self.next_heartbeat=None
        self.script_threads={}
        self.max_script_threads=self.config.getint("activator","max_pull_config")
        self.script_lock=Lock()
        self.script_call_queue=Queue.Queue()
        self.pm_data_queue=[]
        self.pm_result_queue=[]
        self.pm_data_secret=self.config.get("activator","pm_data_secret")
        self.servers=ServersHub(self)
        # CLI debug logging
        self.log_cli_sessions=self.config.getboolean("main","log_cli_sessions")
        self.log_cli_sessions_path=self.config.get("main","log_cli_sessions_path")
        self.log_cli_sessions_ip_re=re.compile(self.config.get("main","log_cli_sessions_ip_re"))
        self.log_cli_sessions_script_re=re.compile(self.config.get("main","log_cli_sessions_script_re"))
        
    ##
    ## IDLE state 
    ##
    def on_IDLE_enter(self):
        if self.sae_stream:
            self.sae_stream.close()
            self.sae_stream=None
        if self.trap_collectors:
            self.stop_trap_collectors()
        if self.syslog_collectors:
            self.stop_syslog_collectors()
        if self.pm_data_collectors:
            self.stop_pm_data_collectors()
        self.set_timeout(5)
    ##
    ## CONNECT state
    ##
    def on_CONNECT_enter(self):
        self.set_timeout(10)
        if HAS_SSL and self.config.get("sae","ssl_host"):
            self.sae_stream=ActivatorSSLSocket(self.factory,self.config.get("sae","ssl_host"),self.config.getint("sae","ssl_port"),
                self.config.get("sae","local_address"))
        else:
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
        if self.stand_alone_mode:
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
            self.start_trap_collectors()
            to_refresh_filters=True
        if self.config.get("activator","listen_syslog"):
            self.start_syslog_collectors()
            to_refresh_filters=True
        if self.config.get("activator","listen_pm_data"):
            self.start_pm_data_collectors()
            to_refresh_filters=True
        if to_refresh_filters:
            self.get_event_filter()
        if self.stand_alone_mode:
            self.check_crashinfo()
    ##
    ## Launch SNMP Trap collectors
    ##
    def start_trap_collectors(self):
        logging.debug("Starting trap collectors")
        from noc.sa.trapcollector import TrapCollector
        self.trap_collectors=[
            TrapCollector(self,ip,port)
            for ip,port
            in self.resolve_addresses(self.config.get("activator","listen_traps"),162)
        ]
    ##
    ## Disable SNMP Trap collectors
    ##
    def stop_trap_collectors(self):
        if self.trap_collectors:
            logging.debug("Stopping trap collectors")
            for tc in self.trap_collectors:
                tc.close()
            self.trap_collectors=[]
    ##
    ## Launch syslog collectors
    ##
    def start_syslog_collectors(self):
        logging.debug("Starting syslog collectors")
        from noc.sa.syslogcollector import SyslogCollector
        self.syslog_collectors=[
            SyslogCollector(self,ip,port)
            for ip,port
            in self.resolve_addresses(self.config.get("activator","listen_syslog"),514)
        ]
    ##
    ## Disable syslog collectors
    ##
    def stop_syslog_collectors(self):
        if self.syslog_collectors:
            logging.debug("Stopping syslog collectors")
            for sc in self.syslog_collectors:
                sc.close()
            self.syslog_collectors=[]
    ##
    ## Launch PM data collectors
    ##
    def start_pm_data_collectors(self):
        logging.debug("Starting PM Data collectors")
        self.pm_data_collectors=[
            PMCollectorSocket(self,ip,port)
            for ip,port
            in self.resolve_addresses(self.config.get("activator","listen_pm_data"),19704)
        ]
    ##
    ## Disable syslog collectors
    ##
    def stop_pm_data_collectors(self):
        if self.pm_data_collectors:
            logging.debug("Stopping PM Data collectors")
            for pdc in self.pm_data_collectors:
                pdc.close()
            self.pm_data_collectors=[]
    ##
    ## Checks wrether max_pull_config limit exceeded
    ##
    def can_run_script(self):
        with self.script_lock:
            return len(self.script_threads)<self.max_script_threads
    
    ##
    ## Script support
    ##
    def run_script(self,name,access_profile,callback,**kwargs):
        logging.info("Script %s(%s)"%(name,access_profile.address))
        pv,pos,sn=name.split(".",2)
        profile=profile_registry["%s.%s"%(pv,pos)]()        
        script=script_registry[name](profile,self,access_profile,**kwargs)
        with self.script_lock:
            self.script_threads[script]=callback
            logging.info("%d script threads"%(len(self.script_threads)))
        script.start()

    def on_script_exit(self,script):
        logging.info("Script %s(%s) completed"%(script.name,script.access_profile.address))
        with self.script_lock:
            cb=self.script_threads.pop(script)
            logging.info("%d script threads left"%(len(self.script_threads)))
        cb(script)
        
    def request_call(self,f,*args,**kwargs):
        logging.debug("Requesting call: %s(*%s,**%s)"%(f,args,kwargs))
        self.script_call_queue.put((f,args,kwargs))
    ##
    ##
    ##
    def ping_check(self,addresses,callback):
        fping_probe_socket=FPingProbeSocket(self.factory,self.config.get("path","fping"),addresses,callback)
    ##
    ##
    ##
    def check_event_source(self,address):
        return address in self.event_sources
        
    ##
    ## Main event loop
    ##
    def run(self):
        self.factory.run(run_forever=True)
    ##
    def tick(self):
        t=time.time()
        # Request filter updates
        if self.get_state()=="ESTABLISHED" and self.next_filter_update and t>self.next_filter_update:
            self.get_event_filter()
        # Check for pending crashinfos
        if self.stand_alone_mode  and self.get_state()=="ESTABLISHED" and self.next_crashinfo_check and t>self.next_crashinfo_check:
            self.check_crashinfo()
        # Perform delayed calls
        while not self.script_call_queue.empty():
            try:
                f,args,kwargs=self.script_call_queue.get_nowait()
            except:
                break
            logging.debug("Calling delayed %s(*%s,**%s)"%(f,args,kwargs))
            apply(f,args,kwargs)
        # Send collected PM data
        if self.get_state()=="ESTABLISHED" and self.pm_data_queue:
            self.send_pm_data()
        # Cancel stale scripts
        if self.get_state()=="ESTABLISHED":
            self.cancel_stale_scripts()
        # Heartbeat when necessary
        if self.heartbeat_enable and (self.next_heartbeat is None or self.next_heartbeat<=t):
            self.heartbeat()
            self.next_heartbeat=t+3
        # Perform default daemon/fsm machinery
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
        r.name=self.activator_name
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
            self.event_sources=set(response.sources)
            logging.debug("Setting event source filter to: %s"%str(self.event_sources))
            self.next_filter_update=time.time()+response.expire
        logging.info("Requesting event source filter")
        r=EventFilterRequest()
        self.sae_stream.proxy.event_filter(r,event_filter_callback)
    ##
    ## Collect crashinfo files and send them as system events to SAE
    ## (Called only in standalone mode)
    ##
    @check_state("ESTABLISHED")
    def check_crashinfo(self):
        if not self.config.get("main","logfile"):
            return
        c_d=os.path.dirname(self.config.get("main","logfile"))
        if not os.path.isdir(c_d):
            return
        for fn in [fn for fn in os.listdir(c_d) if fn.startswith(DEBUG_CTX_CRASH_PREFIX)]:
            # Load and unpickle crashinfo
            path=os.path.join(c_d,fn)
            f=open(path)
            data=f.read()
            f.close()
            data=cPickle.loads(data)
            ts=data["ts"]
            del data["ts"]
            # Send event. "" is an virtual address of ROOT object
            self.on_event(ts,"",data)
            os.unlink(path)
        # Next check - after 60 seconds timeout
        self.next_crashinfo_check=time.time()+60
        
    ##
    ## Send FM event to SAE
    ##
    def on_event(self,timestamp,ip,body):
        def on_event_callback(transaction,response=None,error=None):
            if error:
                logging.error("event_proxy failed: %s"%error)
        r=EventRequest()
        r.timestamp=timestamp
        r.ip=ip
        for k,v in body.items():
            i=r.body.add()
            i.key=str(k)
            i.value=str(v)
        self.sae_stream.proxy.event(r,on_event_callback)
    ##
    ##
    ##
    def queue_pm_data(self,pm_data):
        self.pm_data_queue+=pm_data
    ##
    ##
    ##
    def queue_pm_result(self,pm_result):
        self.pm_result_queue+=pm_result
    ##
    ## Send collected PM data to the SAE
    ##
    def send_pm_data(self):
        def pm_data_callback(transaction,response=None,error=None):
            if error:
                logging.error("pm_data failed: %s"%error)
        r=PMDataRequest()
        for probe_name,probe_type,timestamp,service,result,message in self.pm_result_queue:
            d=r.result.add()
            d.probe_name=probe_name
            d.probe_type=probe_type
            d.timestamp=timestamp
            d.service=service
            d.result=result
            d.message=message
        self.pm_result_queue=[]
        for name,timestamp,is_null,value in self.pm_data_queue:
            d=r.data.add()
            d.name=name
            d.timestamp=timestamp
            d.is_null=is_null
            d.value=value
        self.pm_data_queue=[]
        self.sae_stream.proxy.pm_data(r,pm_data_callback)
    ##
    ## Cancel stale scripts
    ##
    @check_state("ESTABLISHED")
    def cancel_stale_scripts(self):
        to_cancel=[st for st in self.script_threads.keys() if st.is_stale()]
        for script in to_cancel:
            logging.info("Canceling stale script %s(%s)"%(script.name,script.access_profile.address))
            st.cancel_script()
        
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
