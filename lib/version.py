# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC components versions
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
##
## Return NOC version
##
def get_version():
    with open("VERSION") as f:
        return f.read().split("\n")[0].strip()
