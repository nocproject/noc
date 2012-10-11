# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## GridVCS object revision
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from collections import namedtuple


Revision = namedtuple("Revision", ["id", "ts", "ft"])
