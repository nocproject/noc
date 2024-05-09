# ---------------------------------------------------------------------
# Discovery handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.config import config
from noc.core.defer import call_later


def schedule_discovery(event, managed_object):
    """
    Reschedule discovery processes
    """
    managed_object.run_discovery(config.correlator.discovery_delay)


def schedule_discovery_config(event, managed_object):
    """
    Reschedule discovery config processes
    """
    if not managed_object:
        return
    call_later(
        managed_object.id,
        job_class=managed_object.BOX_DISCOVERY_JOB,
        _checks=["config"],
        max_runs=1,
        delay=config.correlator.discovery_delay,
    )


def on_system_start(event, managed_object):
    """
    Called when reboot detected
    :param event:
    :param managed_object:
    :return:
    """
    if managed_object.object_profile.box_discovery_on_system_start:
        managed_object.run_discovery(
            delta=managed_object.object_profile.box_discovery_system_start_delay
        )


def on_config_change(event, managed_object):
    """
    Called when config change detected
    :param event:
    :param managed_object:
    :return:
    """
    if managed_object.object_profile.box_discovery_on_config_changed:
        managed_object.run_discovery(
            delta=managed_object.object_profile.box_discovery_config_changed_delay
        )
