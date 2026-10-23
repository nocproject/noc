# ---------------------------------------------------------------------
# IHasLocalUser
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.core.interface.base import BaseInterface
from .base import StringParameter, BooleanParameter


class IHasLocalUser(BaseInterface):
    username = StringParameter()
    returns = BooleanParameter()
