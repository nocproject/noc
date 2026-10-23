# ----------------------------------------------------------------------
# SyncRateLimit
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from time import sleep

# NOC modules
from .base import BaseRateLimit


class SyncRateLimit(BaseRateLimit):
    def wait(self) -> None:
        """
        Wait when necessary to meet required rate
        :return:
        """
        t = self.get_sleep_timeout()
        if t:
            sleep(t)
