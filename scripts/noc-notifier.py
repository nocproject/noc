#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Abstract script interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import os,sys,site

if __name__ == '__main__':
    # Adjust paths
    d=os.path.dirname(sys.argv[0])
    contrib=os.path.join(d,"..","contrib","lib")
    sys.path.insert(0,contrib)
    sys.path.insert(0,os.path.join(d,"..",".."))
    sys.path.insert(0,os.path.join(d,".."))
    sys.path.insert(0,d)
    # Install eggs from contrib/lib
    site.addsitedir(contrib)
    try:
        import settings
    except ImportError:
        sys.stderr.write("Error: Can't find file 'settings.py'. (If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n")
        sys.exit(1)
    os.environ['DJANGO_SETTINGS_MODULE']="noc.settings"
    from noc.main.notifier import Notifier
    notifier=Notifier()
    notifier.process_command()