# ---------------------------------------------------------------------
# IAuthenticationBackend interface
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import InstanceOfParameter


class IAuthenticationBackend(BaseInterface):
    returns = InstanceOfParameter("User", required=False)
