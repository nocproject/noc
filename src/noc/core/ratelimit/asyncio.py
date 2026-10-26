# ----------------------------------------------------------------------
# AsyncRateLimit
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from asyncio import sleep

from .base import BaseRateLimit


class AsyncRateLimit(BaseRateLimit):
    async def wait(self) -> None:
        """
        Wait when necessary to meet required rate
        :return:
        """
        t = self.get_sleep_timeout()
        if t:
            await sleep(t)
