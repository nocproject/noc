# ---------------------------------------------------------------------
# Discovery handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.defer import call_later

DELAY = config.correlator.discovery_delay


def schedule_discovery(event):
    """
    Reschedule discovery processes
    """
    event.managed_object.run_discovery(DELAY)


def schedule_discovery_config(event):
    """
    Reschedule discovery config processes
    """
    call_later(
        event.managed_object.id,
        job_class=event.managed_object.BOX_DISCOVERY_JOB,
        _checks=["config"],
        max_runs=1,
        delay=DELAY,
    )
