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
        self.choices=[]
        self.is_registered=False
    
    #
    # Should be called within metaclass' __new__ method
    #
    def register(self,name,module):
        if name is None:
            return
        if name in self.classes:
            raise Exception,"Module %s registred twice"%name
        logging.info("%s: Register %s"%(self.name,name))
        self.classes[name]=module
        self.choices.append((name,name))
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
        for app in apps:
            pd=os.path.join(app[4:],self.subdir)
            if not os.path.isdir(pd):
                continue
            for dirpath,dirnames,filenames in os.walk(pd):
                mb=app+"."+".".join(dirpath.split(os.sep)[1:])+"."
                for f in [f for f in filenames if f.endswith(".py") and f!="__init__.py"]:
                    f=f[:-3]
                    if f in self.exclude:
                        continue
                    __import__(mb+f,{},{},self.classname)
        self.is_registered=True
    #
    #
    #
    def __getitem__(self,name):
        return self.classes[name]
