# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Discovery handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.config import config

DELAY = config.correlator.discovery_delay


def schedule_discovery(event):
    """
    Reschedule discovery processes
    """
    event.managed_object.run_discovery(DELAY)
