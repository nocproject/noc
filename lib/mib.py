# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIB lookup utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import logging
## NOC modules
from noc.lib.solutions import solutions_roots

logger = logging.getLogger(__name__)


class MIBRegistry(object):
    def __init__(self):
        self.mib = {}
        self.loaded_mibs = set()

    def __getitem__(self, item):
        if isinstance(item, basestring):
            return self.mib[item]
        else:
            return ".".join([self.mib[item[0]]] + [str(x) for x in item[1:]])

    def load_mibs(self):
        dirs = ["cmibs"]
        for r in solutions_roots():
            d = os.path.join(r, "cmibs")
            if os.path.isdir(d):
                dirs += [d]
        for root in dirs:
            logger.debug("Loading compiled MIBs from '%s'", root)
            for path, dirnames, filenames in os.walk(root):
                for f in filenames:
                    if not f.endswith(".py") or f == "__init__.py":
                        continue
                    fp = os.path.join(path, f)
                    mn = "noc.%s" % fp[:-3].replace(os.path.sep, ".")
                    m = __import__(mn, {}, {}, "*")
                    if hasattr(m, "NAME") and hasattr(m, "MIB"):
                        name = m.NAME
                        if name in self.loaded_mibs:
                            logger.debug("MIB is already loaded: %s, ignoring", name)
                            continue
                        self.loaded_mibs.add(name)
                        logger.debug("Loading MIB: %s", name)
                        self.mib.update(m.MIB)

logger.debug("Loading compiled MIBs")
mib = MIBRegistry()
mib.load_mibs()
