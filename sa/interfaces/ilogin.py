# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from base import Interface, BooleanParameter


class ILogin(Interface):
    returns = BooleanParameter()

