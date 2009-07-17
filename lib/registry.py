# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Abstract module loader/registry
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import os,logging
##
## Abstract module loader/registry
##
class Registry(object):
    name="Registry"
    subdir="directory"
    classname="Class"
    apps=None
    exclude=[] # List of excluded modules
    def __init__(self):
        self.classes={}
        self.is_registered=False
    
    #
    # Should be called within metaclass' __new__ method
    #
    def register(self,name,module):
        if name is None:
            return
        logging.info("%s: Register %s"%(self.name,name))
        self.classes[name]=module
    #
    # Should be called at the top of the models.py
    #
    def register_all(self):
        if self.is_registered:
            return
        if self.apps is None:
            from django.conf import settings
            apps=[a for a in settings.INSTALLED_APPS if a.startswith("noc.")]
        else:
            apps=self.apps
        for l in ["","local"]: # Look in the local/ directory too
            for app in apps:
                pd=os.path.join(l,app[4:],self.subdir)
                if not os.path.isdir(pd):
                    continue
                for dirpath,dirnames,filenames in os.walk(pd):
                    if l:
                        mb="noc.local.%s."%app[4:]+".".join(dirpath.split(os.sep)[2:])
                        # Create missed __init__.py for local/
                        c=dirpath.split(os.sep)
                        for i in range(1,len(c)+1):
                            i_path=os.path.join(os.sep.join(c[:i]),"__init__.py")
                            if not os.path.exists(i_path):
                                open(i_path,"w").close() # Create file
                    else:
                        mb=app+"."+".".join(dirpath.split(os.sep)[1:])
                    for f in [f for f in filenames if f.endswith(".py")]:
                        if f=="__init__.py":
                            f=""
                        else:
                            f="."+f[:-3]
                        if f in self.exclude:
                            continue
                        __import__(mb+f,{},{},self.classname)
        self.is_registered=True
    #
    #
    #
    def __getitem__(self,name):
        return self.classes[name]
    #
    # choices for Model's choices=
    #
    def _choices(self):
        return [(x,x) for x in sorted(self.classes.keys())]
    choices=property(_choices)
