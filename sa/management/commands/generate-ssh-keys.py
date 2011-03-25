# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generate SSH keys according to config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import os
import ConfigParser
## Django modules
from django.core.management.base import BaseCommand
from optparse import OptionParser, make_option
## NOC modules
from noc.sa.script.ssh.keys import generate_pair

class Command(BaseCommand):
    help="Generate ssh keys"
    
    ##
    ## Read noc-launcher config and retrieve all activator instances configs
    ##
    def get_activator_configs(self):
        config=ConfigParser.SafeConfigParser()
        config.read("etc/noc-launcher.defaults")
        config.read("etc/noc-launcher.conf")
        return [config.get("noc-activator", c) for c in config.options("noc-activator") if c.startswith("config")]
    
    ##
    ## Returns ssh key path
    ##
    def get_ssh_key_path(self, path):
        if path.endswith(".conf"):
            d_path=path[:-5]+".defaults"
        else:
            d_path=path+".defaults"
        config=ConfigParser.SafeConfigParser()
        config.read(d_path)
        config.read(path)
        return config.get("ssh", "key")
    
    ##
    ## Create ssh keys when necessary
    ##
    def check_key(self, path):
        pub_path=path+".pub"
        if not os.path.exists(path) or not os.path.exists(pub_path):
            print "Generating RSA keys: (%s, %s)"%(path, pub_path)
            generate_pair(path)
    
    ##
    ##
    def handle(self, *args, **options):
        paths=set([self.get_ssh_key_path(c) for c in self.get_activator_configs()])
        for path in paths:
            self.check_key(path)
    
