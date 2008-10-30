##
## Service Activation Engine
##
from noc.sa.models import Activator
from noc.sa.sae_stream import SAEStream
import asyncore,socket,logging,time,threading,datetime,traceback
from noc.sa.protocols.sae_pb2 import *
from noc.sa.models import TaskSchedule

##
## Placeholder with transaction data
##
class Transaction(object):
    def __init__(self,transaction_id,object=None,stream=None):
        self.transaction_id=transaction_id
        self.object=object
        self.stream=stream
        self.started=time.time()

class Listener(asyncore.dispatcher):
    def __init__(self,sae,address,port):
        asyncore.dispatcher.__init__(self)
        self.sae=sae
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR) 
        self.bind((address,port))
        self.listen(5)
    
    def handle_accept(self):
        self.sae.on_new_connect()
        
class SAE(object):
    def __init__(self,address,port):
        self.address=address
        self.port=port
        self.streams={} # stream -> Name
        self.stream_names={} # name -> stream
        self.transactions={}
        # Periodic tasks
        self.active_periodic_tasks={}
        self.periodic_task_lock=threading.Lock()
        logging.debug("Starting listener at %s:%d"%(self.address,self.port))
        self.listener=Listener(self,self.address,self.port)
        
    def run(self):
        last_cleanup=time.time()
        last_task_check=time.time()
        while True:
            asyncore.loop(timeout=1,count=1)
            for s in self.streams:
                s.keepalive()
            if time.time()-last_task_check>10:
                self.periodic_task_lock.acquire()
                tasks = TaskSchedule.get_pending_tasks(exclude=self.active_periodic_tasks.keys())
                self.periodic_task_lock.release()
                if tasks:
                    for t in tasks:
                        self.run_periodic_task(t)
    
    def run_periodic_task(self,task):
        logging.debug(u"New task running: %s"%unicode(task))
        t=threading.Thread(name=task.periodic_name,target=self.periodic_wrapper,kwargs={"task":task})
        self.periodic_task_lock.acquire()
        self.active_periodic_tasks[task.id]=t
        self.periodic_task_lock.release()
        t.start()
    
    def periodic_wrapper(self,task):
        logging.info(u"Executing %s"%unicode(task))
        tb=None
        try:
            status=task.periodic_class(self).execute()
        except:
            tb=traceback.format_exc()
            status=False
        logging.info(u"Task %s is terminated with '%s'"%(unicode(task),status))
        if status:
            timeout=task.run_every
        else:
            timeout=max(60,task.run_every/4)
            if tb:
                logging.error("Periodic task %s failed\n%s\n"%(unicode(task),tb))
        task.next_run=datetime.datetime.now()+datetime.timedelta(seconds=timeout)
        task.save()
        self.periodic_task_lock.acquire()
        try:
            del self.active_periodic_tasks[task.id]
        finally:
            self.periodic_task_lock.release()
    
    def on_new_connect(self):
        conn,addr=self.listener.accept()
        address,port=addr
        if Activator.objects.filter(ip=address).count()==0:
            logging.error("Refusing connection from %s"%address)
            socket.close(conn)
            return
        logging.info("Connect from: %s"%address)
        s=SAEStream(self)
        s.connect_activator(conn)
        self.streams[s]=None
        
    def on_stream_close(self,stream):
        if stream not in self.streams:
            return
        name=self.streams[stream]
        if name:
            del self.stream_names[name]
        del self.streams[stream]
        
    ##
    ## Components API
    ##
    def pull_config(self,object):
        try:
            stream=self.stream_names[object.activator.name]
        except KeyError:
            raise Exception("Activator not available")
        r=ReqPullConfig()
        r.profile=object.profile_name
        r.access_profile.scheme        = object.scheme
        r.access_profile.address       = object.address
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
        t_id=stream.send_message("pull_config",request=r)
        transaction=Transaction(transaction_id=t_id,stream=stream,object=object)
        self.transactions[t_id]=transaction
    
    ##
    ## SAE Protocol Handlers
    ##
    def req_register(self,sae_stream,transaction_id,msg):
        try:
            activator=Activator.objects.get(name=msg.name)
        except Activator.DoesNotExist:
            logging.error("Unknown activator '%s'"%msg.name)
            sae_stream.send_error("register",transaction_id,"EREG","Unknown activator")
            sae_stream.close()
            return
        logging.info("Registering activator '%s'"%msg.name)
        self.streams[sae_stream]=msg.name
        self.stream_names[msg.name]=sae_stream
        r=ResRegister()
        r.version="1.0"
        sae_stream.send_message("register",transaction_id,response=r)
        
    req_register.message_class=ReqRegister
    ##
    ##
    ##
    def res_pull_config(self,sae_stream,transaction_id,msg):
        transaction=self.transactions[transaction_id]
        del self.transactions[transaction_id]
        transaction.object.write(msg.config)
    res_pull_config.message_class=ResPullConfig
        