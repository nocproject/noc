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
    try:
        import settings
    except ImportError:
        sys.stderr.write("Error: Can't find file 'settings.py'. (If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n")
        sys.exit(1)
    os.environ['DJANGO_SETTINGS_MODULE']="noc.settings"
    from noc.sa.sae import SAE
    sae=SAE()
    sae.process_command()