# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  GridVCS object revision
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2018 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple


Revision = namedtuple("Revision", ["id", "ts", "ft", "compress", "length"])
