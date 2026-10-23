# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.interface.base import BaseInterface
from .base import BooleanParameter, DictParameter, StringParameter


class ILogin(BaseInterface):
    returns = DictParameter(
        attrs={"result": BooleanParameter(), "message": StringParameter(default="")}
    )
