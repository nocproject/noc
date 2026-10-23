#!./bin/python
# ----------------------------------------------------------------------
# Card service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import BaseService
from noc.config import config


class CardService(BaseService):
    name = "card"

    use_translation = True
    use_jinja = True
    use_mongo = True
    use_watchdog = config.watchdog.enable_watchdog
