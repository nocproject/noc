import os
from django.conf import settings

##
## Abstract module loader/registry
##
class Registry(object):
    name="Registry"
    subdir="directory"
    classname="Class"
    def __init__(self):
        self.classes={}
        self.choices=[]
    
    #
    # Should be called within metaclass' __new__ method
    #
    def register(self,name,module):
        if name is None:
            return
        if name in self.classes:
            raise Exception,"Module %s registred twice"%name
        print "%-20s: Register %s"%(self.name,name)
        self.classes[name]=module
        self.choices.append((name,name))
    #
    # Should be called at the top of the models.py
    #
    def register_all(self):
        for app in [a for a in settings.INSTALLED_APPS if a.startswith("noc.")]:
            pd=os.path.join(app[4:],self.subdir)
            if not os.path.isdir(pd):
                continue
            for dirpath,dirnames,filenames in os.walk(pd):
                mb=app+"."+".".join(dirpath.split(os.sep)[1:])+"."
                for f in [f for f in filenames if f.endswith(".py") and f!="__init__.py"]:
                    __import__(mb+f[:-3],{},{},self.classname)
    #
    #
    #
    def __getitem__(self,name):
        return self.classes[name]