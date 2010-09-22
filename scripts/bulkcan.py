#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Bulk can output from CSV file
## USAGE:
## bulkcan <script> <csv>
## Accepts csv file of format:
## <host>,<platform>,<version>,scheme,user,pass,snmp community
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
import csv,os

def bulk_can(script,path):
    v,o,s=script.split(".")
    f=open(path)
    reader=csv.reader(f)
    for host,platform,version,scheme,user,passwd,snmp in reader:
        cmd=["python","manage.py","debug-script","-o","/tmp/canout"]
        if snmp:
            cmd+=["-c",snmp]
        cmd+=[script,"%s://%s:%s@%s/"%(scheme,user,passwd,host)]
        cmd=" ".join(cmd)
        print "Executing: %s"%cmd
        os.system(cmd)
        with open("/tmp/canout") as ff:
            data=ff.read()
        data=data.replace("platform='<<<INSERT YOUR PLATFORM HERE>>>'","platform='%s'"%platform)
        data=data.replace("version='<<<INSERT YOUR VERSION HERE>>>'","version='%s'"%version)
        mask=os.path.join("sa","profiles",v,o,"tests","%s_%s_%s_%s_%%04d.py"%(v,platform,version.replace(".","_"),s))
        i=1
        while True:
            oo=mask%i
            if not os.path.exists(oo):
                break
            i+=1
        print "Saving canned output into %s"%oo
        with open(oo,"w") as ff:
            ff.write(data)

if __name__=="__main__":
    import sys
    bulk_can(sys.argv[1],sys.argv[2])