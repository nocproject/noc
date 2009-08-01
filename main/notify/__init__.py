# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-notifier plugins
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.registry import Registry
from noc.lib.debug import error_report
import Queue,logging,datetime
##
## NotifyRegistry
##
class NotifyRegistry(Registry):
    name="NotifyRegistry"
    subdir="notify"
    classname="Notify"
    apps=["noc.main"]
notify_registry=NotifyRegistry()
##
## Notify Metaclass
##
class NotifyBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        notify_registry.register(m.name,m)
        return m
##
## Notify Base Class
##
class Notify(object):
    __metaclass__=NotifyBase
    name=None
    
    def __init__(self,parent):
        self.info("Initializing")
        self.parent=parent
        self.task_queue=Queue.Queue()
        self.max_queue_size=self.config.getint(self.name,"queue_size")
        self.ttl=datetime.timedelta(seconds=self.config.getint(self.name,"time_to_live"))
        self.retry_interval=datetime.timedelta(seconds=self.config.getint(self.name,"retry_interval"))
    
    def _config(self):
        return self.parent.config
    config=property(_config)
    
    def debug(self,message):
        logging.debug("[%s] %s"%(self.name,message))
    
    def info(self,message):
        logging.info("[%s] %s"%(self.name,message))
    
    def error(self,message):
        logging.error("[%s] %s"%(self.name,message))
    ##
    ## Has the task queue free space?
    ##
    def can_queue(self):
        return self.task_queue.qsize()<self.max_queue_size
    ##
    ## Called by daemon to spool new task
    ##
    def new_task(self,task_id,params,subject,body,link=None):
        self.task_queue.put((task_id,params,subject,body,link))
    ##
    ## Worker loop, executed in separate thread
    ##
    def run(self):
        while True:
            task_id,params,subject,body,link=self.task_queue.get()
            self.info("New task: %d"%task_id)
            try:
                status=self.send_message(params,subject,body,link)
            except:
                error_report()
                self.parent.on_task_complete(task_id,False)
            self.info("Task id completed with status %s"%status)
            if status:
                self.parent.on_task_complete(task_id,status)
            else:
                self.parent.on_task_complete(task_id,status,next_try=datetime.datetime.now()+self.retry_interval)
    ##
    ## send message.
    ## Overloaded by notification plugins
    ##
    def send_message(self,params,subject,body,link=None):
        return True
