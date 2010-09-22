#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Install canned session to proper location
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
import csv,os,re

rx_script=re.compile(r"^\s+script=\"(?P<script>.+?)\"",re.MULTILINE)
rx_q=re.compile(r"[^0-9a-zA-Z_]")

def install_can(path,platform,version):
    with open(path) as f:
        data=f.read()
    # Get script name
    match=rx_script.search(data)
    script=match.group("script")
    v,o,s=script.split(".")
    p=os.path.join("sa","profiles",v,o,"tests")
    if not os.path.exists(p):
        print "Creating directory %s"%p
        os.mkdir(p)
    init=os.path.join(p,"__init__.py")
    if not os.path.exists(init):
        print "Creating %s"%init
        with open(init,"w"):
            pass
    data=data.replace("platform='<<<INSERT YOUR PLATFORM HERE>>>'","platform='%s'"%platform)
    data=data.replace("version='<<<INSERT YOUR VERSION HERE>>>'","version='%s'"%version)
    mask=os.path.join(p,"%s_%s_%s_%s_%%04d.py"%(v,rx_q.sub("_",platform),rx_q.sub("_",version),s))
    i=1
    while True:
        oo=mask%i
        if not os.path.exists(oo):
            break
        i+=1
    print "Saving canned output into %s"%oo
    with open(oo,"w") as f:
        f.write(data)

def usage():
    print "USAGE:"
    print "%s -p <platform> -v <version> path1 .. pathN"%sys.argv[0]
    sys.exit(0)

if __name__=="__main__":
    import sys,getopt
    platform=None
    version=None
    optlist,optarg=getopt.getopt(sys.argv[1:],"p:v:")
    for k,v in optlist:
        if k=="-p":
            platform=v
        elif k=="-v":
            version=v
    if platform is None or version is None:
        usage()
    for p in optarg:
        install_can(p,platform,version)
