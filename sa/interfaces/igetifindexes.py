# ---------------------------------------------------------------------
# IGetDict interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import DictParameter


class IGetIfindexes(BaseInterface):
    returns = DictParameter()
