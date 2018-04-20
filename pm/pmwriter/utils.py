## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
try:
    import cPickle as pickle

    HAS_CPICKLE = True
except:
    import pickle

    HAS_CPICKLE = False


## Safe unpickler
if HAS_CPICKLE:
    class SafeUnpickler(object):
        PICKLE_SAFE = {
            "copy_reg": set(["_reconstructor"]),
            "__builtin__": set(["object"]),
        }

        @classmethod
        def find_class(cls, module, name):
            if not module in cls.PICKLE_SAFE:
                raise pickle.UnpicklingError(
                    "Attempting to unpickle unsafe module %s" % module)
            __import__(module)
            mod = sys.modules[module]
            if not name in cls.PICKLE_SAFE[module]:
                raise pickle.UnpicklingError(
                    "Attempting to unpickle unsafe class %s" % name)
            return getattr(mod, name)

        @classmethod
        def loads(cls, pickle_string):
            pickle_obj = pickle.Unpickler(StringIO(pickle_string))
            pickle_obj.find_global = cls.find_class
            return pickle_obj.load()
else:
    class SafeUnpickler(pickle.Unpickler):
        PICKLE_SAFE = {
            "copy_reg": set(["_reconstructor"]),
            "__builtin__": set(["object"]),
        }

        def find_class(self, module, name):
            if not module in self.PICKLE_SAFE:
                raise pickle.UnpicklingError(
                    "Attempting to unpickle unsafe module %s" % module)
            __import__(module)
            mod = sys.modules[module]
            if not name in self.PICKLE_SAFE[module]:
                raise pickle.UnpicklingError(
                    "Attempting to unpickle unsafe class %s" % name)
            return getattr(mod, name)

        @classmethod
        def loads(cls, pickle_string):
            return cls(StringIO(pickle_string)).load()


def get_unpickler(insecure=False):
    if insecure:
        return pickle
    else:
        return SafeUnpickler
