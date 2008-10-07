from noc.lib.registry import Registry

class HandlerRegistry(Registry):
    name="HandlerRegistry"
    subdir="handlers"
    classname="Handler"
handler_registry=HandlerRegistry()

class HandlerBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        handler_registry.register(m.name,m)
        return m

class Handler(object):
    __metaclass__=HandlerBase
    name=None
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