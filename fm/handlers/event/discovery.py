# ---------------------------------------------------------------------
# Discovery handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.defer import call_later


def schedule_discovery(event):
    """
    Reschedule discovery processes
    """
    event.managed_object.run_discovery(config.correlator.discovery_delay)


def schedule_discovery_config(event):
    """
    Reschedule discovery config processes
    """
    call_later(
        event.managed_object.id,
        job_class=event.managed_object.BOX_DISCOVERY_JOB,
        _checks=["config"],
        max_runs=1,
        delay=config.correlator.discovery_delay,
    )


def on_system_start(event):
    """
    Called when reboot detected
    :param event:
    :return:
    """
    if event.managed_object.object_profile.box_discovery_on_system_start:
        event.managed_object.run_discovery(
            delta=event.managed_object.object_profile.box_discovery_system_start_delay
        )


def on_config_change(event):
    """
    Called when config change detected
    :param event:
    :return:
    """
    if event.managed_object.object_profile.box_discovery_on_config_changed:
        event.managed_object.run_discovery(
            delta=event.managed_object.object_profile.box_discovery_config_changed_delay
        )
