import os,asyncore,logging,signal,cPickle,sys,traceback
from noc.sa.stream import Stream
from noc.sa.profiles import get_profile_class
from noc.sa.actions import get_action_class
import settings
import psycopg2

class Supervisor(object):
    def __init__(self):
        self.streams={}
        logging.info("Setting signal handlers")
        signal.signal(signal.SIGCHLD,self.sig_chld)
        logging.info("Connecting to database")
        self.connect=psycopg2.connect(self.get_dsn())
        self.connect.set_isolation_level(0)
        self.query_checker=QueryChecker(self)
        self.cursor=self.get_cursor()
        self.children={}
        self.cleanup()
        logging.info("Supervisor is ready")
        
    def run(self):
        logging.info("Supervisor started")
        while 1:
            asyncore.loop(timeout=1,count=1)
        
    # Simpified and crude
    def get_dsn(self):
        v=[("dbname",settings.DATABASE_NAME),("user",settings.DATABASE_USER),("password",settings.DATABASE_PASSWORD)]
        return " ".join(["%s=%s"%tuple(x) for x in v if x[1]])

    def get_cursor(self):
        logging.debug("Creating cursor")
        return self.connect.cursor()
        
    def cleanup(self):
        logging.debug("Cleaning up")
        #self.cursor.execute("BEGIN");
        #self.cursor.execute("DELETE FROM sa_task WHERE start_time<('now'::timestamp-'24h'::interval)")
        #self.cursor.execute("COMMIT");
        
    def sig_chld(self,signum,frame):
        logging.debug("SIGCHLD caught")
        pid,status=os.waitpid(-1,os.WNOHANG)
        logging.debug("Process PID=%d is terminated with code %d"%(pid,status))
        
    def start_task(self,task_id):
        self.cursor.execute("SELECT profile,stream_url,action,args FROM sa_task WHERE task_id=%s",[task_id])
        profile,stream_url,action,args=self.cursor.fetchall()[0]
        args=cPickle.loads(args)
        logging.debug("start_task(%s,%s)"%(str(action),str(args)))
        self.cursor.execute("BEGIN")
        self.cursor.execute("UPDATE sa_task SET status='p' WHERE task_id=%s",[task_id])
        self.cursor.execute("COMMIT")
        try:
            stream=Stream.get_stream(get_profile_class(profile),stream_url)
            action=get_action_class(action)(self,task_id,stream,args)
        except:
            self.task_error(task_id,".".join(traceback.format_exception(*sys.exc_info())))

    def task_error(self,task_id,msg):
        logging.debug("Task error: task_id=%d %s"%(task_id,msg))
        self.cursor.execute("BEGIN")
        self.cursor.execute("UPDATE sa_task SET status='f',out=%s WHERE task_id=%s",[msg,id])
        self.cursor.execute("END")
        
    def feed_result(self,task_id,msg,status="p"):
        logging.debug("Feed result: task_id=%s status=%s %s"%(task_id,status,msg))
        self.cursor.execute("BEGIN")
        self.cursor.execute("UPDATE sa_task SET status=%s,out=%s WHERE task_id=%s",[status,msg,task_id])
        self.cursor.execute("END")
        
    def on_action_close(self,action,status):
        logging.debug("on_action_close(%s,%s)"%(str(action),status))
        self.feed_result(action.task_id,action.result,{True:"c",False:"f"}[status])
       

##
## QueryChecker
##
class QueryChecker(asyncore.dispatcher):
    def __init__(self,supervisor):
        asyncore.dispatcher.__init__(self)
        self.supervisor=supervisor
        self.cursor=self.supervisor.get_cursor()
        self.cursor.execute("LISTEN sa_new_task")
        self.set_socket(self.cursor)

    def handle_read(self):
        while self.cursor.isready() and len(self.cursor.connection.notifies)>0:
            pid,event=self.cursor.connection.notifies.pop()
            self.cursor.execute("SELECT task_id FROM sa_task WHERE status='n'")
            for task_id, in self.cursor.fetchall():
                self.supervisor.start_task(task_id)

    def writable(self):
        return False

    def handle_connect(self):
        pass

if __name__=="__main__":
    test()