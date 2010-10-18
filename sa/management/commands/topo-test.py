# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Topology discovery debug
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from django.core.management.base import BaseCommand
from optparse import OptionParser, make_option
from noc.sa.apps.topologydiscovery.topology import TopologyDiscovery
import cPickle

class Command(BaseCommand):
    help="Run topology discovery test"
    option_list=BaseCommand.option_list+(
        make_option("-m","--mac",dest="mac",action="store_true"),
        make_option("-p","--pvst",dest="pvst",action="store_true"),
        make_option("-a","--arp",dest="arp",action="store_true"),
        make_option("-l","--lldp",dest="lldp",action="store_true"),
        make_option("-c","--cdp",dest="cdp",action="store_true"),
        make_option("-s","--stp",dest="stp",action="store_true")
    )
    def _usage(self):
        print "manage.py topo-test [--mac] [--pvst] [--lldp] <datafile>"
        sys.exit(1)
        
    def handle(self, *args, **options):
        with open(args[0]) as f:
            data=cPickle.load(f)
        td=TopologyDiscovery(data=data,mac=options["mac"],per_vlan_mac=options["pvst"],arp=options["arp"],
            lldp=options["lldp"],cdp=options["cdp"],stp=options["stp"])
        print "Writting topology into /tmp/topo.dot"
        with open("/tmp/topo.dot","w") as f:
            f.write(td.dot())
