# ----------------------------------------------------------------------
# Alcatel.7324RU.get_config
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Alcatel.7324RU.get_config"
    interface = IGetConfig
