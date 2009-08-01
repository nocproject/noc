# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-notifier daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.db import transaction,reset_queries
from django.db.models import Q
from noc.lib.daemon import Daemon
from noc.main.models import Notification
from noc.main.notify import notify_registry
import logging, threading, time, datetime
##
notify_registry.register_all()
##
## noc-notifier daemon
##
class Notifier(Daemon):
    daemon_name="noc-notifier"
    def __init__(self):
        self.notifiers={}     # Name -> Notifier mappings
        super(Notifier,self).__init__()
        logging.info("Running Notifier")
        self.in_process=set() # Currently processed IDs
        self.in_process_lock=threading.Lock()
        self.completed_tasks=[] # A list of completed task ids
        self.retry_tasks=[]     # A list of (task_id,next_try)
        self.queue_check_interval=self.config.getint("notifier","queue_check_interval")
        
    def load_config(self):
        super(Notifier,self).load_config()
        for name,cls in notify_registry.classes.items():
            if self.config.has_section(name) and self.config.getboolean(name,"enabled"):
                if name not in self.notifiers:
                    self.run_notifier(name)
                
    def run_notifier(self,name):
        self.notifiers[name]=notify_registry[name](self)
        threading.Thread(name=name,target=self.notifiers[name].run).start()
        
    def run(self):
        transaction.enter_transaction_management()
        while True:
            reset_queries()
            time.sleep(self.queue_check_interval) # Wait
            now=datetime.datetime.now()
            # Flush out expired tasks
            q=Notification.objects.filter(actual_till__lt=now)
            if self.in_process:
                with self.in_process_lock:
                    q=q.exclude(id__in=list(self.in_process))
            ftl=[t.id for t in q]
            if ftl:
                logging.debug("Flushing expired tasks: %s"%(str(ftl)))
                q.delete()
            transaction.commit()
            with self.in_process_lock:
                # Schedule task retries
                if self.retry_tasks:
                    for task_id,next_try in self.retry_tasks:
                        try:
                            n=Notification.objects.get(id=task_id)
                        except Notification.DoesNotExist:
                            continue
                        logging.debug("Sheduling task %d to retry at %s"%(task_id,next_try))
                        n.next_try=next_try
                        n.save()
                    self.retry_tasks=[]
                    transaction.commit()
                # Remove scheduled tasks
                if self.completed_tasks:
                    logging.debug("Purging completed tasks: %s"%str(self.completed_tasks))
                    Notification.objects.filter(id__in=self.completed_tasks).delete()
                    self.completed_tasks=[]
                    transaction.commit()
                # Look for new tasks
                q=Notification.objects.filter(Q(next_try__isnull=True)|Q(next_try__lte=now))
                q=q.filter(notification_method__in=self.notifiers.keys()) # Look up tasks for active plugins only
                # Build a list of busy workers
                busy_workers=[n.name for n in self.notifiers.values() if not n.can_queue()]
                if busy_workers: # Exclude tasks for busy workers
                    q=q.exclude(notification_method__in=busy_workers)
                    logging.debug("Busy workers: %s"%str(busy_workers))
                if self.in_process: # Exclude task in process
                    q=q.exclude(id__in=list(self.in_process))
                for t in q.order_by("next_try"):
                    m=t.notification_method
                    if m in busy_workers: # Do not queue task to the busy workers
                        continue
                    if not self.notifiers[m].can_queue(): # Detect worker became busy
                        busy_workers+=[m]
                        continue
                    if t.actual_till is None: # Set up actual till if necessary
                        t.actual_till=now+self.notifiers[m].ttl
                        t.save()
                    self.notifiers[m].new_task(t.id,t.notification_params,t.subject,t.body,t.link)
                    self.in_process.add(t.id)
            transaction.commit()
        transaction.leave_transaction_management()
    ##
    ## Executed from concurrent thread
    ##
    def on_task_complete(self,task_id,status,next_try=None):
        with self.in_process_lock:
            self.in_process.remove(task_id)
            if status: # Schedule task for removal
                self.completed_tasks+=[task_id]
            else: # Schedule task for retry
                self.retry_tasks+=[(task_id,next_try)]
        