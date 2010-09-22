# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dump existing script tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from django.core.management.base import BaseCommand
from noc.lib.test import ScriptTestCase
import os,types

class Command(BaseCommand):
    help="Dump script tests data"
    def get_tests(self,root=None):
        p=os.path.join("sa","profiles")
        if root:
            for n in root.split("."):
                p=os.path.join(p,n)
        for dirpath,dirnames,files in os.walk(p):
            parts=dirpath.split(os.sep)
            if parts[-1]=="tests":
                for f in [f for f in files if f.endswith(".py") and not f.startswith(".") and f!="__init__.py"]:
                    fp=os.path.join(dirpath,f)
                    m=__import__("noc."+fp[:-2].replace(os.sep,"."),{},{},"*")
                    for n in dir(m):
                        o=getattr(m,n)
                        if type(o)==types.TypeType and issubclass(o,ScriptTestCase) and o!=ScriptTestCase:
                            yield o
    
    def display(self,tests):
        r={} # Profile -> script -> platform -> version
        for t in tests:
            v,o,s=t.script.split(".")
            profile="%s.%s"%(v,o)
            if profile not in r:
                r[profile]={}
            if s not in r[profile]:
                r[profile][s]={}
            if t.platform not in r[profile][s]:
                r[profile][s][t.platform]=set()
            r[profile][s][t.platform].add((t.version,len(t.snmp_get) or len(t.snmp_getnext)))
        #
        for profile in sorted(r.keys()):
            print profile
            print "="*(len(profile))
            for script in sorted(r[profile].keys()):
                print "    "+script
                print "    "+"-"*len(script)
                for platform in sorted(r[profile][script].keys()):
                    print "        "+platform+":"
                    versions=r[profile][script][platform]
                    print "            "+", ".join([(v+" [S]" if snmp else v) for v,snmp in versions])
            
    def handle(self, *args, **options):
        if len(args)>0:
            root=args[0]
        else:
            root=None
        self.display(self.get_tests())
