# ---------------------------------------------------------------------
# IDBPreDelete
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface

from .base import Parameter, SubclassOfParameter


class IDBPreDelete(BaseInterface):
    model = SubclassOfParameter("Model")
    instance = Parameter()
