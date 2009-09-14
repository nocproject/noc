# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.interfaces.base import *
import os,inspect,sys
# Interface autoloader
im=sys.modules["noc.sa.interfaces"]
for f in [f for f in os.listdir(__path__[0]) if f.endswith(".py") and f not in ["__init__.py","base.py"]]:
    m=__import__("noc.sa.interfaces."+f[:-3],{},{},"*")
    for cn in dir(m):
        c=getattr(m,cn)
        if inspect.isclass(c) and issubclass(c,Interface) and c!=Interface:
            setattr(im,c.__name__,c)
