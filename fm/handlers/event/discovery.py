# ---------------------------------------------------------------------
# Discovery handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config

DELAY = config.correlator.discovery_delay


def schedule_discovery(event):
    """
    Reschedule discovery processes
    """
    event.managed_object.run_discovery(DELAY)
