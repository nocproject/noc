# ---------------------------------------------------------------------
# IGetHTTPGet
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import StringParameter


class IGetHTTPGet(BaseInterface):
    url = StringParameter()
    returns = StringParameter()
