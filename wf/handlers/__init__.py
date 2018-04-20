# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## node handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import os
import inspect
## NOC modules
from base import BaseHandler

## Load
handlers = {}
im = sys.modules["noc.wf.handlers"]
for f in [f for f in os.listdir(__path__[0]) if
          not f.startswith(".") and f.endswith(".py") and f not in (
              "__init__.py", "base.py")]:
    m = __import__("noc.wf.handlers.%s" % f[:-3], {}, {}, "*")
    for cn in dir(m):
        c = getattr(m, cn)
        if inspect.isclass(c) and issubclass(c, BaseHandler) and c != BaseHandler:
            setattr(im, c.__name__, c)
            handlers[c.__name__[:-7]] = c
