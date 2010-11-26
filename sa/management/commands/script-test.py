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
import os,types,sys
from optparse import OptionParser, make_option

class Command(BaseCommand):
    help="Dump script tests data"
    option_list=BaseCommand.option_list+(
        make_option("-u","--untested",dest="untested",action="store_true"),
    )
    
    def get_tests(self,filter):
        for dirpath,dirnames,files in os.walk(os.path.join("sa","profiles")):
            parts=dirpath.split(os.sep)
            if parts[-1]=="tests":
                for f in [f for f in files if f.endswith(".py") and not f.startswith(".") and f!="__init__.py"]:
                    fp=os.path.join(dirpath,f)
                    m=__import__("noc."+fp[:-2].replace(os.sep,"."),{},{},"*")
                    for n in dir(m):
                        o=getattr(m,n)
                        if type(o)==types.TypeType and issubclass(o,ScriptTestCase) and o!=ScriptTestCase:
                            if len([x for x,y in zip(o.script.split("."),filter) if x==y or y is None])==3:
                                yield o
    
    def get_scripts(self,filter):
        for dirpath,dirnames,files in os.walk(os.path.join("sa","profiles")):
            parts=dirpath.split(os.sep)
            if parts[-1]!="tests":
                for f in [f for f in files if f.endswith(".py") and not f.startswith(".") and f!="__init__.py"]:
                    fp=os.path.join(dirpath,f)
                    m=__import__("noc."+fp[:-2].replace(os.sep,"."),{},{},"*")
                    if hasattr(m,"Script"):
                        name=m.Script.name
                        if len([x for x,y in zip(name.split("."),filter) if x==y or y is None])==3:
                            yield name
    
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
        filter=[None,None,None]
        if len(args)>0:
            filter=args[0].split(".")
            l=len(filter)
            if l>3:
                print "Invalid filter"
                sys.exit(1)
            if l<3:
                filter+=[None]*(3-l)
            filter=[(x if x!="*" else None) for x in filter]
        if options["untested"]:
            scripts=set(self.get_scripts(filter))
            tested=set([t.script for t in self.get_tests(filter)])
            lp=None
            for s in sorted(scripts-tested):
                v,o,s=s.split(".")
                p="%s.%s"%(v,o)
                if p!=lp:
                    print p
                    print "="*len(p)
                    lp=p
                print "    "+s
        else:
            self.display(self.get_tests(filter))
