# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IGetDict interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.core.interface.base import BaseInterface
from base import DictParameter


class IGetIfindexes(BaseInterface):
    returns = DictParameter()
