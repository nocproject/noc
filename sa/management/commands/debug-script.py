# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Usage: debug-script <profile> <script> <stream-url>
##
## WARNING!!!
## This module implements part of activator functionality.
## Sometimes via dirty hacks
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from noc.sa.profiles import profile_registry
from noc.sa.script import script_registry,scheme_id
from noc.sa.activator import Service,ServersHub
from noc.sa.protocols.sae_pb2 import *
from noc.sa.rpc import TransactionFactory
import logging,sys,ConfigParser,Queue,time,cPickle,threading,signal,os
from noc.lib.url import URL
from noc.lib.nbsocket import SocketFactory
from optparse import OptionParser, make_option

class Controller(object): pass

##
## Activator emulation
##
class ActivatorStub(object):
    def __init__(self):
        # Simple config stub
        self.config=ConfigParser.SafeConfigParser()
        self.config.read("etc/noc-activator.defaults")
        self.config.read("etc/noc-activator.conf")
        self.script_call_queue=Queue.Queue()
        self.ping_check_results=None
        self.factory=SocketFactory(tick_callback=self.tick)
        self.to_exit=False
        self.servers=ServersHub(self)
        self.log_cli_sessions=None
    
    def tick(self):
        logging.debug("Tick")
        while not self.script_call_queue.empty():
            try:
                f,args,kwargs=self.script_call_queue.get_nowait()
            except:
                break
            logging.debug("Calling delayed %s(*%s,**%s)"%(f,args,kwargs))
            apply(f,args,kwargs)
        x=len(self.factory.sockets)==0
        if x and self.to_exit:
            logging.debug("EXIT")
            os._exit(0)
        elif x:
            self.to_exit=True
        
    def on_script_exit(self,script):
        if script.parent is None:
            self.servers.close()
        
    def run_script(self,_script_name,access_profile,callback,**kwargs):
        pv,pos,sn=_script_name.split(".",2)
        profile=profile_registry["%s.%s"%(pv,pos)]()
        script=script_registry[_script_name](profile,self,access_profile,**kwargs)
        script.start()
    
    def request_call(self,f,*args,**kwargs):
        logging.debug("Requesting call: %s(*%s,**%s)"%(f,args,kwargs))
        self.script_call_queue.put((f,args,kwargs))
    
    def can_run_script(self):
        return True

class Command(BaseCommand):
    help="Debug SA Script"
    option_list=BaseCommand.option_list+(
        make_option("-c","--read-community",dest="snmp_ro"),
    )
    def run_script(self,service,request):
        def handle_callback(controller,response=None,error=None):
            if error:
                logging.debug("Error: %s"%error.text)
            if response:
                logging.debug("Script completed")
                logging.debug(response.config)
        logging.debug("Running script thread")
        controller=Controller()
        tf=TransactionFactory()
        controller.transaction=tf.begin()
        service.script(controller=controller,request=request,done=handle_callback)
    
    def SIGINT(self,signo,frame):
        logging.info("SIGINT")
        os._exit(0)
        
    def handle(self, *args, **options):
        if len(args)<2:
            print "Usage: debug-script <script> <stream url> [key1=value1 key2=value2 ... ]"
            print "Where value is valid python expression"
            return
        script_name=args[0]
        vendor,os_name,rest=script_name.split(".",2)
        profile_name="%s.%s"%(vendor,os_name)
        try:
            profile=profile_registry[profile_name]()
        except:
            print "Invalid profile. Available profiles are:"
            print "\n".join([x[0] for x in profile_registry.choices])
            return
        try:
            script_class=script_registry[script_name]
        except:
            print "Invalid script. Available scripts are:"
            print "\n".join([x[0] for x in script_registry.choices])
            return
        logging.root.setLevel(logging.DEBUG)
        signal.signal(signal.SIGINT,self.SIGINT)
        service=Service()
        service.activator=ActivatorStub()
        url=URL(args[1])
        r=ScriptRequest()
        r.script=script_name
        r.access_profile.profile        = profile_name
        r.access_profile.scheme         = scheme_id[url.scheme]
        r.access_profile.address        = url.host
        if url.port:
            r.access_profile.port       = url.port
        r.access_profile.user           = url.user
        if "\x00" in url.password: # Check the password really the pair of password/enable password
            p,s=url.password.split("\x00",1)
            r.access_profile.password   = p
            r.access_profile.super_password = s
        else:
            r.access_profile.password   = url.password
        r.access_profile.path           = url.path
        if options["snmp_ro"]:
            r.access_profile.snmp_ro=options["snmp_ro"]
        # Parse script args
        if len(args)>=3:
            for p in args[2:]:
                k,v=p.split("=",1)
                v=eval(v,{},{})
                a=r.kwargs.add()
                a.key=k
                a.value=cPickle.dumps(v)
        #
        t=threading.Thread(target=self.run_script,args=(service,r,))
        t.start()
        #
        service.activator.factory.run(run_forever=True)
