# ---------------------------------------------------------------------
# Audit handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.sa.models.interactionlog import InteractionLog, Interaction
from noc.config import config


def get_seconds(section, option):
    v = config.get(section, option)
    m = 1
    if v.endswith("h"):
        v = v[:-1]
        m = 3600
    elif v.endswith("d"):
        v = v[:-1]
        m = 24 * 3600
    elif v.endswith("w"):
        v = v[:-1]
        m = 7 * 24 * 3600
    elif v.endswith("m"):
        v = v[:-1]
        m = 30 * 24 * 3600
    elif v.endswith("y"):
        v = v[:-1]
        m = 365 * 24 * 3600
    try:
        v = int(v)
    except ValueError:
        raise "Invalid expiration option in %s:%s" % (section, option)
    return v * m


# Expiration settings
TTL_COMMAND = config.audit.command_ttl
TTL_LOGIN = config.audit.login_ttl
TTL_REBOOT = config.audit.reboot_ttl
TTL_CONFIG = config.audit.config_changed_ttl


def log_cmd(event, managed_object):
    """
    Log CLI command
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=TTL_COMMAND),
        object=managed_object.id,
        user=event.vars.get("user"),
        op=Interaction.OP_COMMAND,
        text=event.vars.get("command"),
    ).save()


def log_login(event, managed_object):
    """
    Log login event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=TTL_LOGIN),
        object=managed_object.id,
        user=event.vars.get("user"),
        op=Interaction.OP_LOGIN,
        text="User logged in",
    ).save()


def log_logout(event, managed_object):
    """
    Log logout event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=TTL_LOGIN),
        object=managed_object.id,
        user=event.vars.get("user"),
        op=Interaction.OP_LOGOUT,
        text="User logged out",
    ).save()


def log_reboot(event, managed_object):
    """
    Log reboot event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=TTL_REBOOT),
        object=managed_object.id,
        user=event.vars.get("user"),
        op=Interaction.OP_REBOOT,
        text="System rebooted",
    ).save()


def log_started(event, managed_object):
    """
    Log system started event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=TTL_REBOOT),
        object=managed_object.id,
        user=None,
        op=Interaction.OP_STARTED,
        text="System started",
    ).save()


def log_halted(event, managed_object):
    """
    Log system halted event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=TTL_REBOOT),
        object=managed_object.id,
        user=event.vars.get("user"),
        op=Interaction.OP_HALTED,
        text="System halted",
    ).save()


def log_config_changed(event, managed_object):
    """
    Log config changed event
    """
    InteractionLog(
        timestamp=event.timestamp,
        expire=event.timestamp + datetime.timedelta(seconds=TTL_CONFIG),
        object=managed_object.id,
        user=event.vars.get("user"),
        op=Interaction.OP_CONFIG_CHANGED,
        text="Config changed",
    ).save()
