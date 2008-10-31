## 
## Usage: debug-profile <profile> <stream-url>
##
from django.core.management.base import BaseCommand
from noc.sa.profiles import profile_registry
from noc.sa.actions import get_action_class
from noc.sa.activator import STREAMS
import asyncore,logging,sys
from noc.sa.protocols.sae_pb2 import AccessProfile
from noc.lib.url import URL

class Command(BaseCommand):
    help="Debug Profile"
    def handle(self, *args, **options):
        if len(args)!=2:
            print "Usage: debug-profile <profile> <stream url>"
            return
        try:
            self.profile=profile_registry[args[0]]()
        except:
            print "Invalid profile. Available profiles are:"
            print "\n".join([x[0] for x in profile_registry.choices])
            return
        logging.root.setLevel(logging.DEBUG)
        url=URL(args[1])
        ap=AccessProfile()
        ap.scheme={"telnet":0,"ssh":1}[url.scheme]
        ap.address=url.host
        if url.port:
            ap.port=int(url.port)
        ap.user=url.user
        ap.password=url.password
        if url.path:
            ap.path=url.path
        self.stream=STREAMS[ap.scheme](ap)
        action=get_action_class("sa.actions.cli")(transaction_id=1,
            stream=self.stream,
            profile=self.profile,
            callback=self.on_pull_config,
            args={
                "user"     : ap.user,
                "password" : ap.password,
                "commands" : self.profile.command_pull_config,
                })
        asyncore.loop()
    def on_action_close(self,action,status):
        logging.debug("Complete with status: %s"%status)
        self.stream.close()
    def on_pull_config(self,action):
        logging.debug("Config pulled")
        logging.debug(self.profile.cleaned_config(action.result))
