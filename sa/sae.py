##
## Service Activation Engine
##
from noc.sa.models import Activator
from noc.cm.models import Config

from noc.sa.rpc import RPCSocket,file_hash,get_digest,get_nonce
import logging,time,threading,datetime,os,sets,random
from noc.sa.protocols.sae_pb2 import *
from noc.sa.models import TaskSchedule
from noc.lib.fileutils import read_file
from noc.lib.daemon import Daemon
from noc.lib.debug import error_report
from noc.lib.nbsocket import ListenTCPSocket,AcceptedTCPSocket,SocketFactory

##
## Additions to MANIFEST-ACTIVATOR file
##
ACTIVATOR_MANIFEST=[
    "sa/profiles/",
]

##
##
##
class Service(SAEService):
    def get_controller_activator(self,controller):
        return Activator.objects.get(name=self.sae.factory.get_name_by_socket(controller.stream))
    ##
    ## RPC interfaces
    ##
    def ping(self,controller,request,done):
        done(controller,response=PingResponse())
        
    def register(self,controller,request,done):
        try:
            activator=Activator.objects.get(name=request.name)
        except Activator.DoesNotExist:
            logging.error("Unknown activator '%s'"%request.name)
            e=Error()
            e.code=ERR_UNKNOWN_ACTIVATOR
            e.text="Unknown activator '%s'"%request.name
            done(controller,error=e)
            return
        logging.info("Requesting digest for activator '%s'"%request.name)
        r=RegisterResponse()
        r.nonce=get_nonce()
        controller.stream.nonce=r.nonce
        done(controller,response=r)
        
    def auth(self,controller,request,done):
        try:
            activator=Activator.objects.get(name=request.name)
        except Activator.DoesNotExist:
            logging.error("Unknown activator '%s'"%request.name)
            e=Error()
            e.code=ERR_UNKNOWN_ACTIVATOR
            e.text="Unknown activator '%s'"%request.name
            done(controller,error=e)
            return
        logging.info("Authenticating activator '%s'"%request.name)
        if controller.stream.nonce is None or get_digest(request.name,activator.auth,controller.stream.nonce)!=request.digest:
            e=Error()
            e.code=ERR_AUTH_FAILED
            e.text="Authencication failed for activator '%s'"%request.name
            done(controller,error=e)
            return
        r=AuthResponse()
        controller.stream.set_name(request.name)
        controller.stream.is_authenticated=True
        done(controller,response=r)
        
    def manifest(self,controller,request,done):
        if not controller.stream.is_authenticated:
            e=Error()
            e.code=ERR_AUTH_REQUIRED
            e.text="Authentication required"
            done(controller,error=e)
            return
        done(controller,response=self.sae.activator_manifest)
        
    def software_upgrade(self,controller,request,done):
        if not controller.stream.is_authenticated:
            e=Error()
            e.code=ERR_AUTH_REQUIRED
            e.text="Authentication required"
            done(controller,error=e)
            return
        r=SoftwareUpgradeResponse()
        for n in request.names:
            if n not in self.sae.activator_manifest_files:
                e=Error()
                e.code=ERR_INVALID_UPGRADE
                e.text="Invalid file requested for upgrade: %s"%n
                done(controller,error=e)
                return
            u=r.codes.add()
            u.name=n
            u.code=read_file(n)
        done(controller,response=r)
        
    def event_filter(self,controller,request,done):
        if not controller.stream.is_authenticated:
            e=Error()
            e.code=ERR_AUTH_REQUIRED
            e.text="Authentication required"
            done(controller,error=e)
            return
        activator=self.get_controller_activator(controller)
        r=EventFilterResponse()
        r.expire=self.sae.config.getint("sae","refresh_event_filter")
        sources=list(request.sources)
        for c in Config.objects.filter(activator=activator,trap_source_ip__isnull=False):
            profile=c.profile
            if ES_SNMP_TRAP in sources:
                if profile.oid_trap_config_changed:
                    f=r.filters.add()
                    f.source=ES_SNMP_TRAP
                    f.ip=c.trap_source_ip
                    f.mask=profile.oid_trap_config_changed
                    f.action=EA_CONFIG_CHANGED
                f=r.filters.add()
                f.source=ES_SNMP_TRAP
                f.ip=c.trap_source_ip
                f.mask=".*"
                f.action=EA_PROXY
            if ES_SYSLOG in sources:
                if profile.syslog_config_changed:
                    f=r.filters.add()
                    f.source=ES_SYSLOG
                    f.ip=c.trap_source_ip
                    f.mask=profile.syslog_config_changed
                    f.action=EA_CONFIG_CHANGED
                f=r.filters.add()
                f.source=ES_SYSLOG
                f.ip=c.trap_source_ip
                f.mask=".*"
                f.action=EA_PROXY
        done(controller,response=r)
        
    def event_proxy(self,controller,request,done):
        if not controller.stream.is_authenticated:
            e=Error()
            e.code=ERR_AUTH_REQUIRED
            e.text="Authentication required"
            done(controller,error=e)
            return
        activator=self.get_controller_activator(controller)
        try:
            c=Config.objects.get(activator=activator,trap_source_ip=request.ip)
        except Config.DoesNotExist:
            e=Error()
            e.code=ERR_UNKNOWN_EVENT_SOURCE
            e.text="Unknown event source '%s'"%request.ip
            done(controller,error=e)
            return
        logging.info("event from: %s: %s"%(c.repo_path,repr(request.message)))
        done(controller,EventResponse())
    
    def event_config_changed(self,controller,request,done):
        if not controller.stream.is_authenticated:
            e=Error()
            e.code=ERR_AUTH_REQUIRED
            e.text="Authentication required"
            done(controller,error=e)
            return
        activator=self.get_controller_activator(controller)
        try:
            c=Config.objects.get(activator=activator,trap_source_ip=request.ip)
        except Config.DoesNotExist:
            e=Error()
            e.code=ERR_UNKNOWN_EVENT_SOURCE
            e.text="Unknown event source '%s'"%request.ip
            done(controller,error=e)
            return
        logging.info("%s configuration changed"%(c.repo_path))
        c.next_pull=min(c.next_pull,datetime.datetime.now()+datetime.timedelta(minutes=10))
        c.save()
        done(controller,EventResponse())

##
## AcceptedTCPSocket with RPC Protocol
##
class SAESocket(RPCSocket,AcceptedTCPSocket):
    def __init__(self,factory,socket):
        AcceptedTCPSocket.__init__(self,factory,socket)
        RPCSocket.__init__(self,factory.sae.service)
        self.nonce=None
        self.is_authenticated=True

##
## SAE Supervisor
##
class SAE(Daemon):
    daemon_name="noc-sae"
    def __init__(self):
        Daemon.__init__(self)
        logging.info("Running SAE")
        #
        self.service=Service()
        self.service.sae=self
        #
        self.factory=SocketFactory()
        self.factory.sae=self
        self.factory.check_access=self.check_activator_access
        
        # Periodic tasks
        self.active_periodic_tasks={}
        self.periodic_task_lock=threading.Lock()
        #
        self.activator_manifest=None
        self.activator_manifest_files=None
    
    def build_manifest(self):
        logging.info("Building manifest")
        manifest=read_file("MANIFEST-ACTIVATOR").split("\n")+ACTIVATOR_MANIFEST
        manifest=[x.strip() for x in manifest if x]
        self.activator_manifest=ManifestResponse()
        self.activator_manifest_files=sets.Set()
        
        files=sets.Set()
        for f in manifest:
            if f.endswith("/"):
                for dirpath,dirnames,filenames in os.walk(f):
                    for f in [f for f in filenames if f.endswith(".py")]:
                        files.add(os.path.join(dirpath,f))
            else:
                files.add(f)
        for f in files:
            self.activator_manifest_files.add(f)
            cs=self.activator_manifest.files.add()
            cs.name=f
            cs.hash=file_hash(f)

    def run(self):
        self.build_manifest()
        logging.info("Starting listener at %s:%d"%(self.config.get("sae","listen"),self.config.getint("sae","port")))
        self.factory.listen_tcp(self.config.get("sae","listen"),self.config.getint("sae","port"),SAESocket)
        
        last_cleanup=time.time()
        last_task_check=time.time()
        while True:
            self.factory.loop(1)
            if time.time()-last_task_check>10:
                self.periodic_task_lock.acquire()
                tasks = TaskSchedule.get_pending_tasks(exclude=self.active_periodic_tasks.keys())
                self.periodic_task_lock.release()
                if tasks:
                    for t in tasks:
                        self.run_periodic_task(t)
    ##
    ## Periodic tasks
    ##
    def run_periodic_task(self,task):
        logging.debug(u"New task running: %s"%unicode(task))
        t=threading.Thread(name=task.periodic_name,target=self.periodic_wrapper,kwargs={"task":task})
        self.periodic_task_lock.acquire()
        self.active_periodic_tasks[task.id]=t
        self.periodic_task_lock.release()
        t.start()
    
    def periodic_wrapper(self,task):
        logging.info(u"Executing %s"%unicode(task))
        cwd=os.getcwd()
        try:
            status=task.periodic_class(self).execute()
        except:
            error_report()
            status=False
        logging.info(u"Task %s is terminated with '%s'"%(unicode(task),status))
        if status:
            timeout=task.run_every
        else:
            timeout=max(60,task.run_every/4)
        task.next_run=datetime.datetime.now()+datetime.timedelta(seconds=timeout)
        task.save()
        self.periodic_task_lock.acquire()
        try:
            del self.active_periodic_tasks[task.id]
        finally:
            self.periodic_task_lock.release()
        new_cwd=os.getcwd()
        if cwd!=new_cwd:
            logging.error("CWD changed by periodic '%s' ('%s' -> '%s'). Restoring old cwd"%(unicode(task),cwd,new_cwd))
            os.chdir(cwd)
    ##
    def check_activator_access(self,address):
        return Activator.objects.filter(ip=address).count()>0
        
    def on_stream_close(self,stream):
        self.streams.unregister(stream)
        
    def register_activator(self,name,stream):
        self.streams.register(stream,name)
        
    def get_activator_stream(self,name):
        try:
            return self.factory.get_socket_by_name(name)
        except KeyError:
            raise Exception("Activator not available: %s"%name)
    
    def script(self,object,name,callback,*args,**kwargs):
        def script_callback(transaction,response=None,error=None):
            if error:
                logging.error("script(%s,*%s,**%s) failed: %s"%(name,args,kwargs,error.text))
                callback(error=error)
                return
            result=response.result
            callback(result=result)
        stream=self.get_activator_stream(object.activator.name)
        r=ScriptRequest()
        r.script=name
        r.access_profile.profile           = object.profile_name
        r.access_profile.scheme            = object.scheme
        r.access_profile.address           = object.address
        if object.port:
            r.access_profile.port          = object.port
        if object.user:
            r.access_profile.user          = object.user
        if object.password:
            r.access_profile.password      = object.password
        if object.super_password:
            r.access_profile.super_password= object.super_password
        if object.remote_path:
            r.access_profile.path          = object.remote_path
        stream.proxy.script(r,script_callback)
    # Signal handlers

    # SIGUSR1 returns process info
    def SIGUSR1(self,signo,frame):
        s=[
            ["factory.sockets",len(self.factory)],
        ]
        logging.info("STATS:")
        for n,v in s:
            logging.info("%s: %s"%(n,v))
        for sock in [s for s in self.factory.sockets.values() if issubclass(s.__class__,RPCSocket)]:
            try:
                logging.info("Activator: %s"%self.factory.get_name_by_socket(sock))
            except KeyError:
                logging.info("Unregistred activator")
            for n,v in sock.stats:
                logging.info("%s: %s"%(n,v))