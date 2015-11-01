# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Generic.Host
## Dummb profile to allow managed object creating
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Generic.Host"
