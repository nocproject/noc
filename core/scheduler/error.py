# ----------------------------------------------------------------------
# Scheduler Exception classes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class RetryAfter(Exception):
    """
    Raise RetryAfter exception from job handler to reschedule
    execution after delay seconds
    """

    def __init__(self, msg, delay):
        super().__init__(msg)
        self.delay = delay
