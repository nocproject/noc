## 
## Usage: debug-profile <profile> <stream-url>
##
from django.core.management.base import BaseCommand
from noc.sa.profiles import profile_registry
from noc.sa.actions import action_registry,scheme_registry
from noc.sa.activator import Service
from noc.sa.protocols.sae_pb2 import *
from noc.sa.sae_stream import TransactionFactory
import logging,sys
from noc.lib.url import URL
from noc.lib.nbsocket import SocketFactory

class Controller(object): pass

class ActivatorStub(object): pass

class Command(BaseCommand):
    help="Debug Profile"
    def handle(self, *args, **options):
        def handle_callback(controller,response=None,error=None):
            if error:
                logging.debug("Error: %s"%error.text)
            if response:
                logging.debug("Config pulled")
                logging.debug(response.config)
        if len(args)!=2:
            print "Usage: debug-profile <profile> <stream url>"
            return
        try:
            profile=profile_registry[args[0]]()
        except:
            print "Invalid profile. Available profiles are:"
            print "\n".join([x[0] for x in profile_registry.choices])
            return
        logging.root.setLevel(logging.DEBUG)
        action_registry.register_all()
        service=Service()
        service.activator=ActivatorStub()
        service.activator.factory=SocketFactory()
        url=URL(args[1])
        r=PullConfigRequest()
        r.access_profile.profile        = args[0]
        r.access_profile.scheme         = scheme_registry.name_to_id[url.scheme]
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
        #r.access_profile.super_password = 
        r.access_profile.path           = url.path
        controller=Controller()
        tf=TransactionFactory()
        controller.transaction=tf.begin()
        service.pull_config(controller=controller,request=r,done=handle_callback)
        service.activator.factory.run()
