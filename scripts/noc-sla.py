#!/usr/bin/env python
##----------------------------------------------------------------------
## SLA Monitor
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import os,sys,getopt

if __name__ == '__main__':
    d=os.path.dirname(sys.argv[0])
    sys.path.insert(0,os.path.join(d,"..",".."))
    sys.path.insert(0,os.path.join(d,".."))
    sys.path.insert(0,d)
    from noc.pm.sla import SLAMonitor
    sla=SLAMonitor()
    sla.process_command()
