#!/usr/bin/env python
#
# Service Activation Engine
#
import os,sys,getopt

if __name__ == '__main__':
    d=os.path.dirname(sys.argv[0])
    sys.path.insert(0,os.path.join(d,"..",".."))
    sys.path.insert(0,os.path.join(d,".."))
    sys.path.insert(0,d)
    from noc.sa.activator import Activator
    activator=Activator()
    activator.process_command()