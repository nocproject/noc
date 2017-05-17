# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raisecom.RCIOS.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Raisecom.RCIOS.get_capabilities"
