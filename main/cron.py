##
##
##
from noc.main.periodic import periodic_registry
from noc.main.models import TaskSchedule
import threading,logging,time,datetime

class CronDaemon(object):
    def __init__(self):
        self.active_tasks={}
        self.task_lock=threading.Lock()
        
    def execute_wrapper(self,task):
        logging.info(u"Executing %s"%unicode(task))
        status=task.periodic_class().execute()
        logging.info(u"Task %s is terminated with '%s'"%(unicode(task),status))
        task.next_run=datetime.datetime.now()+datetime.timedelta(seconds=task.run_every)
        task.save()
        self.task_lock.acquire()
        try:
            del self.active_tasks[task.id]
        finally:
            self.task_lock.release()
        
    def run_task(self,task):
        logging.debug(u"New task running: %s"%unicode(task))
        t=threading.Thread(name=task.periodic_name,target=self.execute_wrapper,kwargs={"task":task})
        self.task_lock.acquire()
        self.active_tasks[task.id]=t
        self.task_lock.release()
        t.start()
        
    def run(self):
        while True:
            self.task_lock.acquire()
            tasks = TaskSchedule.get_pending_tasks(exclude=self.active_tasks.keys())
            self.task_lock.release()
            if tasks:
                for t in tasks:
                    self.run_task(t)
            else:
                st=TaskSchedule.sleep_timeout(exclude=self.active_tasks.keys())
                if not st:
                    st=0x7FFFFFFF
                st=min(20,st)
                time.sleep(st)