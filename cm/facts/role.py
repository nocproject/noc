# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Performed role
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseFact


class Role(BaseFact):
    ATTRS = ["name"]
    ID = ["name"]

    def __init__(self, name):
        super(Role, self).__init__()
        self.name = name

    def __unicode__(self):
        return self.name
