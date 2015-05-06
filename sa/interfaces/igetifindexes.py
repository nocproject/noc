# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IGetDict interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

from base import Interface, DictParameter


class IGetIfindexes(Interface):
    returns = DictParameter()
