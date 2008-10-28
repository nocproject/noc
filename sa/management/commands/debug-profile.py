## 
## Usage: debug-profile <profile> <stream-url>
##
from django.core.management.base import BaseCommand
from noc.sa.profiles import profile_registry
from noc.sa.actions import get_action_class
from noc.sa.stream import Stream
import asyncore,logging,sys

class Command(BaseCommand):
    help="Debug Profile"
    def handle(self, *args, **options):
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
        self.stream=Stream.get_stream(profile,args[1])
        action=get_action_class("sa.actions.cli")(self,None,self.stream,{"commands":profile.command_pull_config})
        asyncore.loop()
    def on_action_close(self,action,status):
        logging.debug("Complete with status: %s"%status)
        print action.result
        self.stream.close()
