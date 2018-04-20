# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various module loading utils
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import inspect


def load_subclasses(module, subclasses, exclude_tests=True):
    """
    Load all subclasses from
    :param module: Module name (noc.....)
    :param subclasses: class or list of classes
    :return: list of classes loaded
    """
    def _loader(path, subclasses):
        if not os.path.isfile(path):
            return []
        if exclude_tests and exclude in path:
            return []
        r = []
        mn = "noc." + path[:-3].replace(os.sep, ".")  # Full module name
        m = __import__(mn, {}, {}, "*")
        for on in dir(m):
            o = getattr(m, on)
            if inspect.isclass(o) and o.__module__.startswith(mn):
                for sc in subclasses:
                    if issubclass(o, sc):
                        r += [o]
        return r

    path = os.path.join(*module.split(".")[1:])
    exclude = "%stests%s" % (os.path.sep, os.path.sep)
    if type(subclasses) not in (list, tuple):
        subclasses = [subclasses]
    r = []
    if os.path.isdir(path):
        # Load directory
        for dirpath, dirnames, filenames in os.walk(path):
            if exclude_tests and exclude in dirpath + os.path.sep:
                continue
            for f in filenames:
                if f.endswith(".py"):
                    r += _loader(os.path.join(dirpath, f), subclasses)
    else:
        # Load file
        fp = path + ".py"
        if os.path.isfile(fp):
            r += _loader(fp, subclasses)
    return r


def load_name(base, name, base_cls):
    """
    Load a subclass of *base_cls* named *name* from *base* package
    """
    try:
        m = __import__("%s.%s" % (base, name), {}, {}, "*")
    except ImportError:
        return False
    for n, v in inspect.getmembers(m, inspect.isclass):
        if issubclass(v, base_cls) and v != base_cls:
            return v
    return None
