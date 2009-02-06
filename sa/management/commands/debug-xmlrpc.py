# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from xmlrpclib import ServerProxy, Error
import ConfigParser

defaults_config_path="etc/%(daemon_name)s.defaults"

class Command(BaseCommand):
    help="Debug SAE XML-RPC server"
    def handle(self, *args, **options):
        config=ConfigParser.SafeConfigParser()
        for p in ["etc/noc-sae.defaults","etc/noc-sae.conf"]:
            config.read(p)
        server=ServerProxy("http://%s:%d"%(config.get("xmlrpc","listen"),config.getint("xmlrpc","port")))
        proxy=getattr(server,args[0])
        print proxy(*args[1:])
        
