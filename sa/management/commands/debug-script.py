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
from noc.sa.activator import Service
from noc.sa.protocols.sae_pb2 import *
from noc.sa.rpc import TransactionFactory
import logging,sys,ConfigParser,Queue,time
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
        self.config.add_section("activator")
        self.config.set("activator","max_pull_config","2")
        self.script_call_queue=Queue.Queue()
    
    def tick(self):
        while not self.script_call_queue.empty():
            try:
                f,args,kwargs=self.script_call_queue.get_nowait()
            except:
                break
            logging.debug("Calling delayed %s(*%s,**%s)"%(f,args,kwargs))
            apply(f,args,kwargs)
        
    def on_script_exit(self,script):
        pass
        
    def run_script(self,name,access_profile,callback,**kwargs):
        pv,pos,sn=name.split(".",2)
        profile=profile_registry["%s.%s"%(pv,pos)]()
        script=script_registry[name](profile,self,access_profile,**kwargs)
        script.start()
    
    def request_call(self,f,*args,**kwargs):
        logging.debug("Requesting call: %s(*%s,**%s)"%(f,args,kwargs))
        self.script_call_queue.put((f,args,kwargs))

class Command(BaseCommand):
    help="Debug SA Script"
    option_list=BaseCommand.option_list+(
        make_option("-c","--read-community",dest="snmp_ro"),
    )
    def handle(self, *args, **options):
        def handle_callback(controller,response=None,error=None):
            if error:
                logging.debug("Error: %s"%error.text)
            if response:
                logging.debug("Config pulled")
                logging.debug(response.config)
        if len(args) not in [2,3]:
            print "Usage: debug-script <script> <stream url> [key1=value1,....,keyN=valueN]"
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
        service=Service()
        service.activator=ActivatorStub()
        service.activator.factory=SocketFactory(tick_callback=service.activator.tick)
        url=URL(args[1])
        r=ScriptRequest()
        r.script=script_name
        r.access_profile.profile        = profile_name
        r.access_profile.scheme         = scheme_id[url.scheme]
        r.access_profile.address        = url.host
        if url.port:
            r.access_profile.port       = url.port
        r.access_profile.user           = url.user
        if "/" in url.password:
            p,s=url.password.split("/",1)
            r.access_profile.password   = p
            r.access_profile.super_password = s
        else:
            r.access_profile.password   = url.password
        r.access_profile.path           = url.path
        if options["snmp_ro"]:
            r.access_profile.snmp_ro=options["snmp_ro"]
        # Parse script args
        if len(args)==3:
            for p in args[2].split(","):
                k,v=p.strip().split("=")
                a=r.kwargs.add()
                a.key=k
                a.value=v
        #
        controller=Controller()
        tf=TransactionFactory()
        controller.transaction=tf.begin()
        service.script(controller=controller,request=r,done=handle_callback)
        service.activator.factory.run()
        service.activator.factory.tick_callback()
