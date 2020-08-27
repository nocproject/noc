# ----------------------------------------------------------------------
#  Handler management utilities
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2020 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import cachetools

_CCACHE = {}  # handler -> object cache


@cachetools.cached(_CCACHE)
def get_handler(path):
    """
    Converts full path (i.e. "module.name" to python object)
    performing all necessary imports
    :param path:
    :returns: Python object referenced by path
    """
    if callable(path):
        return path
    try:
        mod_name, obj_name = path.rsplit(".", 1)
    except ValueError:
        raise ImportError("%s isn't valid handler name" % path)
    # Load module
    try:
        m = __import__(str(mod_name), {}, {}, [str(obj_name)])  # if unicode - TypeError
    except ImportError as e:
        raise ImportError("Cannot load handler '%s': %s" % (path, e))
    # Get attribute
    try:
        c = getattr(m, obj_name)
    except AttributeError as e:
        raise ImportError("Cannot get handler attribute '%s': %s" % (path, e))
    return c
