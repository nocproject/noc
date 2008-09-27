import os

class BaseHandler(object):
    name="undefined"
    def __init__(self,object):
        self.object=object
    
    # Push latest version from repository to the equipment
    # Should be None when unsupported or
    # def push(self): otherwise
    push=None
    # Pull object into repository
    # Should be None when unsupported or
    # def pull(self): otherwise
    pull=None
    # Push latest version of all objects of given type
    # from repository to the equipment
    # Should be None when unsupported or
    # @classmethod
    # def global_pull(self): otherwise
    global_pull=None
    # Push latest version of all objects of given type
    # from repository to the equipment
    # Should be None when unsupported or
    # @classmethod
    # def global_push(self): otherwise
    global_push=None

#
# Global storage for registered profile classes
#
handler_classes={}
#
# Choices for CharField(choices=...)
#
handler_choices=[]
#
#
#
def get_handler_class(name):
    return handler_classes[name]

def register_handler_classes():
    for dirpath,dirnames,filenames in os.walk("cm/handlers/"):
        if dirpath.endswith("/"):
            dirpath=dirpath[:-1]
        for f in [f for f in filenames if f.endswith(".py") and f!="__init__.py"]:
            module=__import__("%s.%s"%(dirpath.replace("/","."),f.replace("/",".")[:-3]),globals(),locals,["Handler"])
            pc=getattr(module,"Handler")
            handler_classes[pc.name]=pc
    for p in handler_classes:
        handler_choices.append((p,p))
    handler_choices.sort(lambda x,y: cmp(x[0],y[0]))